[bits 64]
xor rdi, rdi
lea rsi, [rel buff]
mov rdx, buff_end - buff
mov rax, 1
syscall
ret

buff:
db "This is a demo shellcode - to use your own, please buy the full version of our software", 0x0a, 0
buff_end:
