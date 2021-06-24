from itertools import product
import sys
file = sys.argv[1]
out = open(file, "w+")
nums = ["1", "2", "4", "8", "16"]
kd_tree = ["stat_input"]
queries = ["stat_queries0.25_random", "stat_queries0.25"]
split = ["SPLIT"]
size = ["5000000"]
ideal = ["ACTUAL"]
merged = ["NON-MERGED", "MERGED"]
pipelined = ["PIPELINED"]
lists = [kd_tree, queries, pipelined, merged, ideal, nums, split, size, nums, size, nums, size, nums]
combinations = list(product(*lists))
for comb in combinations:
    out.write(' '.join(comb) + '\n')