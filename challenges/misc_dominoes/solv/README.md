## Description
The challenge is about combining three-letter dominoes into a full sentence. Each of the dominoes has to be used exactly once. 

For example, from DOM, OMI, MIN, INO, NOE, OES you create:

```
DOM
 OMI
  MIN
   INO
    NOE
     OES
```

After overlapping, you see that the word is `DOMINOES`

This challenge is inspired by another challenge prepared by me, that is about leaking all three-letters words and then use them to recover the whole CSRF token with only one page reload. 

## Solution

I used the `backtracking` algorithm to find all the possible solutions where the correctness function is the existence of each word in the `english top 10000` dictionary.

After running the algorithm, it produced `7296` correct solutions. 

From reading the first lines of the produced file we can notice that each sentence consists of the same words but in the permutated order. 

```
there_the_player_like_you_shall_solve_doubt_great_in_my_mind_that_puzzle_was_no_single
there_the_player_like_you_shall_solve_doubt_in_my_mind_that_great_puzzle_was_no_single
there_the_player_like_you_shall_solve_was_no_single_doubt_great_in_my_mind_that_puzzle
there_the_player_like_you_shall_solve_was_no_single_doubt_in_my_mind_that_great_puzzle
there_the_player_like_you_shall_single_was_no_solve_doubt_great_in_my_mind_that_puzzle
there_the_player_like_you_shall_single_was_no_solve_doubt_in_my_mind_that_great_puzzle
there_the_player_like_you_solve_doubt_great_in_my_mind_that_puzzle_was_no_shall_single
```

The idea of the challenge is to find the correct flag from these `7296` lines. From the challenge description, it was clear that the flag is in the unusual format, and that it consists of lower_case english words that when combined produce a  grammatically correct meaningful sentence.

The approach for reducing the number of lines is to filter out all "strange" sentences.

```
Start: 7296
^.*(the_was).*$\n - 1632
^.*(the_you).*$\n - 1632
^.*(the_that).*$\n - 528
^.*(was_no_shall).*$\n - 1752
^.*(was_no_solve).*$\n - 875
^.*(solve_doubt_great).*$\n - 90
^the_there.*$\n - 40 
^that_in_my_mind.*$\n - 86
^.*there_doubt_great.*$\n - 36
^.*that_great_in_my_mind.*$\n - 192
^.*player_like_there.*$\n - 28
^.*puzzle_the_doubt.*$\n - 12
^.*great_puzzle_player.*$\n - 13
^.*player_like_the_doubt.*$\n - 19
^.*player_like_doubt.*$\n - 65
^.*shall_solve_doubt.*$\n - 39
^.*player_like_the_puzzle.*$\n - 5
^.*there_doubt_in_my_mind.*$\n - 21
^.*was_no_single$\n - 116
^.*the_doubt_great.*$\n - 48

Left: 67
```

For example, the above approach can reduce the number of solutions to 67, from where it's relatively easy to find the best candidates for the flag, which is **justCTF{there_was_no_single_doubt_in_my_mind_that_great_player_like_you_shall_solve_the_puzzle}**

## PoC

I created PoC, that solves the challenge.

```sh
node --max-old-space-size=10000 dominoes-solver.js
```