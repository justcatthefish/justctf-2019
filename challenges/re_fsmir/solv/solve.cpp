#include <stdlib.h>
#include <string>
#include <iostream>
#include "Vfsmir.h"
#include "verilated.h"

int main(int argc, char **argv)
{
	Verilated::commandArgs(argc, argv);

	Vfsmir *top = new Vfsmir;

	std::string alph = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~";

	int cur_level = 0;

	top->di = 0;


	while(!top->solved)
	{

		for(char c : alph)
		{
			top->di = c;
			top->c = cur_level;

			top->clk = 0;
			top->eval();
			top->clk = 1;
			top->eval();

			if(top->c != 0)
			{
				std::cout << c;
				cur_level++;
				break;
			}

		}
	}

	std::cout << std::endl;

	return 0;
}