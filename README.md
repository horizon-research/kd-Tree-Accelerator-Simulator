# k-d Tree Scratchpad Simulator
---
This repository contains the source code for a simple simulation of a point cloud accelerator. It consists of two basic parts:

First, an implementation of the kd-Tree data structure, and some of its most commonly used search algorithms. When ran, these algorithms produce trace data of the simulated memory accesses performed during execution.    

Second, a simple simulation of an accelerator utilzing scratchpad memory, which takes in the kd-Tree traces, and simulates the given memory accesses on an acclerator with a specified configuration.  



### Scratchpad Simulator instructions:
- In the scratchpad_sim folder, run in the format:
  python3 run.py \<Config Input> <# of simulations to be performed in parallel> 
- Example:  
  > python3 simulator.py test 2
- The simulations results will be written a a csv log file
- The number of simulations which can be run in parallel will vary based on computer specifications
  
 ### kd-Tree input format:
- Points can be entered line by line in the format of three floating point numbers ex: 3.2 -1.1 4.3  
- Order does not matter as they will automatically be inserted in a well balanced order
  
 ### Query input format:
- Queries can be entered line by line in a format based on query type
- k-nearest-nighbours format: KNN \<X\> \<Y\> \<Z\> \<k\>
  
 ### Configuration input format:
- Configurations can be entered line by line, and will be processed in that order
- There are a number of parameters for the acclerator which can be configured
- k-d Tree input file
- Query Input File
- Pipelined vs Non-Pipelined
- Merged vs Non-Merged Query Queue
- Ideal vs Actual Scratchpad Performance
- Number of PEs
- Joint vs Split Scratchpad (If split, scratchpad parameters will be entered once for each scratchpad)
- Scratchpad Size (bytes)
- Number of Scratchpad Banks
- Examples
  > stat_input stat_queries0.25 PIPELINED NON-MERGED ACTUAL 1 SPLIT 5000000 1 5000000 1 5000000 1
  > stat_input stat_queries0.25 NON-PIPELINED MERGED IDEAL 1 JOINT 5000000 1 
  
  
