# kd-Tree-Scratchpad-Sim
---
This repository consists of two separate parts: 
- A C++ kd-tree implementation which performs nearest-neighbour searches, and genrates a trace file containing a series of simulated memory acceses which would occur during thenearest-neighbour search.
- A Python scratchpad simulator which takes in trace files, and simulates the accesses on a scratchpad of the desired paramesters, outputting various statistics from the simulation

### kd-Tree Trace Generator instructions:
- Run make command and the run in the format:
  >./trace_generator \<kd-Tree input file\>    \<NNS query input file\>    \<Trace file to write to\>
- Input and output files should be contained in their respective folders

### Scratchpad Simulator instructions:
- Run in format:
  >python3 simulator.py \<Number of banks\>  \<Size in bytes\>  \<Trace file input\> 
