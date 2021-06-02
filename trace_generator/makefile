CXXFLAGS= -std=c++17 -Wall -g 
DEPFILES = KD_Tree.h Point.h Memory.h

trace_generator: KD_Tree.o Point.o Memory.o main.o KD_Tree.h Point.h Memory.h
	g++ -o trace_generator KD_Tree.o Point.o Memory.o main.o

clean:
	rm main.o KD_Tree.o Point.o Memory.o trace_generator