#!/bin/sh
g++ -fno-stack-protector -fstack-protector-explicit -Wall -Wextra -Wpedantic -fPIE -z noexecstack -Wl,-z,relro,-z,now main.cpp -o atm
strip atm
cp atm ../../public/atm
mv atm ../binary/
