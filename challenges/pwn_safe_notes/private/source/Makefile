all: release-program static-program debug-program
	#ALL

release-program: program.cpp
	g++ -fPIE -std=c++17 -Wall -Wextra -pedantic -s -O3 program.cpp -lssl -lcrypto -o release-program



static-program: program.cpp
	g++ -fPIE -std=c++17 -static -Wall -Wextra -pedantic program.cpp -lssl -lcrypto -O3 -s -o static-program

debug-program: program.cpp
	g++ -DPRINTROP -std=c++17 -Wall -Wextra -pedantic program.cpp -lssl -lcrypto -O3 -g -o debug-program

clean: cracker debug-program static-program release-program
	rm -rf debug-program static-program release-program cracker

cracker: cracker.cpp
	g++-8 -std=c++17 -Wall -Wextra -pedantic cracker.cpp -lssl -lcrypto -O3 -g -o cracker
