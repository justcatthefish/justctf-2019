#!/usr/bin/env python

from copy import deepcopy
from itertools import combinations, izip_longest
from math import ceil, floor, log
from random import randint
from string import printable

from Crypto.Cipher import AES


# -------- misc utils
def recv_until(conn, data):
    received = ''
    while received != data:
        received += conn.recv(1)
    return received


def recv(conn, amount):
    received = ''
    while len(received) != amount:
        received += conn.recv(amount - len(received))
    return received


def send_line(conn, data):
    # print('sending "{}"'.format(data+'\n'))
    conn.send(data + '\n')


def send(conn, data):
    # print('sending "{}"'.format(data))
    conn.send(data)


def random_str(length):
    alphabet = printable[:-5]
    return ''.join([alphabet [randint(0, len(alphabet )-1)] for x in range(length)])


def xor(a, b):
    return ''.join(chr(ord(x)^ord(y)) for x,y in zip(a,b))


def i2b(number, size=0, endian='big', signed=False):
    if signed and number < 0:
            number += (1 << size)

    number_bytes = ''
    while number:
        number_bytes += chr(number & 0xff)
        number >>= 8

    number_bytes += '\x00'*(int(ceil(size/8.0))-len(number_bytes))

    if endian == 'big':
        return number_bytes[::-1]
    return number_bytes


def b2i(number_bytes, endian='big'):
    if endian == 'little':
        number_bytes = number_bytes[::-1]
    return int(number_bytes.encode('hex'), 16)


def deg(n):
    if type(n) == list:
        for d in reversed(xrange(len(n))):
            if n[d].to_int() != 0:
                return d
        return -1
    else:
        if n == 0:
            return -1
        return int(floor(log(n, 2) + 1))


# -------- Polynomials
class Polynomial_2():
    """Polynomial with coefs in GF(2)"""
    def __init__(self, coefficients):
        """x^3 + x + 1  == 0b1101 == [3, 1, 0]"""
        self.coefficients = Polynomial_2.convert_coefficients(coefficients)

    @staticmethod
    def convert_coefficients(coefficients):
        if type(coefficients) == list:
            coefficients = Polynomial_2.list_to_int(coefficients)
        elif type(coefficients) == str:
            # reverse bit order
            coefficients = int(''.join(map(lambda x: '{:08b}'.format(ord(x)), coefficients))[::-1], 2)
        elif type(int(coefficients)) in [int, long]:
            pass
        else:
            raise ValueError("Bad coefficients: {} ({})".format(coefficients, type(coefficients)))
        return coefficients


    @staticmethod
    def egcd(a, b):
        """Extended Euclidean algorithm"""
        a, b = map(Polynomial_2, [a, b])
        s0, t0, s1, t1 = map(Polynomial_2, [1, 0, 0, 1])
        while b.coefficients:
            q, a, b = a/b, b, a%b
            s0, s1 = s1, s0 - q*s1
            t0, t1 = t1, t0 - q*t1
        return a, s0, t0

    @staticmethod
    def list_to_int(coefficients):
        result = 0
        for coef in coefficients:
            result |= 1<<coef
        return result

    def __str__(self):
        return self.to_poly()

    def __getitem__(self, no):
        if type(no) not in [int, long]:
            return 'No must be a number'
        if no < 0 or no > self.to_bits():
            return 'Bad no'
        return int(self.to_bits()[no])

    def to_bits(self):
        return '{:b}'.format(self.coefficients)[::-1]

    def to_int(self):
        return self.coefficients

    def to_poly(self):
        if self.coefficients == 0:
            return '0'
        result = ''
        for i, coef in enumerate(self.to_bits()):
            if coef == '1':
                result = 'x^{} + '.format(i) + result
        return result[:-3]

    def to_list(self):
        return map(int, list(self.to_bits()))

    def __add__(self, other):
        return Polynomial_2(self.coefficients ^ other.coefficients)

    def __sub__(self, other):
        return self + other

    def __mul__(self, other):
        if type(other) in [int, long]:
            other = Polynomial_2(other)

        p = 0
        a = self.coefficients
        b = other.coefficients

        while a > 0:
            if a & 1:
                p = p ^ b
            a = a >> 1
            b = b << 1

        return Polynomial_2(p)


    def __rmul__(self, other):
        return self.__mul__(other)

    def __divmod__(self, other):
        a = self.coefficients
        b = other.coefficients
        q, r = 0, a

        while deg(r) >= deg(b):
            d = deg(r) - deg(b)
            q = q ^ (1 << d)
            r = r ^ (b << d)

        return Polynomial_2(q), Polynomial_2(r)

    def __mod__(self, other):
        return self.__divmod__(other)[1]

    def __div__(self, other):
        return self.__divmod__(other)[0]

    def __pow__(self, y):
        p = Polynomial_2(1)
        b = Polynomial_2(self.coefficients)

        while y > 0:
            if y & 1:
                p *= b
            y >>= 1
            b *= b
        return p

    def __eq__(self, other):
        return self.coefficients == other.coefficients

    def __hash__(self):
        return hash(self.to_int())


class Polynomial_2k():
    """Polynomial with coefs in GF(2) representing elements in GF(2^k)"""
    def __init__(self, coefficients, k, modulus):
        """x^3 + x + 1  == 0b1101"""
        self.coefficients = Polynomial_2.convert_coefficients(coefficients)
        self.k = k

        if isinstance(modulus, Polynomial_2):
            self.modulus = modulus
        else:
            self.modulus = Polynomial_2(modulus)

        tmp = Polynomial_2(self.coefficients) % self.modulus
        self.coefficients = tmp.coefficients


    def __str__(self):
        return self.to_poly()

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, no):
        if type(no) not in [int, long]:
            return 'No must be a number'
        if no > self.to_bits():
            return 'Bad no'
        return int(self.to_bits()[no])

    def to_bytes(self):
        return i2b(int(self.to_bits(), 2)).rjust(self.k//8, '\x00')

    def to_bits(self):
        return '{:b}'.format(self.coefficients).zfill(self.k)[::-1]

    def to_int(self):
        return self.coefficients

    def to_poly(self):
        if self.coefficients == 0:
            return '0'
        result = ''
        for i, coef in enumerate(self.to_bits()):
            if coef == '1':
                result = 'x^{} + '.format(i) + result
        return result[:-3]

    def to_list(self):
        return map(int, list(self.to_bits()))

    def __add__(self, other):
        return Polynomial_2k(self.coefficients ^ other.coefficients, self.k, self.modulus)

    def __sub__(self, other):
        return self + other

    def __mul__(self, other):
        if type(other) in [int, long]:
            other = Polynomial_2k(other, self.k, self.modulus)

        p = 0
        a = self.coefficients
        b = other.coefficients
        m = self.modulus.coefficients

        while a > 0:
            if a & 1:
                p = p ^ b
            a = a >> 1
            b = b << 1

            if deg(b) == deg(m):
                b = b ^ m

        return Polynomial_2k(p, self.k, self.modulus)

    def invmod(self):
        """Modular inverse. a*invmod(a) == 1 (mod n)"""
        d, s, t = Polynomial_2.egcd(self.coefficients, self.modulus.coefficients)
        if d.coefficients != 1:
            raise ValueError("Modular inverse doesn't exists ({}**(-1) % {})".format(self, self.modulus))
        return Polynomial_2k(s.coefficients, self.k, self.modulus)

    def __mod__(self, other):
        print 'Modulo not allowed'
        return None

    def __div__(self, other):
        return self * other.invmod()

    def __pow__(self, y):
        p = Polynomial_2k(1, self.k, self.modulus)
        b = Polynomial_2k(self.coefficients, self.k, self.modulus)

        while y > 0:
            if y & 1:
                p *= b
            y >>= 1
            b *= b
        return p

    def __eq__(self, other):
        return self.k == other.k and self.coefficients == other.coefficients

    def __hash__(self):
        return hash(self.to_bytes()+'-'+str(self.k))


# -------- Polynomial utils
class Polynomial_2k_generator():
    def __init__(self, k, modulus):
        self.k = k
        self.modulus = modulus

    def __call__(self, coefficients):
        return Polynomial_2k(coefficients, self.k, self.modulus)


aes_polynomial = Polynomial_2k_generator(128, [128, 7, 2, 1, 0])


def poly_to_vector(y):
    return vector(GF(2), y.to_list())


def vector_to_poly(v):
    poly = 0
    for vi in reversed(v):
        poly <<= 1
        poly += int(vi)
    return aes_polynomial(poly)


def aes_bytes_to_poly_blocks(ciphertext, additional, block_size=16):
    size_additional = len(additional)*8
    size_ciphertext = len(ciphertext)*8

    if len(ciphertext) % block_size != 0:
        ciphertext += '\x00' * (block_size - len(ciphertext)%block_size)
    if len(additional) % block_size != 0:
        additional += '\x00' * (block_size - len(additional)%block_size)
    
    blocks = []
    blocks.extend([additional[block_size*i:(block_size*i)+block_size] for i in xrange(len(additional)//block_size)])
    blocks.extend([ciphertext[block_size*i:(block_size*i)+block_size] for i in xrange(len(ciphertext)//block_size)])
    blocks.append(i2b(size_additional, size=(block_size//2)*8, endian='big') + i2b(size_ciphertext, size=(block_size//2)*8, endian='big'))
    blocks = map(aes_polynomial, blocks)
    return blocks


def poly_blocks_to_aes_bytes(blocks, block_size=16):
    blocks = map(lambda x: x.to_bytes(), blocks)
    sizes = blocks[-1]
    size_additional = b2i(sizes[:block_size//2], endian='big')
    size_ciphertext = b2i(sizes[block_size//2:], endian='big')
    size_additional_padded = size_additional//8
    if size_additional_padded % block_size != 0:
        size_additional_padded += 16 - size_additional_padded % block_size

    blocks = ''.join(blocks[:-1])
    additional = blocks[:size_additional//8]
    ciphertext = blocks[size_additional_padded:size_additional_padded + size_ciphertext//8]
    return ciphertext, additional


# -------- GCM
def encrypt_ctr(plaintext, key, nonce, block_size=16, initial_value=0):
    aes = AES.new(key, AES.MODE_ECB)
    key_stream = ''
    for counter in xrange(int(ceil(len(plaintext)/16.))):
        x = nonce + i2b(counter+initial_value, size=8*(block_size-len(nonce)), endian='big')
        key_stream += aes.encrypt(nonce + i2b(counter+initial_value, size=8*(block_size-len(nonce)), endian='big'))
    return xor(plaintext, key_stream)


def gcm_compute_parts(additional='', key=None, nonce=None, auth_key=None, s=None, plaintext='', ciphertext='', block_size=16):
    if nonce is not None and len(nonce) != 12:
        print 'nonce length must be 12'
        return None, None, None

    if nonce is None or key is None:
        if None in (ciphertext, s):
            print 'nonce can\'t be None if ciphertext, auth_key or s is None'
            return None, None, None

    blocks = []

    if auth_key is None:
        auth_key = AES.new(key, AES.MODE_ECB).encrypt('\x00'*block_size)
    h = aes_polynomial(auth_key)

    if ciphertext == '':
        ciphertext = encrypt_ctr(plaintext, key, nonce, block_size, 2)

    size_additional = len(additional)*8
    size_ciphertext = len(ciphertext)*8

    if len(additional) % block_size != 0:
        additional += '\x00'*(block_size - len(additional)%block_size)
    if len(ciphertext) % block_size != 0:
        ciphertext += '\x00'*(block_size - len(ciphertext)%block_size)

    blocks.extend([additional[block_size*i:(block_size*i)+block_size] for i in xrange(len(additional)//block_size)])
    blocks.extend([ciphertext[block_size*i:(block_size*i)+block_size] for i in xrange(len(ciphertext)//block_size)])

    blocks.append(i2b(size_additional, size=(block_size//2)*8, endian='big') + i2b(size_ciphertext, size=(block_size//2)*8, endian='big'))

    blocks = map(aes_polynomial, blocks)

    g = aes_polynomial(0)
    for b in blocks:
        g = g + b
        g = g * h

    if s is None:
        s = AES.new(key, AES.MODE_ECB).encrypt(nonce+i2b(1, size=4*8, endian='big'))
    s = aes_polynomial(s)

    t = g + s
    return blocks, t, s


def gcm_encrypt(plaintext, additional, key, nonce, tag_size=128, iv_counter=2, block_size=16):
    if len(nonce) != 12:
        print 'nonce length must be 12'
        return None, None

    ciphertext = encrypt_ctr(plaintext, key, nonce, block_size, 2)
    _, t, _ = gcm_compute_parts(ciphertext=ciphertext, additional=additional, key=key, nonce=nonce, block_size=16)

    return ciphertext, t.to_bytes()[:tag_size//8]


def gcm_verify(tag, ciphertext, additional, key, nonce, tag_size=16, block_size=16):
    _, t, _ = gcm_compute_parts(ciphertext=ciphertext, additional=additional, key=key, nonce=nonce, block_size=16)
    return t.to_bytes(), t.to_bytes()[:tag_size//8] == tag


# -------- tests
def test_polynomials():
    print "test polynomials"
    Pmod = Polynomial_2k_generator(128, [128,7,2,1,0])
    P = Pmod(0b10011010101100110100100110011101100110010111111000111011101000000110110100010101000101100100111100011001010100100110100111011000)
    Q = Pmod(0b01111010101010110111000011011100010011101111000001010000011000010000111010001111100001111010110001001000011101000011111110010101)
    print P.to_bits(), bin(P.to_int()), P
    print Q.to_bits(), bin(Q.to_int()), Q
    w = P*Q
    print w.to_bits(), bin(w.to_int()), w
    assert Q.coefficients == Pmod(Q.coefficients).coefficients
    assert Q.coefficients == Pmod(Q.to_int()).coefficients
    assert Q.coefficients == Pmod(Q.to_bytes()).coefficients
    print ''


def test_gcm():
    print "test gcm"
    plaintext = 'hn9YA(F BW&B (W&&W(RT&WEF f7*WB FTgsdc'
    additional = 'j gej8g0SRYH8s  8s9yf sgd78taDS* GASyd '
    key = 'xgrtjdh&LA28XNwh'
    nonce = 'a drO*1@((js'
    ciphertext, tag = gcm_encrypt(plaintext, additional, key, nonce)
    assert gcm_verify(tag, ciphertext, additional, key, nonce)

    blocks = aes_bytes_to_poly_blocks(ciphertext, additional)
    ciphertext2, additional2 = poly_blocks_to_aes_bytes(blocks)
    assert ciphertext == ciphertext2
    assert additional == additional2


if __name__ == "__main__":
    test_polynomials()
    test_gcm()
