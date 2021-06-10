READ = 0
WRITE = 1

POINT = 0
NODE = 1
STACK = 2
END = 3
X = 0
Y = 1
Z = 2

P = 0
LEFT = 1
RIGHT = 2

memory_ptrs = [0, 0, 0, 0]
current_query = None
def calculate_pointers(num_nodes):
    memory_ptrs[NODE] = data_sizes[POINT] * num_nodes
    memory_ptrs[STACK] = memory_ptrs[NODE] + (data_sizes[NODE] * num_nodes)
    memory_ptrs[END] = memory_ptrs[STACK] + (data_sizes[STACK] * num_nodes)
def write_trace(access_type, index, data_type, offset):
    address = memory_ptrs[data_type] + (data_sizes[data_type] * index) + offset
    current_query.add((access_type, data_type, address))
