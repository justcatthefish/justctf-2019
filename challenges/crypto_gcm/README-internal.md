### GCM

Service implementing AES-GCM encryption and decryption. The task was to find GCM authentication key.

The vulnerability is that the service uses short authentication tags (16 bits). Such short tags allows us to brute-force and forge them. Such forgeries may in turn leak some information about the key. So getting enough forgeries we can compute the whole key and get the flag.

Moreover, we can increase the probability of forgery encrypting large messages. Because with `n`-bits tag and encrypted message of length `2^k`, we can forge another message that the tag will validate with probability `2^(n-k)` (instead of expected `2^n`).

The vulnerability and attack is described in the paper "Authentication weaknesses in GCM" by Niels Ferguson.
