from os import pipe
from scratchpad import Scratchpad
from kd_tree import KD_Tree
from kd_tree import Point
from query import Query
from pe import PE
import time
import sys
    
#Represents high level simulator, contains PEs, as well as statistics on the current simulation
class Simulator:
    def __init__(self, kd_tree_in, queries_in, scratchpads, pipelined):
        self.split = False
        self.pipelined = pipelined
        self.scratchpads = scratchpads
        if len(scratchpads) > 1:
            self.split = True
        self.ncycles = 0
        self.bcycles = 0
        self.kd_tree = kd_tree_in
        self.queries = queries_in
        self.num_queries = len(queries_in)
        #Current query to be processed next
        self.query_index = 0

        self.num_PEs = 0
        self.PEs = []
        self.query_queue = []
        self.backtrack_queue = []
        self.active_queries = []
        #Unique number for each access processed
        self.access_num = 0
        self.kd_tree.split = self.split
        #Statistics for simulations
        self.num_conflicts = 0
        self.stalled_cycles = 0
        self.read_nums = [0, 0, 0]
        self.write_nums = [0, 0, 0]
        self.cycles = 0
    #Creates desired number of PEs, assigns them inital queries to process
    def initialize_PEs(self, num_PEs):
        self.PEs.clear()
        self.num_PEs = num_PEs
        for i in range(num_PEs):
            pe = PE()
            self.assign_query(pe, False)
            self.PEs.append(pe)

    #Prints resulting statistics
    def print_results(self):
        print("\nSummary:")
        print(f'Num PEs: {self.num_PEs}')
        print(f'Pipelined: {self.pipelined}')
        config = 'Split' if self.split else 'Joint'
        print(f'Scratchpad Configuration: {config}\n')
        if self.split:
            print(f'Point scratchpad size: {self.scratchpads[0].size}')
            print(f'Point scratchpad banks: {self.scratchpads[0].num_banks}')

            print(f'Node scratchpad size: {self.scratchpads[1].size}')
            print(f'Node scratchpad banks: {self.scratchpads[1].num_banks}')

            print(f'Stack scratchpad size: {self.scratchpads[1].size}')
            print(f'Stack scratchpad banks: {self.scratchpads[1].num_banks}')
        else:
            print(f'Scratchpad size: {self.scratchpads[0].size}')
            print(f'Scratchpad banks: {self.scratchpads[0].num_banks}')


        print(f'\nNumber of queries processed: {self.num_queries}\n')

        print(f'Total accesses: {self.access_num}')
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
        print(f'Cycles lost stalling: {self.cycles - max}\n')
        print(self.ncycles)
        print(self.bcycles)

    #Starts processing of queries, managing PEs to ensure they always have an assigned query if possible
    def run_sim(self):
        #As long as at least one PE is processing instructions, the simulation continues
        while len(self.active_queries) > 0:
            for pe in self.PEs: 
                #PE attempts to process curent trace line
                #time.sleep(0.1)
                
                pe.manage_pipeline(self, pe.pipeline)
                pe.manage_pipeline(self, pe.backtrack_pipeline)
                
                #If the PE isn't busy, and there are remaining trace files to be processed, a new one is assigned to the PE
                

                if pe.pipeline_open(self.pipelined):
                    self.assign_query(pe, False)
                if pe.backtrack_pipeline_open(self.pipelined):
                    self.assign_query(pe, True)
            #Accesses processed during this cycle are returned
            for scratchpad in self.scratchpads:
                scratchpad.clear_banks()
            self.cycles += 1


    
    #Given PE is assigned a new query trace file
    def assign_query(self, pe, backtrack):
        if not backtrack:
            if len(self.query_queue) > 0:
                q = self.query_queue.pop()
                pe.pipeline[0] = q
            elif self.query_index < self.num_queries:
                line = self.queries[self.query_index]
                q = Query()
                self.kd_tree.query_trace = q
                self.active_queries.append(q)
                pe.pipeline[0] = q
                self.query_index += 1

                tokens = line.split()
                if tokens[0] == "KNN":
                    p = Point(tokens[1:4])
                    k = int(tokens[4])
                    self.kd_tree.knn(p, k)
                    
                else:
                    print("Unknown query")
                    exit()
                q.next_instruction()

                
        else:
            if len(self.backtrack_queue) > 0:
                q = self.backtrack_queue.pop()
                pe.backtrack_pipeline[0] = q
           
                
    #If any of the active queries had an access processed by the scratchpad, it is removed from its list of dependencies
    def clear_dependencies(self, deps):
        for dep in deps:
            for query in self.active_queries:
                query.remove_dependency(dep)


#Takes input and runs on according simulator
def main():
    kd_tree = KD_Tree("../kdTree_Inputs/" + sys.argv[1])
    queries = open("../Query_Inputs/" + sys.argv[2]).readlines()
    configs = open("../Config_Inputs/" + sys.argv[3]).readlines()

    for config in configs:
        scratchpads = []
        tokens = config.split()
        if tokens[0] == "PIPELINED":
            pipelined = True
        elif tokens[0] == "NON-PIPELINED":
            pipelined = False
        num_PEs = int(tokens[1])
        if tokens[2] == "JOINT":
            size = int(tokens[3])
            num_banks = int(tokens[4])
            scratchpads.append(Scratchpad(size, num_banks))
        elif tokens[2] == "SPLIT":
            for i in range(3):
                size = int(tokens[3 + (i * 2)])
                num_banks = int(tokens[4 + (i * 2)])
                scratchpads.append(Scratchpad(size, num_banks))

        s = Simulator(kd_tree, queries, scratchpads, pipelined)
        s.initialize_PEs(num_PEs)
        s.run_sim()
        s.print_results()
   
main()