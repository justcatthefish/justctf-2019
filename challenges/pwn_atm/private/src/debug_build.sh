#!/bin/sh
g++ -DLOGME -fno-stack-protector -fstack-protector-explicit -Wall -Wextra -Wpedantic -fPIE -z noexecstack -Wl,-z,relro,-z,now main.cpp -o atm_debug
mv atm_debug ../binary/
