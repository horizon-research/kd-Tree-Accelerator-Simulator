from scratchpad import Scratchpad
from kd_tree import KD_Tree
from kd_tree import Point
from query import Query
import sys

#Processing Engine class, contains Pe's current status, as well as thw query it's currently assigned to
class PE:
    def __init__(self):
        self.stalled = False
        self.query = None
        self.busy = False
        self.lines_processed = 0
        self.line = ""
    #Attempts to process next instruction
    def process_line(self, sim, access_num):
        #If the PE isn't currently processing a query, nothing is done
        if self.busy:
            #Loads next instruction if not currently stalled
            if self.stalled:
                sim.stalled_cycles += 1
            else:
                self.lines_processed += 1
                self.line = self.query.next_instruction()

            #Read
            if self.line[0] == "R":
                access_type = self.line[1]
                sim.read_nums[access_type] += 1
                address = self.line[2]
                #Unique access number for this read is added to the dependencies for the curret query, the next instruction can't processed until it is resolved
                self.query.add_dependency(access_num)
                #If true is returned there was a bank conflict
                if sim.scratchpad.read(address, access_num):
                    sim.num_conflicts += 1
                sim.access_num += 1

            #Computation
            if self.line[0] == "C":
                #If there are any dependencies the computation can't be performed, and the PE is stalled
                if self.query.num_dependencies() > 0:
                    self.stalled = True
                else:
                    self.stalled = False

            #If there are no more instructions to be processed, the query is removed from the list of active queries, and the PE is ready to be assigned a new query
            if self.query.finished():
                self.busy = False
                sim.active_queries.remove(self.query)
                self.query = None


    


        

#Represents high level simulator, contains PEs, as well as statistics on the current simulation
class Simulator:
    def __init__(self, kd_tree_in, queries_in):
        self.scratchpad = None
        
        self.kd_tree = kd_tree_in
        self.queries = queries_in
        self.num_queries = len(queries_in)
        #Current query to be processed next
        self.query_index = 0
        self.active_queries = []

        self.num_PEs = 0
        self.PEs = []

        #Unique number for each access processed
        self.access_num = 0

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
            self.assign_query(pe)
            self.PEs.append(pe)

    #Prints resulting statistics
    def print_results(self):
        print("\nSummary:")
        print(f'Scratchpad size: {self.scratchpad.size} bytes')
        print(f'Scratchpad banks: {self.scratchpad.num_banks}')
        print(f'Num PEs: {self.num_PEs}')
        print(f'Number of queries processed: {self.num_queries}\n')

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


    #Starts processing of queries, managing PEs to ensure they always have an assigned query if possible
    def run_sim(self):
        #As long as at least one PE is processing instructions, the simulation continues
        while len(self.active_queries) > 0:
            for pe in self.PEs: 
                #PE attempts to process curent trace line
                pe.process_line(self, self.access_num)
                #If the PE isn't busy, and there are remaining trace files to be processed, a new one is assigned to the PE
                if not pe.busy:
                    self.assign_query(pe)
            #Accesses processed during this cycle are returned
            processed_accesses = self.scratchpad.clear_banks()
            #Accesses potentially removed from dependency lists
            self.clear_dependencies(processed_accesses)
            self.cycles += 1


    
    #Given PE is assigned a new query trace file
    def assign_query(self, pe):
        if self.query_index < self.num_queries:
            pe.busy = True
            line = self.queries[self.query_index]
            q = Query()
            self.query_index += 1
            self.kd_tree.query_trace = q
            self.active_queries.append(q)
            pe.query = q
            tokens = line.split()
            if tokens[0] == "KNN":
                p = Point(tokens[1:4])
                k = int(tokens[4])
                self.kd_tree.knn(p, k)
            return True
        else:
            return False
                
    #If any of the active queries had an access processed by the scratchpad, it is removed from its list of dependencies
    def clear_dependencies(self, deps):
        for dep in deps:
            for query in self.active_queries:
                query.remove_dependency(dep)


#Takes input and runs on according simulator
def main():
    kd_tree = KD_Tree("../kdTree_Inputs/" + sys.argv[1])
    queries = open("../Query_Inputs/" + sys.argv[2]).readlines()
    
    running = True
    while running:
        line = input("Enter accelerator configuration <Num banks> <Scratchpad size> <Num PEs> (\"quit\" to quit): ")
        if line == "quit":
            running = False
        else:
            s = Simulator(kd_tree, queries)
            tokens = line.split()
            s.scratchpad = Scratchpad(int(tokens[0]), int(tokens[1]))
            s.initialize_PEs(int(tokens[2]))
            s.run_sim()
            s.print_results()
   
main()