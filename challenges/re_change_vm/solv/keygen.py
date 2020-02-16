"""
To solve:

1) extract program memory to dump.bin
- launch binary `./change_my_vm &`
- get a gdb session in it `pidof change_my_mind` -> `sudo gdb` -> `attach <pid>`
- in gdb see `proc info mappings` or `vmmap` in pwndbg
- dump memory via:
```
pwndbg> dump memory dump.bin 0x5619fd88e000+0x4080 0x5619fd897000
```
where the first and last address are start address of first binary memory page and end address of last binary memory page
the 0x4080 is offset where program decrypts its logic, so this offset needs to be hardcoded

2) This will create `dump.bin` that we pass to this keygen (`python keygen.py dump.bin`). Jobs done!

---

another option is to just extract key1, key2 and src
"""


import sys

if len(sys.argv) != 2:
    print "./keygen dump.bin"
    sys.exit(0)

with open(sys.argv[1], "rb") as f:
  a = bytearray(f.read())

key1 = a[334:334+49]  #hardcoded part1
key2 = a[487:487+49]  #hardcoded part2
src = a[8192:8192+48] #address of binary image

flag = ""
for i in range(0, 48):
    c = key1[i] ^ key2[i] ^ src[i] ^ i
    flag += chr(c)
print flag
