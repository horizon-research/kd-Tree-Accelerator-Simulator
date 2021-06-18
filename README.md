# kd-Tree Scratchpad Simulator
---
This repository contains the source code for a simple simulation of a point cloud accelerator. It consists of two basic parts:

First, an implementation of the kd-Tree data structure, and some of its most commonly used search algorithms. When ran, these algorithms produce trace data of the simulated memory accesses performed during execution.    

Second, a simple simulation of an accelerator utilzing scratchpad memory, which takes in the kd-Tree traces, and simulates the given memory accesses on an acclerator with a specified configuration.  



### Scratchpad Simulator instructions:
- In the scratchpad_sim folder, run in the format:
  python3 simulator.py \<kd-Tree input> \<Query input> <Config Input>, where the input files are found in their respective folders  
- Example:  
  > python3 simulator.py test q1 c
- Upon running the program, the user will be prompted to input their desired configuration for the accelerator, with the simulation being run on the inputted    configurations until the user wants to quit.
  
 ### kd-Tree input format:
- Points can be entered line by line in the format of three floating point numbers ex: 3.2 -1.1 4.3  
- Order does not matter as they will automatically be inserted in a well balanced order
  
 ### Query input format:
- Queries can be entered line by line in a format based on query type
- k-nearest-nighbours format: KNN \<X\> \<Y\> \<Z\> \<k\>
  
 ### Configuration input format:
- Configurations can be entered line by line, and will be processed in that order
- There are a number of parameters for the acclerator which can be configured
- Pipelined vs Non-Pipelined
- Number of PEs
- Joint vs Split Scratchpad (If split, scratchpad parameters will be entered once for each scratchpad)
- Scratchpad Size (bytes)
- Number of Scratchpad Banks
- Examples
  > PIPELINED 4 SPLIT 512000 4 512000 4 512000 4  
  > NON_PIPELINED 1 JOINT 512000 8
  
  
