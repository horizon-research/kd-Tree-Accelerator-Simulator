# kd-Tree-Scratchpad-Sim
---
This repository contains the source code for a simple simulation of a point cloud accelerator. It consists of two basic parts:

First, an implementation of the kd-Tree data structure, and some of its most commonly used search algorithms. When ran, these algorithms produce trace data of the simulated memory accesses performed during execution.    

Second, a simple simulation of an accelerator utilzing scratchpad memory, which takes in the kd-Trace traces, and simulates the given memory accesses on an acclerator with a specified configuration.  



### Scratchpad Simulator instructions:
- In the scratchpad_sim folder, run in the format:
  python3 simulator.py <kd-Tree input> <Query input> Where the input files are found in their respective folders  
- Example:  
  > python3 simulator.py test q1
- Upon running the program, the user will be prompted to input their desired configuration for the accelerator, with the simulation being run on the inputted    configurations until the user wants to quit.
