/* chngc -> Change VM Compiler*/

#include <cstdio>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <functional>
#include <iostream>
#include <map>
#include <stdexcept>
#include <string>
#include <vector>

bool readFile(std::string fpath, std::vector<std::string>& lines){
	std::ifstream ifile(fpath);
	if(ifile.fail())
		return false;
	std::string tmp;
	while (std::getline(ifile, tmp))
		if(!tmp.empty())
			lines.push_back(tmp);
	return true;
}

int tokenize(std::string str, std::vector<std::string>& res){
	std::string tmp;
	for(int i = 0; i < str.size(); i++){
		if(str[i] != ' ')
			tmp += str[i];
		else{
		  if(!tmp.empty())
    	  res.push_back(tmp);
			tmp="";
		}
	}
	if(!tmp.empty() && tmp[0] != ' '){
		res.push_back(tmp);
	}
  return res.size();
}

void writeWord(std::ofstream& ofile, uint32_t word){
	ofile.write((char*)&word, sizeof(uint32_t));
}

uint8_t opcode_number = 0;

uint32_t imm1(const std::vector<std::string>& args){
  uint32_t res = opcode_number;
  uint32_t imm = std::stoi(args[0]) & 0xffff;
  res |= (imm << 16);
  return res;
}

uint32_t reg1imm1(const std::vector<std::string>& args){
	uint32_t res = opcode_number;
	uint32_t reg = std::stoi(args[0]);
	uint32_t imm = std::stoi(args[1]) & 0xffff;
	res |= (reg << 8);
	res |= (imm << 16);
	return res;
}

//from 1 (jmp reg) to 3 regs (add dest src1 src2)
uint32_t regs(const std::vector<std::string>& args){
	uint32_t res = opcode_number;
	for(int i = 0; i < args.size(); i++){
		uint32_t encoded = std::stoi(args[i]);
		res |= (encoded << (8+i*8));
	}
	return res;
}

uint32_t none(const std::vector<std::string>& args){
  return 0;
}

void compile(const std::vector<std::string>& lines){
	std::ofstream fout;
	fout.open("a.out", std::ios::out | std::ios::binary);

	std::map<std::string,
		std::pair<
			std::function< uint32_t(const std::vector<std::string>&) >,
			uint8_t> >
	m = {
		{"set",    {&reg1imm1, 1}},
		{"mov",    {&regs, 2}},
		{"add",    {&regs, 3}},
		{"xor",    {&regs, 4}},
		{"jmp",    {&regs, 5}},
		{"jb",     {&regs, 6}},
		{"load",   {&regs, 7}},
		{"storeb", {&regs, 8}},
		{"storew", {&regs, 9}},
		{"nop",    {&regs, 10}},
		{"read",   {&regs, 11}},
		{"write",  {&regs, 12}},
		{"exit",   {&imm1, 13}},
		{"enc",    {&imm1, 14}},
    {"je",     {&regs, 15}},
    {"dbg",    {&none, 16}}
	};

  std::map<std::string, std::string> aliases = {};
	
  for(int i = 0; i < 16; i++){
    std::string reg = "r" + std::to_string(i);
    aliases[reg] = std::to_string(i);
  }

  uint32_t enc_key=0;
  uint32_t ip=0;
  for(int i = 0; i < lines.size(); i++){
    std::vector<std::string> args;
		if(!tokenize(lines[i], args))
      continue;
   
    //comments
    std::string opcode = args[0];
    if(opcode.size() >= 1 && opcode[0] == ';')
      continue;
   
    for(int i = 0; i < args.size(); i++){
      if(args[i].size() >= 1 && args[i][0] == ';'){
        args.erase(args.begin()+i, args.end());
        break;
      }
    }
    
    for(int i = 0; i < args.size(); i++){
      if(aliases.find(args[i]) != aliases.end()){
        args[i] = aliases[args[i]];
      }
    }
    if(args.size() >= 3 && args[0] == "alias"){
      if(args[2] == "$"){
        uint32_t jump_offset = 0;
        if(args.size() == 4){
          jump_offset = std::stoi(args[3]);
        }

        aliases[args[1]] = std::to_string(ip+jump_offset);
      }
      else
        aliases[args[1]] = args[2];
      continue;
    }
  	args.erase(args.begin());
    if(m.find(opcode) == m.end()){
      printf("Unknown opcode |%s|!\n", opcode.c_str());
      fout.close();
      return;
    }
    auto x = m[opcode];
	  opcode_number = x.second;
	  uint32_t word = x.first(args);
    word ^= enc_key;
    writeWord(fout, word);

    if(args.size() == 1 && opcode == "enc")
    {
      enc_key = atoi(args[0].c_str());
      enc_key |= (enc_key << 16);
    }

    ip += 4;
	}

	fout.close();
}

int main(int argc, char* argv[]){
	if(argc != 2){
		printf("./chngvm file\n");
		return -1;
	}
	std::vector<std::string> lines;
	if(!readFile(argv[1], lines))
		throw std::invalid_argument("Can't read file");
	compile(lines);	
}
