from functools import lru_cache
from Crypto.Util.number import bytes_to_long

@lru_cache(1024)
def factorial(n):
    return 1 if n == 0 else n * factorial(n-1)

PERM_SIZE = 37
def flag_to_perms(flag):
    assert len(flag) % 16 == 0, "Incorrect flag len"

    def int_to_perm(v):
        assert v < factorial(PERM_SIZE)
        tmp = []
        for x in range(PERM_SIZE-1, -1, -1):
            tmp += [ v // factorial(x) ]
            v = v % factorial(x)

        tmp = tmp[::-1]

        ret = []
        for i in range(PERM_SIZE):
            p = tmp[i]

            ret = ret[:p] + [i] + ret[p:]

        return ' '.join(map(str, ret))

    parts = [ flag[i*16:(i+1)*16].encode() for i in range(len(flag)//16) ]
    VALS = map(bytes_to_long, parts)

    return list(map(int_to_perm, VALS))

flag = input()
perms = flag_to_perms(flag)
print(*perms, sep='\n')
for i in range(len(flag)//16):
    with open("flag_perm_" + str(i+1) + ".in", "w") as f:
        f.write(perms[i])
