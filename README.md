# kd-Tree-Scratchpad-Sim
---
This repository consists of two separate parts: 
- A C++ kd-tree implementation which performs nearest-neighbour, k-nearest-neighbours, and range searches, and generates a trace file containing a series of simulated memory accesses which would occur during each query.
- A Python scratchpad simulator which takes in trace files, and simulates the accesses on a scratchpad of the desired paramesters, outputting various statistics from the simulation

### kd-Tree Trace Generator instructions:
- Run "make" command and then run in the format:
  ./trace_generator \<kd-Tree input file\>    \<Query input file\>    \<New directory to contain trace files\>  
- Example: 
  > ./trace_generator test2_in search1 test
- Input and output files should be contained in their respective folders.

### Scratchpad Simulator instructions:
- Run in format:
  python3 simulator.py \<Number of banks\>  \<Size in bytes\>  \<Number of PEs for simulation\>  \<Folder containing trace files\>  
- Example:  
  > python3 simulator.py 2 1024 2 test
