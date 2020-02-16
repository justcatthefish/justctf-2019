
# Safe Notes

After small reversing, we have two possibilities:
- put on stack pointer to four executable bytes, controlled by us (SHA of input)
- put on stack to read only memory with our input (as long as we want)
Then we have to create a ROP (SHA ROP).

