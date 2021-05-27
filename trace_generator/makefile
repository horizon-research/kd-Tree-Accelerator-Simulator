CXXFLAGS= -std=c++11 -Wall -g 
DEPFILES = KD_Tree.h Point.h

trace_generator: KD_Tree.o Point.o main.o KD_Tree.h Point.h
	g++ -o trace_generator KD_Tree.o Point.o main.o

clean:
	rm main.o KD_Tree.o Point.o trace_generator