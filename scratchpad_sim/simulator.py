from .scratchpad import Scratchpad
from .kd_tree import KD_Tree
from .kd_tree import Point

from .query import Query
import sys
import queue

#Processing Engine class, represents current status as well as curent dependencies
class PE:
    def __init__(self):
        self.stalled = False
        self.busy = False
        self.current_query = None
    #Attempts to process next instruction
    def process_line(self, sim, access_num):
        #If the end of the current trace file has been reached, the PE is no longer busy, and is ready for a new trace
        if self.current_line == self.trace_length:
            self.busy = False
            return False

        line = self.current_query[self.current_line]
        line_tokens = line.split()
        #Read
        if line_tokens[0] == "R":
            access_type = int(line_tokens[1])
            sim.read_nums[access_type] += 1
            address = int(line_tokens[2], 16)
            #Unique access number for this read is added to the dependencies for this PE, the next isntruction can't processed until it is resolved
            self.dependencies.add(access_num)
            #If true is returned there was a conflict
            if sim.scratchpad.read(address, access_num):
                sim.num_conflicts += 1
            sim.access_num += 1
        #Computation
        if line_tokens[0] == "I":
            #If there are any dependencies the computation can't be performed, and the PE is stalled
            if len(self.dependencies) > 0:
                self.stalled = True
            else:
                self.stalled = False

        if self.stalled:
            sim.stalled_cycles += 1
        else:
            self.current_line += 1
            self.lines_processed += 1

        return True

    #Each time a access is processed by the scratchpad, it is checked to be removed from this PE's dependencies
    def remove_dependencies(self, accesses):
        for access in accesses:
            self.dependencies.discard(access)


        

#Represents high level simulator, contains PEs, as well as statistics on the current simulation
class Simulator:
    def __init__(self, kd_tree_in, queries_in):
        self.scratchpad = None
        
        self.kd_tree = kd_tree_in
        self.queries = queries_in
        self.query_index = 0

        self.active_queries = []
        self.num_PEs = 0
        self.PEs = []
        #PEs are initally assigned traces
        


        self.access_num = 0
        #Statistics for simulations
        self.num_conflicts = 0
        self.stalled_cycles = 0
        self.read_nums = [0, 0, 0]
        self.write_nums = [0, 0, 0]
        self.cycles = 0

    def initialize_PEs(self, num_PEs):
        self.PEs.clear()
        for i in range(num_PEs):
            pe = PE()
            self.PEs.append(pe)


    def print_results(self):
        print("Summary:")
        print(f'Scratchpad size: {self.scratchpad.size} bytes')
        print(f'Scratchpad banks: {self.scratchpad.num_banks}')
        print(f'Num PEs: {self.num_PEs}')
        print(f'Number of queries processed: {self.num_queries}\n')


        print(f'Point reads: {self.read_nums[0]}')
        print(f'Node reads: {self.read_nums[1]}')
        print(f'Stack reads: {self.read_nums[2]}\n')

        print(f'Num conflicts: {self.num_conflicts}')
        print(f'Total number of stalled cycles: {self.stalled_cycles}')
        sum = 0
        max = 0
        for pe in self.PEs:
            sum += pe.lines_processed
            if pe.lines_processed > max:
                max = pe.lines_processed
        print(f'Total lines processed: {sum}')
        print(f'Ideal num cycles: {max}')
        print(f'Actual num cycles: {self.cycles}')
        print(f'Cycles lost stalling: {self.cycles - max}')



    def run_sim(self, kd_tree, queries):
        #As long as at least one PE is processing instructions, the simulation continues
        
        while active_queries:
            for pe in self.PEs: 
                #PE attempts to process curent trace line
                if not pe.process_line(self, self.access_num):
                    #If the PE isn't busy, and there are remaining trace files to be processed, a new one is assigned to the PE
                    if not pe.busy:
                        self.assign_query(pe)
                    pe.process_line(self, self.access_num)
            #Accesses processed during this cycle are returned
            processed_accesses = self.scratchpad.clear_banks()
            #Accesses potentially removed from dependency lists
            for pe in self.PEs:
                pe.remove_dependencies(processed_accesses)
            active_queries = self.PEs_active()
            if active_queries:
                self.cycles += 1


    
    #Given PE is assigned a new query trace file
    def assign_query(self, pe):
        if self.query_index < self.num_queries:
            line = self.queries[self.query_index]
            q = Query()
            self.kd_tree.query_trace = q
            self.active_queries.append(q)
            tokens = line.split()
            if tokens[0] == "KNN":
                p = Point(tokens[1:3])
                k = tokens[4]
                self.kd_tree.knn(p, k)
                
    #Checks if there are any busy PEs
    def PEs_active(self):
        for pe in self.PEs:
            if pe.busy == True:
                return True
        return False


#Takes input and runs on according simulator
def main():
    '''
    kd_tree = KD_Tree(sys.argv[1])
    queries = open(sys.argv[2]).readlines()
    
    s = Simulator(kd_tree, queries)
    running = True
    while running:
        line = input("Enter accelerator configuration <Num banks> <Scratchpad size> <Num PEs> (\"quit\" to quit): ")
        if line == "quit":
            running = False
        else:
            tokens = line.split()
            s.scratchpad = Scratchpad(tokens[0], tokens[1])
            s.initialize_PEs(tokens[2])
            s.run_sim()
            s.print_results()
    '''
   


        

    
main()