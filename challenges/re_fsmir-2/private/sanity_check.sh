# DEPRECATED - use ../solv/build.sh
verilator --cc fsmir2 -I../public --exe sim_main.cpp &&
rm -r ./obj_dir
