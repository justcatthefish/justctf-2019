main:
	g++ chngvmc.cpp -std=c++17 -o chngvmc
	./chngvmc task.chng
	python2 mem_gen.py > mem.h
	gcc change_my_mind.c -std=c11 -o change_my_mind
	strip -s change_my_mind

clean:
	rm chngvmc change_my_mind a.out a.bin mem.h
