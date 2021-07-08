from collections import deque



#Class representing indivudal query, contains list of instructions to be processed, as well as all current dependencies
class Query:
    def __init__(self):
        #self.instructions = []
        self.instructions = deque()
        self.length = 0
        self.stalled = False
        self.backtrack = False
        self.subtree = -1
        self.heap = None
        self.p = None
    #Adds instruction tuple to list
    def add(self, instruction):
        self.instructions.append(instruction)
        self.length += 1


    #There are no more instructions to process
    def finished(self):
        return not self.instructions
        
    #Removes instruction from top of list and returns it
    def next_instruction(self):
        if self.instructions:
            if not self.stalled:
                self.current_instruction = self.instructions.popleft()
        else:
            return "?"

#Computes address for given address based on data type, data index, and offset, and writes it to the trace in a tuple
def access(self, access_type, data_type, index, offset):
    address = (data_sizes[data_type] * index) + offset
    if not self.split:
        address += self.memory_ptrs[data_type]
    self.query_trace.add(("R", data_type, address))

#Adds desired number of non access instructions to trace
def computation(self, num):
    for _ in range(num):
        self.query_trace.add("C")
def backtrack(self):
    self.query_trace.add("BT")
        
            
