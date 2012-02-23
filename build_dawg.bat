gcc -std=c99 -O3 -c -o _dawg.o dawg.c
gcc -shared -o _dawg.dll _dawg.o
del _dawg.o
