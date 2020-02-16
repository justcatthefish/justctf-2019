shellcodeexecutor: shellcodeexecutor.c
	gcc -lseccomp -Wall -Wpedantic $^ -o $@

demo_shellcode: demo_shellcode.asm
	nasm $^
