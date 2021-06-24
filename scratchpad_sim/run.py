import sys
from os import system
from math import floor

file = sys.argv[1]
num_parallel = int(sys.argv[2])

size = len(open("../Config_Inputs/" + file).readlines())
length = size / num_parallel
for i in range(num_parallel):
    command = "python3 simulator.py " + file + " " + file + "_" + str(i) + " " + str(floor(length * i)) + " " + str(floor(length * (i + 1))) + " &"
    print(command)
    system(command)
