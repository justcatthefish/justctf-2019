from public import *

def perms_to_flag(perms):
    def perm_to_int(perm):
        ret = 0
        for i in range(len(perm)):
            ret += factorial(perm[i]) * len( [None for x in perm[:i] if x < perm[i]] )

        return ret
    VALS = map(perm_to_int, perms)
    STRS = map(long_to_bytes, VALS)

    return b''.join(STRS)

ENCRYPTED = [
    list(map(int, '11 23 29 10 19 30 27 5 22 25 35 26 12 18 13 17 8 31 9 15 3 36 33 32 14 24 6 20 28 2 1 34 7 0 4 21 16'.split())),
    list(map(int, '31 12 5 13 10 6 27 24 17 23 30 32 20 14 26 3 29 7 19 2 1 35 34 0 8 21 18 9 16 28 4 25 11 36 33 22 15'.split())),
    list(map(int, '33 14 18 11 35 25 17 23 21 36 3 13 26 0 24 16 1 29 9 34 4 15 27 20 19 5 12 31 6 22 30 32 7 8 10 2 28'.split()))
]

PERMS = [
    list(map(int, '10 34 18 27 28 7 14 26 8 33 1 29 3 25 23 6 21 30 16 32 11 0 19 12 31 15 17 24 9 20 36 2 35 13 4 22 5'.split())),
    list(map(int, '9 10 33 26 13 31 34 3 20 16 14 24 28 30 32 35 5 25 21 15 12 1 2 29 4 11 6 22 8 36 27 18 19 0 17 7 23'.split())),
    list(map(int, '19 27 33 14 1 21 36 9 3 0 6 29 4 15 23 17 20 8 11 2 5 35 28 34 22 30 10 16 26 32 24 7 18 13 31 25 12'.split()))
]

def multiply(a, b):
    assert len(a) == len(b)
    for i in range(len(b)):
        assert (i in a) and (i in b)

    return [ a[b[i]] for i in range(len(b)) ]

def inverse_permutation(perm):
    for i in range(len(perm)):
        assert i in perm

    return [perm.index(i) for i in range(len(perm))]

if __name__ == "__main__":
    CLEAN = [ multiply(ENCRYPTED[i], inverse_permutation(PERMS[i])) for i in range(len(PERMS)) ]
    PARTS = perms_to_flag(CLEAN)
    print(PARTS)
    # WORKS :)
