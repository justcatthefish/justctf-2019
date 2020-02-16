from pwn import *

from random import randint
from gmpy2 import gcd, lcm, invert

def solve_k(x, a, m):
    if x == 0:
        return 0

    g = gcd(x, m)

    ap = a//g
    xp = x//g
    mp = m//g

    return (ap*invert(xp, mp))%mp

def solve(p, q, e, dm, m):
    # Solutions step
    c_lambda = lcm(p-1, q-1)

    # Smallest solution
    d_min = invert(e, c_lambda)

    # Residue; k * lambda = a mod m
    a = (dm - d_min)%m

    k = solve_k(c_lambda%m, a, m)

    return ( d_min + c_lambda * k ) #% ( (p-1) * (q - 1) )


with remote(args.HOST, args.PORT) as io:
    for _ in range(250):
        io.recvuntil('/250\n')
        p, q, e, dm, m = map(int, io.recvuntil('\n', drop=True).split())

        io.sendline(str(solve(p, q, e, dm, m)))

    #flag = input()
    io.interactive()
