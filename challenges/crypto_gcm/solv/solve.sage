#!/usr/bin/env sage

import sys
from socket import socket
from telnetlib import Telnet
from sys import exit
from binascii import hexlify
from Crypto.Cipher import AES
from string import printable
from repoze.lru import lru_cache
from utils import (aes_polynomial,
                    gcm_encrypt, gcm_verify,
                    poly_blocks_to_aes_bytes, aes_bytes_to_poly_blocks,
                    poly_to_vector, vector_to_poly,
                    random_str, recv, recv_until, send, send_line)

hostname, port = sys.argv[1].split('HOST=')[1], int(sys.argv[2].split('PORT=')[1])

MAX_TEXT_SIZE = 262144
IV_LEN = 12
TAG_SIZE = 2
KEY_SIZE = 16
BLOCK_SIZE = 16
MAX_OPERATIONS = 1337


def print_log(data):
    print(data)


# ----------------- remote gcm
def encrypt_remote(conn, plaintext):
    assert len(plaintext) <= MAX_TEXT_SIZE

    additional = ''

    recv_until(conn, 'operation: ')
    send(conn, 'e')
    recv_until(conn, 'plaintext size: ')
    send_line(conn, str(len(plaintext)))
    recv_until(conn, 'plaintext: ')
    send(conn, plaintext)

    iv = recv(conn, IV_LEN)
    tag = recv(conn, TAG_SIZE)
    ciphertext = recv(conn, len(plaintext))

    return ciphertext, additional, tag, iv


def verify_remote(conn, ciphertext, additional, tag, iv):
    recv_until(conn, 'operation: ')
    send(conn, 'v')
    recv_until(conn, 'ciphertext size: ')
    send_line(conn, str(len(ciphertext)))
    recv_until(conn, 'ciphertext: ')
    send(conn, ciphertext)
    recv_until(conn, 'tag: ')
    send(conn, tag)
    recv_until(conn, 'iv: ')
    send(conn, iv)

    result = recv(conn, 1)
    if result == 'O':
        recv(conn, 2)
        return True
    else:
        recv(conn, 4)
        return False


# ----------------- local gcm
def encrypt_local(conn, plaintext):
    assert len(plaintext) <= MAX_TEXT_SIZE
    additional = ''
    key = 'a'*KEY_SIZE
    iv = random_str(IV_LEN)
    ciphertext, tag =  gcm_encrypt(plaintext, additional, key, iv, tag_size=TAG_SIZE*8)
    return ciphertext, additional, tag, iv


def verify_local(conn, ciphertext, additional, tag, iv):
    key = 'a'*KEY_SIZE
    return gcm_verify(tag, ciphertext, additional, key, iv, tag_size=TAG_SIZE*8)[1]



@lru_cache(1000)
def create_multiply_matrix(c):
    columns = []
    i = 1
    while i < 2**128:
        x = aes_polynomial(i)
        column = (c*x).to_list()
        columns.append(column)
        i <<= 1

    return matrix(GF(2), columns).transpose()


@lru_cache(1000)
def create_square_matrix():
    columns = []
    i = 1
    while i < 2**128:
        x = aes_polynomial(i)
        column = (x**2).to_list()
        columns.append(column)
        i <<= 1
    return matrix(GF(2), columns).transpose()


@lru_cache(1000)
def precompute_square_matrices(no):
    Ms = create_square_matrix()
    matrices = [create_square_matrix()]
    for _ in xrange(1, no):
        matrices.append(matrices[-1]*Ms)
    return matrices


def create_Ad(c, cp, Msi_all=None):
    # assume c consists only blocks di == c(2^i)
    if len(c) != len(cp):
        print 'Wrong lengths'
        return None

    if Msi_all is None:
        Msi_all = precompute_square_matrices(len(c))

    Ad = matrix.zero(GF(2), 128, 128)
    for i in xrange(len(c)):
        di = c[i] - cp[i]
        Mdi = create_multiply_matrix(di)
        Ad += Mdi * Msi_all[i]
    return Ad


def flip_bit(poly, no):
    r = aes_polynomial(poly.to_int() ^^ (1<<no))
    return r


def create_T(d, X, tag_size, max_tag_bits_zeroed=None):
    # assume c consists only blocks di == c(2^i)
    n = len(d)
    columns = []
    Msi_all = precompute_square_matrices(n)

    AdX_columns = X.dimensions()[1]
    AdX_rows_zero_max = (128*n - ((128*n) % AdX_columns)) // AdX_columns
    AdX_rows_zero = min(tag_size-1, AdX_rows_zero_max)  # left at least one row non-zero

    if (128*n)-(AdX_rows_zero*AdX_columns) == 0:  # left some bits to play with
        AdX_rows_zero -= 1

    if max_tag_bits_zeroed is not None:
        AdX_rows_zero = min(max_tag_bits_zeroed, AdX_rows_zero)

    print_log("Ad*X will have {} columns".format(AdX_columns))
    print_log("We can zero out {} bits, {} rows ({} left)".format(128*n, AdX_rows_zero_max, tag_size-AdX_rows_zero_max))
    print_log("Will zero out {} bits ({} left), {} rows ({} left)".format(AdX_rows_zero*AdX_columns, (128*n)-(AdX_rows_zero*AdX_columns), AdX_rows_zero, tag_size-AdX_rows_zero))
    print_log("Probability of forgery is 2^(-{})".format(tag_size-AdX_rows_zero))
    print_log("Generating T matrix")

    for i in xrange(n):
        print_log("  {}/{}".format(i, n-1))
        for no in xrange(128):
            # dp = d[:i] + [flip_bit(d[i], no)] + d[i+1:]
            # Ad = create_Ad(d, dp, Msi_all)
            Mdi = create_multiply_matrix(flip_bit(d[i], no) - d[i])
            Ad = Mdi * Msi_all[i]
            AdX = Ad*X
            columns.append(AdX.list()[:AdX_rows_zero*AdX_columns])
    T = matrix(GF(2), columns).transpose()
    return T


def remove_lineary_dependend_vectors(A):
    A = A.echelon_form()
    for i, v in enumerate(A):
        if v.is_zero():
            A = A.delete_rows(range(i, A.dimensions()[0]))
            break
    return A


# ----------------- attack
def recover_h(conn, tag_size):
    K = matrix(GF(2))
    X = matrix.identity(GF(2), 128)
    V = GF(2)**128

    enc_counter = 0
    verify_counter = 0

    while K.dimensions()[0] - len(V.linear_dependence(K)) < 127:
        if enc_counter + verify_counter >= MAX_OPERATIONS:
            print('Hit operations limit')
            exit(1)

        plaintext = random_str(BLOCK_SIZE * (2**randint(9, 14)))
        enc_counter += 1
        ciphertext, additional, tag, iv = encrypt_remote(conn, plaintext)
        c = aes_bytes_to_poly_blocks(ciphertext, additional)[::-1]  # first block should be the one encoding length
        # tag = s + c1*h + c2*h^2 + c3*h^3 + ... + cn*h^n

        # get only di == c(2^i) and skip c0
        d = [c[(2**i) - 1] for i in xrange(int(floor(log(len(c),2))+1))][1:]

        print_log("K:")
        print_log(K.__repr__())
        print_log("K have {} vectors, {} are lineary indepentend".format(K.dimensions()[0], K.dimensions()[0]-len(V.linear_dependence(K))))
        print_log(K.str().replace(' ', ''))
        print_log('')

        print_log("X:")
        print_log(X.__repr__())
        print_log("")

        T = create_T(d, X, tag_size, max_tag_bits_zeroed=tag_size-3)
        print_log("T:")
        print_log(T.__repr__())

        NT = T.right_kernel().basis_matrix()
        print_log("NT:")
        print_log(NT.__repr__())
        for no, v in enumerate(NT):
            v = ''.join(map(str,v))
            v = map(aes_polynomial, [int(v[j*128:(j+1)*128][::-1],2) for j in xrange(len(v)//128)])

            faked_c = [c[0]]
            for i in xrange(1, len(c)):
                if (i+1) & i == 0:  # 2^i
                    faked_c.append(c[i]+v[int(log(i,2))])
                else:
                    faked_c.append(c[i])

            if enc_counter + verify_counter >= MAX_OPERATIONS:
                print('Hit operations limit')
                exit(1)

            # probability of forging MAC is 2^(-tag_size+len(d)-1)
            verify_counter += 1
            ciphertext, additional = poly_blocks_to_aes_bytes(faked_c[::-1])
            verified = verify_remote(conn, ciphertext, additional, tag, iv)
            print_log('test no: {}'.format(no))

            if verified:
                print_log('found')
                test_c, test_faked_c = [], []
                for i in xrange(1, len(c)):
                    if (i+1) & i == 0:  # 2^i
                        test_faked_c.append(c[i]+v[int(log(i,2))])
                        test_c.append(c[i])

                Ad = create_Ad(test_c, test_faked_c)  # Ad should have first len(d)-1 rows == 0
                print_log("Ad:")
                print_log(Ad[:tag_size].str().replace(' ' ,''))
                print_log("")
                K_new = Ad[:tag_size]  # K*h == 0

                if K.dimensions() == (0, 0):
                    K = K_new
                else:
                    K = block_matrix(GF(2), 2, 1, [K, K_new])
                K = remove_lineary_dependend_vectors(K)

                X = K.right_kernel().basis_matrix().transpose()
                break

        print_log('-'*10)

    NK = K.right_kernel().basis_matrix()
    h_recovered = vector_to_poly(NK[0])

    print_log("h found:")
    print_log(NK.__repr__())
    print_log(NK.str().replace(' ', ''))
    print_log(h_recovered.to_int())
    print_log(hexlify(h_recovered.to_bytes()))

    print_log('enc_counter: {}'.format(enc_counter))
    print_log('verify_counter: {}'.format(verify_counter))

    return h_recovered.to_bytes()


if __name__ == "__main__":
    CONN = (hostname, port)
    conn = socket()
    conn.connect(CONN)

    h = recover_h(conn, TAG_SIZE*8)
    assert len(h) == BLOCK_SIZE

    recv_until(conn, 'operation: ')
    send(conn, 'q')
    recv_until(conn, 'authentication key: ')
    send(conn, h)

    data_all = ''
    while True:
        data = conn.recv(1)
        data_all += data
        if data == '}':
            break
    print(data_all)

    conn.close()
