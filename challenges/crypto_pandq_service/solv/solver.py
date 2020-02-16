#!/usr/bin/env python2

from pwn import *
from Crypto.Util import number
from Crypto import Random

def solve():
    
    p = b'justGiveTheFlag!!' + Random.get_random_bytes(14) + b'\x0f'
    p = number.bytes_to_long(p)

    while not number.isPrime(p) or not number.isPrime( (p-1)>>1 ) :
        p = b'justGiveTheFlag!!' + Random.get_random_bytes(14) + b'\x0f'
        p = number.bytes_to_long(p)

    return p, (p-1)>>1, hex(p).rstrip('L')

with remote(args.HOST or '127.0.0.1', int(args.PORT or 1337)) as nc:
    p,q,cipher = solve()

    nc.recvuntil('p: ')
    nc.sendline(str(p).lstrip('L'))
    nc.recvuntil('q: ')
    nc.sendline(str(q).lstrip('L'))
    nc.recvuntil('cipher: ')
    nc.sendline(str(cipher))
   
    nc.recvuntil('Result:\n')
    flag = nc.recvuntil('\n', drop=True)
    print(flag)
    sys.stdout.flush()

        
