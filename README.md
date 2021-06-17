# kd-Tree-Scratchpad-Sim
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
- Confgiurations can be entered line by line, and will be processed in that order
- Joint scratchpad format: \<Num PEs> JOINT \<SP size> \<SP banks>
- Split scratchpad format: \<Num PEs> SPLIT \<Point SP size> \<Point SP banks> \<Node SP size> \<Node SP banks> \<Stack SP size> \<Stack SP banks>
  
  
