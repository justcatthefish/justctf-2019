#include <signal.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

//generated with 
//python mem_gen.py > mem.h
#include "mem.h"

#define DEBUG 0

#define debug_print(fmt, ...) \
            do { if (DEBUG) fprintf(stderr, fmt, __VA_ARGS__); } while (0)

uint32_t regs[16];
uint32_t entry_point=8192;
uint32_t ip;
uint32_t enc_key;

uint8_t reg1, reg2, reg3;
uint16_t imm;

void dbg(){
#if DEBUG == 0
	printf("**********DBG**********\n");
  printf("ip=%d\n", ip);
	for(int i = 0; i < 16; i++)
		printf("reg_%d = %d (%x)\n", i, regs[i], regs[i]);
  printf("**********DBG**********\n");
#endif
}


void decodeParams(uint32_t instr){
	reg1 = (instr&0x0000ff00)>>8;
	reg2 = (instr&0x00ff0000)>>16;
	reg3 = (instr&0xff000000)>>24;
	imm  = (instr&0xffff0000)>>16;
}

//illegal
void decode0(){
	raise(SIGILL);
}

//set
void decode1(){
	debug_print("set: regs[%d]=%d\n", reg1, imm);
	regs[reg1] = imm;
}

//mov
void decode2(){
	debug_print("mov: regs[%d] = regs[%d]\n", reg1, reg2);
	regs[reg1]=regs[reg2];
}

//add
void decode3(){
	debug_print("add: regs[%d] = regs[%d] + regs[%d]\n", reg1, reg2, reg3);
	regs[reg1]=regs[reg2] + regs[reg3];
}

//xor
void decode4(){
	debug_print("xor: regs[%d] = regs[%d] ^ regs[%d]\n", reg1, reg2, reg3);
	regs[reg1]=regs[reg2] ^ regs[reg3];
} 

//jmp
void decode5(){
	debug_print("jmp: regs[%d]\n", reg1);
	ip = regs[reg1] - 4; //will be increased by 4 in runInstruction() 
}

//jb
void decode6(){
	debug_print("jb: regs[%d] < regs[%d] -> jmp regs[%d]\n", reg1, reg2, reg3);
	if(regs[reg1] < regs[reg2])
    ip = entry_point+regs[reg3] - 4;
}

//load
void decode7(){
	debug_print("load from mem[regs[%d]] to regs[%d]\n", reg2, reg1);
	regs[reg1] = memory[regs[reg2]];
}

//storeb
void decode8(){
	debug_print("store byte from regs[%d] to mem[regs[%d]]\n", reg2, reg1);
	memory[regs[reg1]] = regs[reg2];
}

//storew
void decode9(){
	debug_print("store word from regs[%d] to mem[regs[%d]]\n", reg2, reg1);
	*((uint32_t*)&memory[regs[reg1]]) = regs[reg2];
}

//nop
void decode10(){

}

//read
void decode11(){
	debug_print("reading regs[%d] characters from STDIN to mem[reg[%d]]\n", reg2, reg1);
  regs[0] = read(0, &memory[regs[reg1]], regs[reg2]);
}

//write
void decode12(){
	debug_print("writing regs[%d] characters to STDOUT from mem[reg[%d]]\n", reg2, reg1);
	write(1, &memory[regs[reg1]], regs[reg2]);
}

//exit
void decode13(){
  debug_print("exiting with code: %d\n", imm);
  exit(imm);
}

//enc
void decode14(){
  enc_key = imm;
  enc_key |= (enc_key << 16);
  debug_print("encrypting with key %d\n", enc_key);
}

//je
void decode15(){
	debug_print("je: regs[%d] == regs[%d] -> jmp regs[%d]\n", reg1, reg2, reg3);
	if(regs[reg1] == regs[reg2])
    ip = entry_point+regs[reg3] - 4;
}

void decode16(){
  dbg();
}

void (*decoders[]) () = {
	decode0, decode1, decode2, decode3, decode4, decode5, decode6,
	decode7, decode8, decode9, decode10, decode11, decode12,
  decode13, decode14, decode15, decode16
};

void runInstruction(uint32_t instr, uint32_t opcode_vec_len){
	uint8_t enc_opcode = instr&0xff;
	//uint8_t opcode = enc_opcode - (ip>>2);
	uint8_t opcode = enc_opcode;
   
  decodeParams(instr);
	if(opcode > opcode_vec_len)
		decode0();
	(*decoders[opcode])();
	ip+=4;
}

void runVM(uint32_t run_ip){
  ip = run_ip;
  while(1){
    uint32_t enc = *((uint32_t *) &memory[ip]);
		enc ^= enc_key;
		runInstruction(enc, sizeof(decoders)/sizeof(void*));
  }
}

int main(){
	runVM(entry_point);
}
