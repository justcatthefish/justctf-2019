### FSMir

RE/hardware primer (trivial by design) consisting of reverse engineering a DFA implemented in SystemVerilog.
The state machine simply counts the correct characters, and resets the counter on error. The task can be solved either by inspecting the code or brute forcing, as the complexity is linear.
In the `./solv` directory you can find a solution which compiles the code with Verilator and then bruteforces the flag.
