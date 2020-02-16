### FSMir 2

Basically the same as FSMir 1, but now the transition function is much denser, in order to make bruteforcing infeasible.
Compiling or otherwise parsing the code is necessary in order to extract the transition table and perform a graph traversal. In `./solve` you can find a script which compiles (transpiles?) the code with Verilator and performs a DFS search using the module as a black box.
