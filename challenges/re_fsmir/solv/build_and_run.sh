verilator --cc fsmir -I../public --exe solve.cpp &&
make -j -C obj_dir -f Vfsmir.mk Vfsmir
./obj_dir/Vfsmir
