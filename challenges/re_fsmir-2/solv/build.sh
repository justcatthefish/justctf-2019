export CPPFLAGS="-std=c++11"
verilator --cc fsmir2 -I../public --exe sim_main.cpp &&
make -j -C obj_dir -f Vfsmir2.mk Vfsmir2
./obj_dir/Vfsmir2
