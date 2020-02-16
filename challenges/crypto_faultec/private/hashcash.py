
"""
Module to generate and validate HashCash stamps.

"""

__author__ = 'prussell'

from hashlib import sha1
from datetime import datetime
from random import randint
from math import ceil

rand_chars = ([chr(x) for x in range(ord('a'), ord('z'))] +
              [chr(x) for x in range(ord('A'), ord('Z'))] +
              [chr(x) for x in range(ord('0'), ord('9'))] +
              ['+', '-', '/'])


char_map = {'0' : '0000',
            '1' : '0001',
            '2' : '0010',
            '3' : '0011',
            '4' : '0100',
            '5' : '0101',
            '6' : '0110',
            '7' : '0111',
            '8' : '1000',
            '9' : '1001',
            'a' : '1010',
            'b' : '1011',
            'c' : '1100',
            'd' : '1101',
            'e' : '1110',
            'f' : '1111'}


rc_len = len(rand_chars)

min_bits = 0
# Max number of bits for SHA-1 stamps
max_bits = 160
default_bits = 15

def is_valid(stamp : str) -> bool:
    return validate(int(stamp.split(':')[1]), stamp)

def validate(nbits : int, stamp : str, encoding : str ='utf-8') -> bool:
    if nbits < min_bits or nbits > max_bits:
        raise ValueError("Param 'nbits' must be in range [0, 160), but is {}".format(nbits))

    i = 0
    total = 0
    N = int(nbits/8)
    hashed = sha1(stamp.encode(encoding)).digest()

    while i < N:
        total |= hashed[i]
        i += 1

    remainder = nbits % 8
    if remainder != 0:
        total |= hashed[i] >> (8 - remainder)

    return total == 0

def generate(nbits : int, resource : str, encoding : str ='utf-8') -> str:
    # ver:bits:date:resource:[ext]:rand:counter
    ver = 1
    bits = nbits
    date_str = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    ext = ''
    rand = ''.join(rand_chars[randint(0, rc_len-1)] for x in range(0, 10))
    counter = 0

    result = None
    while result is None:
        stamp = ":".join(str(elem) for elem in [ver, bits, date_str, resource, ext, rand, counter])

        if validate(nbits, stamp, encoding=encoding):
            result = stamp
            break

        counter += 1

    return result


if __name__ == "__main__":
    
    from argparse import ArgumentParser
    parser = ArgumentParser()

    parser.add_argument("NBITS", type=int, default=default_bits, help="Number of leading zeroes in a stamp", choices=range(max_bits+1))
    parser.add_argument("RESOURCE", help="The resource string to use in the stamp. Ex: email address, ip address, etc")
    parser.add_argument('-v', '--validate', action='store_true', help="Validate RESOURCE as a HashCash stamp")
    
    args = parser.parse_args()

    func = generate

    if args.validate:
        func = validate
    
    print(func(args.NBITS, args.RESOURCE))
