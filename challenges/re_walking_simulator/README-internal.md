### Walking Simulator

Input to binary:
- Permutation
- Sequence (possibly infinity) of choices

State:
- Vertex in graph

Given:
- Iutput permutations for run with flag encoded as permutation.

Every binary has graph inside, we have to reach winning vertex to print modified permutation.
Then restore input permutation for given outputs.
And restore flag form those permutations.

Solution is dynamic binary analysis.
Scripting gdb or sth.
I tried to make static analysis hard.
