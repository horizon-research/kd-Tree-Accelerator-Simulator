from itertools import product
import sys
file = sys.argv[1]
out = open(file, "w+")
pe_nums = ["1", "2", "4", "8", "16", "32", "64"]
spad_nums = ["16"]
kd_tree = ["stat_input"]
queries = ["stat_queries0.25_random", "stat_queries0.25", "stat_queries0.5_random", "stat_queries0.5", "stat_queries_random", "stat_queries"]
split = ["JOINT"]
size = ["5000000"]
ideal = ["IDEAL"]
merged = ["NON-MERGED", "MERGED"]
pipelined = ["PIPELINED"]
lists = [kd_tree, queries, pipelined, merged, ideal, pe_nums, split, size, spad_nums]
combinations = list(product(*lists))
for comb in combinations:
    out.write(' '.join(comb) + '\n')