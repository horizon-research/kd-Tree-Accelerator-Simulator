import sys
import csv
from os import system
from math import floor

file = sys.argv[1]
num_parallel = int(sys.argv[2])
if len(sys.argv) == 4 and sys.argv[3] == "-p":
    profile = "-m cProfile "
else:
    profile = ""
log = open("../Log_Files/" + file + "_log.csv", "w")
#Writes first line of csv
writer = csv.writer(log)
writer.writerow(["kd_Tree_File", "Query_File", "Num_PEs", "Pipeline", "Merged_QQ", "Split_Scratchpad", "Scratchpad_0_Size", "Scratchpad_0_Banks",  "Scratchpad_1_Size", "Scratchpad_1_Banks", "Scratchpad_2_Size", "Scratchpad_2_Banks","Ideal",
    "Queries_Processed", "Nodes_Visited", "Point_Accesses", "Node_Accesses", "Stack_Accesses", 
    "Conflicts", "Stages_Stalled", "Percent_Time_Stalled", "Lines_Processed", "Cycles", "Avg_Cycles_per_Node"])
log.flush()
log.close()
size = len(open("../Config_Inputs/" + file).readlines())
#Calculates number of queries to be performed by each process, and runs them each as a background process
length = size / num_parallel
for i in range(num_parallel):
    #command = "python3 " + profile + "simulator.py " + file + " " + file + "_"  + "log " + str(floor(length * i)) + " " + str(floor(length * (i + 1))) + " &"
    command = "python3 " + profile + "new_accelerator.py " + file + " " + file + "_"  + "log " + str(floor(length * i)) + " " + str(floor(length * (i + 1))) + " &"

    print(command)
    system(command)
