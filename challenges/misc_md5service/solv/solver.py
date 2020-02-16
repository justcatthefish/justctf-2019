#!/usr/bin/env python2

from pwn import *

with remote(args.HOST or '127.0.0.1', int(args.PORT or 1337)) as p:
    p.recvuntil('Cmd: ')
    p.sendline('READ /0c8702194e16f006e61f45d5fa0cd511/flag_a6214417905b7d091f00ff59b51d5d78.txt')
    p.recvuntil("Executing READ on '/0c8702194e16f006e61f45d5fa0cd511/flag_a6214417905b7d091f00ff59b51d5d78.txt'\n")
    p.recvuntil('RESULT:\n')
    flag = p.recvuntil('\n', drop=True)
    if flag == 'justCTF{very_secret_file}':
        print(flag)
