from random import shuffle
import sys
lines = open(sys.argv[1]).readlines()
out = open(sys.argv[1] + "_random", "w+")
shuffle(lines)
out.writelines(lines)
