#!/usr/bin/env python
# -*- coding: utf-8 -*-


from pwn import *
from collections import defaultdict
from ec import *
from hashlib import sha512
from binascii import unhexlify, hexlify
import sys

hostname, port = args['HOST'] or 'localhost', int(args['PORT'] or 1337)


def solve_hashcat(p):
    p.recvuntil(b'Please use the following command to solve the Proof of Work:\n')
    hashcat = p.recvuntil('\n', drop=True)
    out = subprocess.check_output(hashcat, shell=True)
    p.send(out)
    p.recvuntil('proof of work:')


def get_data(P, data):
    conn = remote(hostname, port)
    solve_hashcat(conn)

    conn.recvuntil(b'Welcome to our cryptoservice!\n')
    flag_enc = unhexlify(conn.recvline().strip())

    conn.sendline(str(P.x))
    conn.recvuntil('gimme x: ')
    conn.sendline(str(P.y))
    conn.recvuntil('gimme y: ')

    n = int(conn.recvline().strip())
    Q_n = conn.recvline().strip().replace(b'(',b'').replace(b')',b'').split(b',')
    Q_n = P.curve.point(int(Q_n[0]), int(Q_n[1]))

    for i in range(2000):
        Q_n_d = conn.recvline().strip().replace(b'(',b'').replace(b')',b'').split(b',')
        Q_n_d = P.curve.point(int(Q_n_d[0]), int(Q_n_d[1]))
        fault_at = int(conn.recvline().strip())
        data[fault_at].append(Q_n_d)

    conn.close()
    return flag_enc, n, Q_n, data


def brute_bits(Q_n, P, n, d_found, d_found_bits):
    """
        n - d bit length
        Q_n = d*P
    """
    missing_bits = n - d_found_bits
    d_found <<= missing_bits
    for x in range(0, 2**missing_bits):
        d_to_check = d_found + x
        if Q_n == d_to_check*P:
            print('found d: {}'.format(hex(d_to_check)))
            return d_to_check
    return None


def one_run_test(Q_n, P, n, m, d_found, d_found_bits, data):
    want_fault_at = n - m + 1
    shuffle(data[want_fault_at])
    Q_n_d = data[want_fault_at][0]

    i = n - m  # such that d_i = 1 and fault at iteration idx >= i
    while i + d_found_bits < n:
        # x = {0,1}^n-i, msb of d
        for x in range(1, 2**(n - i - d_found_bits), 2):
            x = d_found * (2**(n - i - d_found_bits)) + x
            xx = x * (2**i)
            Qx_i = Q_n - xx*P
            # print('{:0{width}b}'.format(xx, width=n))

            if Qx_i == Identity(Qx_i.curve):
                print('found whole d: {}'.format(hex(xx)))
                return xx, xx.bit_length()

            for y in range(4):
                Qx_i_d = Qx_i.curve.point(Qx_i.x ^ (1<<y), Qx_i.y)
                Qx_n_d = Qx_i_d

                x2 = x
                for ii in range(i, n):
                    if x2 & 1:
                        Qx_n_d += (2**ii)*P
                    x2 >>= 1

                if Qx_n_d == Q_n_d:
                    print('found:')
                    print('    d upper {} bits'.format(n-i))
                    print('    x: {:b}'.format(xx))
                    print('    f: {}'.format(n - want_fault_at))

                    d_part_found = True
                    d_found = x
                    d_found_bits = n-i

                    return d_found, d_found_bits
        i += 1
    return None


def solve(P):
    is_all_data = False
    data = defaultdict(list)
    while not is_all_data:
        flag_enc, n, Q_n, data = get_data(P, data)
        if len(data.keys()) == n:
            is_all_data = True

    print('n = {}'.format(n))

    m_start = 6  # trade-off param
    d = 0
    d_found_bits = 0

    m = m_start + d_found_bits
    count_failed_tries = 0
    while d_found_bits + m_start < n:
        print('testing with window len = {}'.format(m - d_found_bits))
        result = one_run_test(Q_n, P, n, m, d, d_found_bits, data)
        if result is None:
            count_failed_tries += 1
            if count_failed_tries > m - d_found_bits:
                m = min(n, m+1)
                count_failed_tries = 0
        else:
            d, d_found_bits = result
            m = m_start + d_found_bits

    d = brute_bits(Q_n, P, n, d, d_found_bits)

    if Q_n != d*P:
        print('Something is wrong with d')

    print(hexlify(flag_enc))
    print(xor(flag_enc, sha512(d.to_bytes(32, 'big')).digest()))
    return d


if __name__ == "__main__":
    p = 115792089210356248762697446949407573530086143415290314195533631308867097853951
    a = -3
    b = 41058363725152142129326129780047268409114441015993725554835256314039467401291
    curve = EC_w(p, a, b)
    curve.order = 115792089210356248762697446949407573529996955224135760342422259061068512044369

    x = 64019174494556640138491251983533938958975666785987328871067474809270492241311
    y = 84214221971505716467197298374958396985392314823346645555985859332634827941119
    P = curve.point(x, y)

    solve(P)
