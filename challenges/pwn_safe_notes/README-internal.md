
# Safe Notes

After small reversing, we have two possibilities:
- put on stack pointer to four executable bytes, controlled by us (SHA of input)
- put on stack to read only memory with our input (as long as we want)
Then we have to create a ROP (SHA ROP).

The main problem here is that we have to be able to create rop from executable
segments of length four.
And in all, except last, we have to have ret (\xc3) at the end.
We can, however, make read-only string with a long sequence (like "/bin/sh").
