#!/usr/bin/env python2

from z3 import *
import random
import sys


def solve(info, T, N, first_char='', last_char='', hints=[]):
    TT = T-1

    info = map(lambda x: tuple(x), info)

    # remove duplicates
    info = list(dict.fromkeys(info))

    # convert to integers
    info = list(map(lambda x: list(map(lambda y: ord(y), x)), info))

    # define symbolic variables
    chars = [ Int('x_%s' % i) for i in range((N-TT)*T)]

    # solution chars
    real_chars = []
   
    # add real chars
    for i in range(0, len(chars), T):
        real_chars.append(chars[i])

    # add real chars suffixs
    for i in range(TT):
        real_chars.append(chars[-TT+i])
        
    s = Solver()

    if first_char:
        s.add(real_chars[0] == ord(first_char))
    if last_char:
        s.add(real_chars[-1] == ord(last_char))
    
    
    # sequence constraints x1==x3 ^ x2==x4 ^ x4 == x6 ^ x5 == x7 ^ 
    for i in range(1,len(chars)-TT,T):
        for d in range(TT):
            s.add(chars[i+d] == chars[i+d+TT])

    # add hints
    for hint in hints:
        l = len(hint)
        x = []
        for i in range(len(real_chars)-l+1):
            x.append(And([real_chars[i+d] == ord(hint[d]) for d in range(l)]))
        s.add(Or(x))

    # all pairs (x0,x1,x2),(x3,x4,x5)... are in info
    for i in range(0,len(chars),T):
        x = []
        for j in info:
            x.append(And([chars[i+d] == j[d] for d in range(T)]))
        s.add(Or(x))

    # each pair from info has been used at least once
    for j in info:
        x = []
        for i in range(0,len(chars),T):
            x.append(And([chars[i+d] == j[d] for d in range(T)]))
        s.add(Or(x))


    solutions = []
    while s.check() == sat:
        m = s.model()
        solutions.append(''.join(list(map(lambda x: chr(m.evaluate(x).as_long()), real_chars))))
        s.add(Or([x != m[x] for x in chars]))
    return solutions


if __name__ == '__main__':
    if len(sys.argv) != 4 or sys.argv[1] not in ['array', 'secret']:
        print('python %s array "aaa,vvv,zzz" 32' % sys.argv[0])
        print('python %s secret "907e5f274c6d6117040d65739df1ab5a" 3' % sys.argv[0])
        sys.exit(0)
    if sys.argv[1] == 'array':
        info = list(map(lambda x: tuple(x.strip()), sys.argv[2].strip().split(',')))
        t = len(info[0])
        n = int(sys.argv[3])
    if sys.argv[1] == 'secret':
        secret = sys.argv[2].strip()
        t = int(sys.argv[3])
        n = len(secret)
        info = zip(*[secret[i:] for i in range(t)])
        random.shuffle(info)
        
    print(info)
    s = solve(info, t, n)
    print(len(s), s[0])