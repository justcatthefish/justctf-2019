### Shellcode Executor PRO (pwn)

* UAF can be used to overwrite buffer used as the shellcode. The data we write is filtered (needs to be printable ascii).
* Syscalls are limited to prevent some automatic tools.
* The flag is hardcoded into the binary, so the shellcode needs to fetch its address and print it
