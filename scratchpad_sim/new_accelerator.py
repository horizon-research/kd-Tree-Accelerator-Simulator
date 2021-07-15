#Gunnar Hammonds
#Simulator for configurable point cloud accelerator. 

from memory import Memory, DRAM, Scratchpad
from new_kd_tree import KD_Tree
from new_kd_tree import Point
from query import Query
from new_pe import PE
from collections import deque
import csv
import sys
from time import sleep
    
#Represents high level simulator, contains PEs, as well as statistics on the current simulation
class Simulator:
    def __init__(self, kd_tree_in, queries_in, memory, num_PEs, pipelined, merged_queues, ideal):
        #Scratchpad setup
        self.memory = memory
        self.split = memory.split
        

        self.kd_tree = kd_tree_in
        self.queries = queries_in
        self.num_queries = len(queries_in)
        self.toptree = True
        #Query to be processed next
        self.nodes_visited = 0
        self.query_index = 0

        self.stages_stalled = 0
        #PE setup
        self.num_PEs = num_PEs
        self.PEs = []
        self.pipelined = pipelined
        self.pipeline_size = 34
        self.backtrack_pipeline_size = 8
        self.ideal = ideal
        self.inaccuracy = 0
        #Creates appropriate number of query queues
        self.merged_queues = merged_queues
        self.query_queues = []
        if merged_queues:
            self.query_queues.append([])
        else:
            for i in range(self.num_PEs):
                self.query_queues.append([])

        self.active_queries = []
        self.num_subtrees = 2**self.kd_tree.toptree_levels
        print(self.num_subtrees)
        self.local_subtree_queues = [deque() for i in range(self.num_subtrees)]
        self.subtree_queue_size = 16
        self.subtree_queries  = [deque() for i in range(self.num_subtrees)]
        self.current_subtree = -1
        #PEs are initally assigned queries
        self.initialize_PEs(self.num_PEs)

        #Ensures k-d tree trace will use proper address calculation
        self.kd_tree.split = self.split

        #Statistics for simulations
        self.num_conflicts = 0
        self.stalled_cycles = 0
        self.access_nums = [0, 0, 0, 0, 0, 0]
        self.cycles = 0
        #Initally loads data to memory
        self.memory.load(0)
        self.memory.load(1)
        self.memory.load(2)
        self.memory.load(3)

    #Creates desired number of PEs, assigns them inital queries to process
    def initialize_PEs(self, num_PEs):
        self.PEs.clear()
        self.num_PEs = num_PEs
        for i in range(num_PEs):
            pe = PE(self.pipeline_size, self.backtrack_pipeline_size)
            self.assign_query(i, pe)
            self.PEs.append(pe)

    #Prints resulting statistics
    def print_results(self, kdtree, queries):
        results = []
        results.append(kdtree)
        results.append(queries)
        results.append(self.num_PEs)
        results.append(self.pipelined)
        results.append(self.merged_queues)
        results.append(self.split)
        if self.split:
            results += [self.memory.scratchpads[0].size, self.memory.scratchpads[0].num_banks, self.memory.scratchpads[1].size, self.memory.scratchpads[1].num_banks,self.memory.scratchpads[2].size, self.memory.scratchpads[2].num_banks]
        else:
            results += [self.memory.scratchpads[0].size, self.memory.scratchpads[0].num_banks, "NA", "NA", "NA", "NA"]
        results.append(self.ideal)
        results.append(self.num_queries)
        results.append(self.nodes_visited)
        results.append(self.access_nums[0] + self.access_nums[2])
        results.append(self.access_nums[1] + self.access_nums[3])
        results.append(self.access_nums[5])
        results.append(self.num_conflicts)
        results.append(self.stages_stalled)

        percent = self.stages_stalled / (self.pipeline_size * self.num_PEs * self.cycles)
        results.append(percent)
        sum = 0
        max = 0
        for pe in self.PEs:
            sum += pe.lines_processed
            if pe.lines_processed > max:
                max = pe.lines_processed
        results.append(sum)
        results.append(self.cycles)
        avg = self.cycles / self.nodes_visited
        results.append(avg)
        
        return results

    #Starts processing of queries, managing PEs to ensure they always have an assigned query if possible
    def run_sim(self):
        #As long as at least one PE is processing instructions, the simulation continues
        print(self.toptree)
        while len(self.active_queries) > 0:
            print(len(self.active_queries))
            for i in range(self.num_PEs): 
                pe = self.PEs[i]
                pe.manage_pipeline(self)
                
                #If the PE has an open spot in its pipeline a new query is attempted to be assigned to the PE
                if pe.pipeline_open(self.pipelined):
                    self.assign_query(i, pe)
            #Accesses processed during this cycle are returned
            self.memory.clear_banks()
            self.memory.process_loads()
            if self.toptree:
                for i, queue in enumerate(self.local_subtree_queues):
                    if len(queue) == self.subtree_queue_size:
                        self.flush_queues(i, queue)
            self.cycles += 1

        if self.toptree:
            for i, queue in enumerate(self.local_subtree_queues):
                self.flush_queues(i, queue)
            
            #for queue in reversed(self.subtree_queries):
                #self.active_queries.extend(queue)
            self.active_queries.extend(self.subtree_queries[self.current_subtree])
            self.query_queues[0].extend(self.subtree_queries[self.current_subtree])
            self.memory.load(2)   
            self.memory.load(3)   
            self.toptree = False
            self.current_subtree += 1
            self.run_sim()
        else:
            if self.current_subtree < self.num_subtrees:
                self.active_queries.extend(self.subtree_queries[self.current_subtree])
                self.query_queues[0].extend(self.subtree_queries[self.current_subtree])
                self.memory.load(2)   
                self.memory.load(3) 
                self.current_subtree += 1
                self.run_sim()

    def flush_queues(self, index, queue):
        self.subtree_queries[index].extend(queue)
        queue.clear()

    
    #Given PE is assigned a new query trace file
    def assign_query(self, index, pe):
        query_queue = None
        
        #Uses either universal queue or queue assigned to PE based on simulator configuration
        if not self.merged_queues:
            query_queue = self.query_queues[index]
        else:
            query_queue = self.query_queues[0]
        
        #If there are queries in the queue, one is taken out and assigned to the PE
        if query_queue:
            q = query_queue.pop()
            if not q.backtrack:
                self.nodes_visited += 1
            pe.pipeline[0] = q
            #print(f"{q.p} {q.subtree}")
        #Otherwise, a new query trace has to be generated from the inputted list of queries
        elif self.query_index < self.num_queries:
            line = self.queries[self.query_index]
            q = Query()
            self.kd_tree.query_trace = q
            self.active_queries.append(q)
            pe.pipeline[0] = q
            self.query_index += 1
            self.nodes_visited += 1
            #Query type is determined and processed
            tokens = line.split()
            if tokens[0] == "KNN":
                p = Point(tokens[1:4])
                k = int(tokens[4])
                #if self.toptree:
                actual = self.kd_tree.knn_top(p, k)
                ideal = self.kd_tree.knn_ideal(p, k)
                sum = 0
                for p1, p2 in zip(actual, ideal):
                    sum += (p2[0] - p1[0])
                self.inaccuracy += sum
                
                
            else:
                print("Unknown query")
                exit()
            q.next_instruction()
        

            
    #Adds query which has just went through PE pipeline back to the query queue
    def query_to_queue(self, pe, query, stage):
        
        if query.subtree > -1:
            queue = self.local_subtree_queues[query.subtree]
            if len(queue) < self.subtree_queue_size:
                query.stalled = False
                self.local_subtree_queues[query.subtree].append(query)
                self.active_queries.remove(query)
                if query.stalled:
                    query.subtree = -3
                else:
                    query.subtree = -2
                return True
            else:
                
                query.stalled = True
                return False
        elif query.finished():
            self.active_queries.remove(query)
            query.stalled = False
            print(f'{query} $$$$$$$$$$$$$$$$$$$')
            return True
        elif ((query.backtrack and stage == self.backtrack_pipeline_size - 1) or stage == self.pipeline_size - 1) and not query.stalled:
            if self.merged_queues:
                self.query_queues[0].append(query)
            else:
                index = self.PEs.index(pe)
                self.query_queues[index].append(query)
            return True
    
        return False
           
#Takes input and runs on according simulator
def main():
    
    configs = open("../Config_Inputs/" + sys.argv[1]).readlines()
    log = open("../Log_Files/" + sys.argv[2] + ".csv", "a")
    if len(sys.argv) == 5:
        start = int(sys.argv[3])
        end = int(sys.argv[4])
    else:
        start = 0
        end = len(configs)


    writer = csv.writer(log)
    for i in range(start, end):
        config = configs[i]
        sim_data = configurate_simulator(config)
        s = sim_data[0]
        percent = round(((i - start) / (end - start)) * 100)
        print("\rSimulating " + sys.argv[2] + ": " + str(percent) + "%")
        s.run_sim()
        print(s.inaccuracy)
        results = s.print_results(sim_data[1], sim_data[2])
        writer.writerow(results)
        log.flush()
    print("Finished " + sys.argv[2])
    log.close()
        
def configurate_simulator(config):
    
    scratchpads = []
    tokens = config.split()
    kd_tree = KD_Tree("../kdTree_Inputs/" + tokens[0], -1)
    queries = open("../Query_Inputs/" + tokens[1]).readlines()
    #Pipelining options
    if tokens[2] == "PIPELINED":
        pipelined = True
    elif tokens[2] == "NON-PIPELINED":
        pipelined = False
    #Query queue options
    if tokens[3] == "MERGED":
        merged = True
    elif tokens[3] == "NON-MERGED":
        merged = False
    if tokens[4] == "IDEAL":
        ideal = True
    elif tokens[4] == "ACTUAL":
        ideal = False
    num_PEs = int(tokens[5])
    #Scratchpad options
    if tokens[6] == "JOINT":
        size = int(tokens[7])
        num_banks = int(tokens[8])
        scratchpads.append(Scratchpad(size, num_banks))
    elif tokens[6] == "SPLIT":
        kd_tree.split = True
        for i in range(4):
            size = int(tokens[7 + (i * 2)])
            num_banks = int(tokens[8 + (i * 2)])
            scratchpads.append(Scratchpad(size, num_banks))
    #Simulator is created and ran
    memory = Memory(True, scratchpads, None)
    kd_tree.memory = memory
    memory.calculate_address_space(kd_tree.subtree_size, kd_tree.toptree_size, kd_tree.tree_depth)
    s = Simulator(kd_tree, queries, memory, num_PEs, pipelined, merged, ideal)
    return (s, tokens[0], tokens[1])

   
main()