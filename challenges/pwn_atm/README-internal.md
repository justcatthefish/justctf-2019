### ATM (pwn)

This is a bank ATM service, where we can parse a request that will be send to an ATM and then either print or send it.

The send operation does just a write to `/dev/null`, I didn't want to connect anywhere to not let users create some outgoing connections.

TLDR:
- In the task we "save", "print" and "send" a global request instance (there is just a single one)
- We can allocate big buffer `ptr = malloc(v)` where `v` is range `[0x20000, 0x30000]`
- We can do `ptr[x:x+4] = '*'*4` where `int32_t x = atoi(input)` from this allocation, by sending a `mask-pin-at: <input>` request header
- We can also leak `ptr[x:x+4]` if we save request with `mask-pin-at: <input>` and then save one without the header and print the request

...for more bugs see `private/src/main.cpp`
