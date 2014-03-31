all:
	g++ -O2 -c -fPIC c_velo_lib.cpp -o c_velo_lib.o
	g++ -O2 -shared -Wl,-soname,c_velo_lib.so -o c_velo_lib.so c_velo_lib.o  -lgsl -lgslcblas -lm 
