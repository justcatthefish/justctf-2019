import os
import sys
from struct import *

flag="justCTF{1_ch4ng3d_my_m1nd_by_cl34r1n6_7h3_r00m}\x00"
sys.stderr.write("flag_len: " + str(len(flag)) + "\n")

def get_random_bytes(length):
  res = bytearray(os.urandom(length))
  for i in range(0, length):
    while res[i] == ord('"') or res[i] == ord("'"):
      res[i] = os.urandom(1)
  return res

memsize = 16384

mem = get_random_bytes(memsize)

#offsets to memory locations
o = {}
space = {}

mem_ptr = 0
def add_mem(key, value):
  global mem_ptr
  length = len(value)
  o[key] = mem_ptr
  space[key] = length
  for i in range(0, len(value)):
    mem[mem_ptr] = value[i]
    mem_ptr += 1

o["bytecode_start"] = 8192

with open("a.out", "rb") as f:
  a = bytearray(f.read())
  ctr = 0
  for x in a:
    mem[o["bytecode_start"]+ctr] = x
    ctr += 1

add_mem("greeter", "Hello!\nPlease provide your credentials!\n\x00")
add_mem("prompt", ">>\x00")
add_mem("pass_len_ok",   "Lets'check...\n\x00")
add_mem("pass_len_wrong","Wrong password :(\n\x00");

hardcoded1 = get_random_bytes(len(flag))
hardcoded1 += "\x00"
hardcoded2 = ""
for i in range(0, len(flag)):
  hardcoded2 += chr(hardcoded1[i] ^ ord(flag[i]) ^ i ^ mem[o["bytecode_start"]+i])
hardcoded2 += "\x00"

mem_ptr += 256
add_mem("hardcoded1", hardcoded1)
add_mem("Asled", "A"*96+"/bin/sh\x00")
add_mem("hardcoded2", hardcoded2)
add_mem("good_pw", "Good password. Congratulations!\n\x00")

with open('a.bin', 'wb') as f:
  f.write(mem)

hexdump=""
for i in range(0, len(mem)):
  hexdump += "\\x"
  hexdump += hex(mem[i])[2:]

c_src = "uint8_t memory["+str(memsize)+"] = \"" + hexdump + "\";"

for key, value in sorted(o.items(), key=lambda item: item[1]):
  if key in space:
    sys.stderr.write(key+" -> "+str(value)+"(len="+str(space[key])+")\n")
  else:
    sys.stderr.write(key+" -> "+str(value)+"(len=?)\n")

print c_src
