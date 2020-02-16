#!/usr/bin/env python
# -*- coding: utf-8 -*-

import signal
import sys
import hashcash
import os
import string
from random import randint, choice
from ec import EC_w
from sys import exit
from hashlib import sha512
from binascii import hexlify
from secret import FLAG, key

def rand_string(length=10):
    return ''.join(choice(string.ascii_letters) for i in range(length))

def handler(signum, frame):
    print('Time limit exceeded. Good bye!')
    sys.stdout.flush()
    sys.exit(1)

signal.signal(signal.SIGALRM, handler)
signal.alarm(175)

print('Please use the following command to solve the Proof of Work:')
print('hashcash -mb25', rand_string(8))

proof_of_work = input('proof of work:')

if not hashcash.validate(25, proof_of_work):
    print('Provided stamp was not valid!')
    os.exit(1)

def xor(a, b):
    return b''.join([bytes([x^y]) for x,y in zip(a,b)])


def fault(Q):
    x = Q.x ^ (1<<randint(0,3))
    return Q.curve.point(x, Q.y)


def mul(d, P):
    counter = 0
    fault_at = randint(0, d.bit_length()-1)
    H = P
    Q = P.curve.Identity()
    while d > 0:
        if d & 1:
            Q += H
        H += H
        d >>=  1
        if fault_at == counter:
            Q = fault(Q)
        counter += 1
    return Q, fault_at


def run():
    p = 115792089210356248762697446949407573530086143415290314195533631308867097853951
    a = -3
    b = 41058363725152142129326129780047268409114441015993725554835256314039467401291
    curve = EC_w(p, a, b)
    curve.order = 115792089210356248762697446949407573529996955224135760342422259061068512044369

    # d = randint(2, curve.order-1)
    d = key
    flag_enc = hexlify(xor(FLAG, sha512(d.to_bytes(32, 'big')).digest()))
    print(flag_enc.decode())

    x = int(input('gimme x: ')) % curve.p
    y = int(input('gimme y: ')) % curve.p

    P = curve.point(x, y)
    if not P.is_correct():
        print('Your point is not on the curve')
        exit(1)

    print(d.bit_length())
    print(d*P)
    for i in range(2000):
        Q, fault_at = mul(d, P)
        print(Q)
        print(fault_at)


if __name__ == '__main__':
    print("Welcome to our cryptoservice!")
    run()
