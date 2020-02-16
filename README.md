# justCTF 2019

This repo contains sources for [justCTF 2019](https://2019.justctf.team) challenges hosted by [justCatTheFish](https://ctftime.org/team/33893).

TLDR: Run a challenge with `./run.sh` (requires Docker/docker-compose and might require `sudo` as we use `nsjail` extensively under the hood).

The [`challenges/`](challenges/) contains challanges directories with the following structure:
* `README.md` - official challenge description used during CTF
* `run.sh` - shell script to run the challenge locally (uses Docker and sometimes docker-compose)
* `public/` - files that were public/to download
* `private/` - sources and other unlisted files
* `README-internal.md` - internal challenge readme, might contain spoilers or description how to launch given challenge
* `flag.txt` - the flag (don't look there?)
* `solv/` - scripts and files with raw solution (used by healthcheck, if exists)
* other files


### Challenges

| Category | Name | Points | Solves | Author |
|----------|------|--------|--------|--------|
| Web | [Cache Review](challenges/web_Cache-Review) | 500 | 0 | [cypis] |
| Web | [Scam generator FIXED](challenges/web_scam-generator_fixed) | 500 | 1 | [terjanq] |
| Web | [Ugliest Website](challenges/web_ugly-website) | 474 | 2 | [terjanq] |
| Web | [Scam generator](challenges/web_scam-generator) | 474 | 2 | [terjanq] |
| Web | [Cache review but with no presents](challenges/web_Cache-review-but-with-no-presents) | 435 | 4 | [cypis] |
| Web | [Ugly website](challenges/web_ugly-website) | 293 | 21 | [terjanq] |
| Web | [FirmwareUpdater](challenges/web_firmwareupdater) | 106 | 118 | [ahpaleus] |
| RE | [Walking Simulator](challenges/re_walking_simulator) | 474 | 2 | [Tacet] |
| RE | [GoSynthesizeTheFlagYourself](challenges/re_GoSynthesizeTheFlagYourself) | 453 | 3 | [stawrocek] |
| RE | [CHANGE_VM](challenges/re_change_vm) | 347  | 12 | [stawrocek] |
| RE | [FSMir 2](challenges/re_fsmir-2) | 197 | 52 | [Altair] |
| RE | [FSMir](challenges/re_fsmir) | 154 | 77 | [Altair] |
| Pwn, RE | [Safe notes](challenges/pwn_safe_notes) | 500 | 1 | [Tacet] |
| Pwn | [ATM service](challenges/pwn_atm) | 394 | 7 | [Disconnect3d] |
| Pwn | [Shellcode Executor PRO](challenges/pwn_shellcode-) | 283 | 23 | [rand0w] |
| Pwn | [Phonebook](challenges/pwn_phonebook) | 283 | 23 | [Lacky] |
| Misc, Stego | [catto](challenges/misc_catto) | 420 | 5 | [Altair] |
| Misc, PPC | [RSA Exponent](challenges/ppc_rsa-exponent) | 326 | 15 | [Tacet] |
| Misc, PPC | [Dominoes](challenges/misc_dominoes) | 199 | 51 | [terjanq] |
| Misc | [Discreet](challenges/misc_discreet) | 373 | 9 | [Altair] |
| Misc | [wierd signals](challenges/misc_wierd_signals) | 314 | 17 | [soltys] |
| Misc | [Will it stop?](challenges/misc_will-it-stop) | 283 | 23 | [mzr] |
| Misc | [md5service](challenges/misc_md5service) | 263 | 28 | [terjanq] |
| Misc | [Matryoshka](challenges/misc_matryoshka) | 157 | 75 | [soltys] |
| Misc | [Sanity check](challenges/misc_sanity_check) | 50 | 296 | ---- |
| Crypto | [GCM](challenges/crypto_gcm) | 500 | 1 | [Gros] |
| Crypto | [p&q Service](challenges/crypto_pandq_service) | 453 | 3 | [terjanq] |
| Crypto | [Fault EC](challenges/crypto_faultec) | 394 | 7 | [Gros] |

### Write-ups
Write-ups can be found on [CTFTime](https://ctftime.org/event/943/tasks/). You should also look at challenges solution directories, if they exist (`solv/`).

### CTF Platform
We wrote our own CTF platform which is available [here](https://github.com/justcatthefish/ctfplatform).

### People involved in organizing justCTF 2019 (alphabetical order)
* [Ahpaleus]
* [Altair]
* [Cypis]
* [Disconnect3d]
* [Gros]
* [Lacky]
* [mzr]
* [rand0w]
* [soltys]
* [stawrocek]
* [Tacet]
* [terjanq]
* [Vesim]


[ahpaleus]: https://github.com/ahpaleus
[Altair]: https://github.com/AltairQ
[Cypis]: https://github.com/patryk4815
[Disconnect3d]: https://github.com/disconnect3d
[Gros]: https://github.com/GrosQuildu/
[Lacky]: https://github.com/bigben93
[mzr]: https://github.com/mzr
[rand0w]: https://github.com/rand0w
[soltys]: https://github.com/soltysek
[stawrocek]: https://github.com/stawrocek
[Tacet]: https://github.com/AdvenamTacet
[terjanq]: https://github.com/terjanq
[Vesim]: https://github.com/vesim987


### justCTF 2019 was sponsored by
* [Trail of Bits](https://www.trailofbits.com/)
* [Wirtualna Polska](https://www.wp.pl/)   

