gcc -std=c99 -O3 -c -o _engine.o engine.c
gcc -shared -o _engine.dll _engine.o
del _engine.o
