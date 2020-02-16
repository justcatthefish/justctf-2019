import hashlib


'''
flag: jctf{m4y_th3_synths_b3_w17h_y0u}

hash: [0,3]  = 714d32d45f6cb3bc336a765119cb3c4c 81|81|81|
hash: [3,3]  = 51a96b38445ff534e3cf14c23e9c977f 77|84|81|
hash: [6,3]  = 51a96b38445ff534e3cf14c23e9c977f 77|84|81|
hash: [9,3]  = bc9189406be84ec297464a514221406d 88|88|88|
hash: [12,3] = 4ec6aa45006dae153d94abd86b764e17 89|84|80|
hash: [15,3] = 51a96b38445ff534e3cf14c23e9c977f 77|84|81|
'''

def h(s):
    return hashlib.md5(s.encode('utf-8')).hexdigest()

def bruteHash(hash):
    mini=0
    maxi=128
    for a in range(mini, maxi):
        for b in range(mini, maxi):
            for c in range(mini, maxi):
                tmp = chr(a)+chr(b)+chr(c)
                if h(tmp) == hash:
                    return [a,b,c]
                    
    return 1

def keygen():
    
    flag  ="m4y_th3_5yn7h351z3r5_b3_w17h_y0u"
    hashed="ca238e87f380eb6b709f26c8cb1a8c72"
    print(len(flag))
    print(len(hashed))
    hardcoded=[]
    for i in range(0, len(flag)):
        hardcoded.append(ord(hashed[i]) ^ ord(flag[i]))
    print(hardcoded) #[14, 85, 75, 108, 76, 13, 11, 104, 83, 74, 86, 7, 13, 81, 3, 83, 77, 3, 75, 83, 109, 84, 80, 103, 20, 83, 6, 9, 103, 26, 7, 71]
    
    
    h1="714d32d45f6cb3bc336a765119cb3c4c"
    h2="51a96b38445ff534e3cf14c23e9c977f"
    h3="51a96b38445ff534e3cf14c23e9c977f"
    h4="bc9189406be84ec297464a514221406d"
    h5="4ec6aa45006dae153d94abd86b764e17"
    h6="51a96b38445ff534e3cf14c23e9c977f"
    
    print("Cracking partial hashes...")
    a=bruteHash(h1)
    b=bruteHash(h2)
    c=bruteHash(h3)
    d=bruteHash(h4)
    e=bruteHash(h5)
    f=bruteHash(h6)
    
    res = a+b+c+d+e+f
    print("MIDI sequence:")
    print(res)
    
    s=""
    for x in res:
        s+=chr(x)
    s=h(s)
    print("Hash of this MIDI sequence: ")
    print(s)
    
    hardcoded=[14, 85, 75, 108, 76, 13, 11, 104, 83, 74, 86, 7, 13, 81, 3, 83, 77, 3, 75, 83, 109, 84, 80, 103, 20, 83, 6, 9, 103, 26, 7, 71]
    res=""
    for i in range(0, len(hardcoded)):
        res += chr(hardcoded[i] ^ ord(s[i]))
    print("Flag: ")
    print("justCTF{"+res+"}")
    
keygen()