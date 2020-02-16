#!/usr/bin/env python
# -*- coding: utf-8 -*-

from numbers import Number
from random import randint
from binascii import hexlify


def random_str(length):
    alphabet = printable[:-5]
    return ''.join([alphabet [randint(0, len(alphabet )-1)] for x in range(length)])


def xor(*args, **kwargs):
    """Xor given values
    Args:
        args - bytes to be xored
        expand(bool) - don't expand bytes to size of the longest string if False
    Return:
        xored bytes
    """
    if 'expand' in kwargs and kwargs['expand'] is False:
        result = bytes(len(min(args, key=len)))
    else:
        max_size = len(max(args, key=len))
        result = bytes(max_size)

    for one in args:
        one = bytes(one)
        result = bytes([result[x] ^ one[x % len(one)] for x in range(len(result))])
    return result


def b2h(a, size=0):
    """Encode bytes to hex string"""
    return hexlify(a).decode()


def h2b(a):
    """Decode hex string to bytes"""
    a = a.strip()
    try:
        return bytes.fromhex(a)
    except (TypeError, ValueError):
        try:
            return bytes.fromhex(bytes(b'0')+a)
        except Exception as e:
            print(e, a)


def h2i(a):
    """Decode hex string to int"""
    return int(a, 16)


def i2h(a, size=0):
    """Encode int as hex string"""
    return hexlify(i2b(a, size=size)).decode()


def b2i(number_bytes, endian='big'):
    """Unpack bytes into int
    Args:
        number_bytes(bytes)
        endian(string): big/little
    Returns:
        int
    """
    if endian not in ['little', 'big']:
        log.critical_error("Bad endianness, must be big or little")

    if isinstance(number_bytes, Number):
        return int(number_bytes)

    if endian == 'little':
        number_bytes = number_bytes[::-1]
    return int(hexlify(number_bytes).decode(), 16)


def i2b(number, size=0, endian='big', signed=False):
    """Pack int to bytes
    Args:
        number(int)
        size(int): minimum size in bits, 0 if whatever it takes
        endian(string): big/little
        signed(bool): pack as two's complement if True (size must be given)
    Returns:
        bytes
    """
    if endian not in ['little', 'big']:
        log.critical_error("Bad endianness, must be big or little")

    if type(signed) != bool:
        log.critical_error("Bad sign, must be True or False")

    if size < 0:
        log.critical_error("Bad size, must be >= 0")

    if not size and signed:
        log.critical_error("Can't do signed packing without size")

    if number < 0 and not signed:
        log.critical_error("Negative number with signed==False")

    if not isinstance(number, Number):
        return number

    if signed and number < 0:
        number += (1 << size)

    number_bytes = bytes(b'')
    while number:
        number_bytes += bytes([number & 0xff])
        number >>= 8

    number_bytes += bytes(b'\x00'*(int(math.ceil(size/8.0))-len(number_bytes)))

    if endian == 'big':
        return number_bytes[::-1]
    return number_bytes
    return int(number_bytes.encode('hex'), 16)


def crt(a, n):
    """Solve chinese remainder theorem
    from: http://rosettacode.org/wiki/Chinese_remainder_theorem#Python
    The solution will be modulo product of modules
    Args:
        a(list): remainders
        n(list): modules
    Returns:
        int: solution to crt
    """
    if len(a) != len(n):
        log.critical_error("Different number of remainders({}) and modules({})".format(len(a), len(n)))

    prod = product(n)
    sum_crt = 0

    for n_i, a_i in zip(n, a):
        p = prod // n_i
        sum_crt += a_i * invert(p, n_i) * p
    return int(sum_crt % prod)
