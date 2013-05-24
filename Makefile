all:
	gcc -O2 -shared -Wl,-soname,testlib -o ./GRCFlibs/thickDisc.so -fPIC ./GRCFlibs/thickDisc.c -lgsl -lgslcblas 
clean:
	rm ./GRCFlibs/thickDisc.so
