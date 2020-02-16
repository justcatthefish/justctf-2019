#include <stdlib.h>
#include <string>
#include <iostream>
#include "Vfsmir2.h"
#include "verilated.h"

#include <unordered_set>

std::unordered_set <int> visited;
const std::string alph = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!#$%&()*+,-./:;<=>?@[]^_`{|}~";

Vfsmir2 *top;

void dfs(int cur_c, std::string cur_prefix)
{
	if(visited.find(cur_c) != visited.end())
		return;

	visited.insert(cur_c);

	for(auto&& chr : alph)
	{
		top->clk = 0;
		top->fsmir2__DOT__c = cur_c;
		top->di = chr;
		top->eval();
		top->clk = 1;
		top->eval();

		if(top->solved)
		{
			std::cout << cur_prefix + chr << std::endl;
			// Do not terminate to perform exhaustive search
		}

		dfs(top->fsmir2__DOT__c, cur_prefix + chr);
	}
}

int main(int argc, char **argv)
{
	Verilated::commandArgs(argc, argv);

	top = new Vfsmir2;

	std::cout << "The flag is:" << std::endl;

	dfs(0, "");

	std::cout << std::endl;

	return 0;
}
