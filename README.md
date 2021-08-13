# k-d Tree Scratchpad Simulator
---
This repository contains the source code for a simple simulation of a point cloud accelerator. 
The simulator takes in a k-d tree input file, a knn search query file, and a simulator configuration file. It outputs a csv file containg the results of the simulation.  

The simulated accelerator attempts to improve memeory performance by splitting the k-d tree into two sections: the toptree, the first *n* levels of the tree, and the subtrees, whose root nodes start just below the toptree. The toptree is peremenantly stored in the scratchpad memory due top its small size and frequent usage. The subtrees are loaded into the scratchpad as needed.

### Scratchpad Simulator instructions:
- In the scratchpad_sim folder, run in the format:
  python3 run.py \<Config Input> <# of simulations to be performed in parallel> 
- Example:  
  > python3 run.py test 2
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
- Simulator version
- Number of toptree levels
- Examples
  > stat_input stat_queries0.25 PIPELINED NON-MERGED ACTUAL 1 SPLIT 5000000 1 5000000 1 5000000 1 NEW 6
  
  
  
