#Gunnar Hammonds
#Simulator for configurable point cloud accelerator. 

from memory import Scratchpad
from kd_tree import KD_Tree
from kd_tree import Point
from query import Query
from pe import PE
import csv
import sys
    
#Represents high level simulator, contains PEs, as well as statistics on the current simulation
class Simulator:
    def __init__(self, kd_tree_in, queries_in, scratchpads, num_PEs, pipelined, merged_queues, ideal):
        #Scratchpad setup
        self.split = False
        self.scratchpads = scratchpads
        if len(scratchpads) > 1:
            self.split = True

        self.kd_tree = kd_tree_in
        self.queries = queries_in
        self.num_queries = len(queries_in)

        #Query to be processed next
        self.nodes_visited = 0
        self.query_index = 0

        self.stages_stalled = 0
        #PE setup
        self.num_PEs = num_PEs
        self.PEs = []
        self.pipelined = pipelined
        self.pipeline_size = 32
        self.backtrack_pipeline_size = 8
        self.ideal = ideal
        #Creates appropriate number of query queues
        self.merged_queues = merged_queues
        self.query_queues = []
        if merged_queues:
            self.query_queues.append([])
        else:
            for i in range(self.num_PEs):
                self.query_queues.append([])

        self.active_queries = []

        #PEs are initally assigned queries
        self.initialize_PEs(self.num_PEs)

        #Ensures k-d tree trace will use proper address calculation
        self.kd_tree.split = self.split

        #Statistics for simulations
        self.num_conflicts = 0
        self.stalled_cycles = 0
        self.access_nums = [0, 0, 0]
        self.cycles = 0

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
        #print("\nSummary:")
        #print(f'Num PEs: {self.num_PEs}')
        results.append(self.num_PEs)

        #print(f'Pipelined: {self.pipelined}')
        results.append(self.pipelined)

        #print(f'Merged Query Queue: {self.merged_queues}')
        results.append(self.merged_queues)

        config = 'Split' if self.split else 'Joint'
        #print(f'Scratchpad Configuration: {config}\n')
        results.append(self.split)
        
        if self.split:
            #print(f'Point scratchpad size: {self.scratchpads[0].size}')
            #print(f'Point scratchpad banks: {self.scratchpads[0].num_banks}')

            #print(f'Node scratchpad size: {self.scratchpads[1].size}')
            #print(f'Node scratchpad banks: {self.scratchpads[1].num_banks}')

            #print(f'Stack scratchpad size: {self.scratchpads[1].size}')
            #print(f'Stack scratchpad banks: {self.scratchpads[1].num_banks}')
            results += [self.scratchpads[0].size, self.scratchpads[0].num_banks, self.scratchpads[1].size, self.scratchpads[1].num_banks,self.scratchpads[2].size, self.scratchpads[2].num_banks]
        else:
            #print(f'Scratchpad size: {self.scratchpads[0].size}')
            #print(f'Scratchpad banks: {self.scratchpads[0].num_banks}')
            results += [self.scratchpads[0].size, self.scratchpads[0].num_banks, "NA", "NA", "NA", "NA"]


        #print(f'Ideal: {self.ideal}')
        results.append(self.ideal)

        #print(f'\nNumber of queries processed: {self.num_queries}\n')
        results.append(self.num_queries)

        #print(f'Number of nodes visited: {self.nodes_visited}')
        results.append(self.nodes_visited)

        #print(f'Point accesses: {self.access_nums[0]}')
        results.append(self.access_nums[0])

        #print(f'Node accesses: {self.access_nums[1]}')
        results.append(self.access_nums[1])

        #print(f'Stack accesses: {self.access_nums[2]}\n')
        results.append(self.access_nums[2])

        #print(f'Num conflicts: {self.num_conflicts}')
        results.append(self.num_conflicts)

        #print(f'Total stages stalled: {self.stages_stalled}')
        results.append(self.stages_stalled)

        percent = self.stages_stalled / (self.pipeline_size * self.num_PEs * self.cycles)
        #print(f'Percentage of time stalled : {percent}')
        results.append(percent)


        sum = 0
        max = 0
        for pe in self.PEs:
            sum += pe.lines_processed
            if pe.lines_processed > max:
                max = pe.lines_processed
        #print(f'Total lines processed: {sum}')
        results.append(sum)

        #print(f'Actual num cycles: {self.cycles}')
        results.append(self.cycles)

        avg = self.cycles / self.nodes_visited
        #print(f'Average cycles per node traversed: {avg}')
        results.append(avg)
        
        return results
        #print(f'Ideal number of cycles per node traversed: {(self.pipeline_size + self.backtrack_pipeline_size) / (self.num_PEs * (self.pipeline_size + self.backtrack_pipeline_size) / 2)}')

    #Starts processing of queries, managing PEs to ensure they always have an assigned query if possible
    def run_sim(self):
        #As long as at least one PE is processing instructions, the simulation continues
        while len(self.active_queries) > 0:
            for i in range(self.num_PEs): 
                pe = self.PEs[i]
                
                pe.manage_pipeline(self)
                
                #If the PE has an open spot in its pipeline a new query is attempted to be assigned to the PE
                if pe.pipeline_open(self.pipelined):
                    self.assign_query(i, pe)
            #Accesses processed during this cycle are returned
            for scratchpad in self.scratchpads:
                scratchpad.clear_banks()
            self.cycles += 1


    
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
                self.kd_tree.knn(p, k)
                
            else:
                print("Unknown query")
                exit()
            q.next_instruction()
            
    #Adds query which has just went through PE pipeline back to the query queue
    def query_to_queue(self, pe, query):
        index = self.PEs.index(pe)
        if self.merged_queues:
            self.query_queues[0].append(query)
        else:
            self.query_queues[index].append(query)
           
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
        results = s.print_results(sim_data[1], sim_data[2])
        writer.writerow(results)
        log.flush()
    print("Finished " + sys.argv[2])
    log.close()
        
def configurate_simulator(config):
    
    scratchpads = []
    tokens = config.split()
    kd_tree = KD_Tree("../kdTree_Inputs/" + tokens[0])
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
        for i in range(3):
            size = int(tokens[7 + (i * 2)])
            num_banks = int(tokens[8 + (i * 2)])
            scratchpads.append(Scratchpad(size, num_banks))
    #Simulator is created and ran
    
    s = Simulator(kd_tree, queries, scratchpads, num_PEs, pipelined, merged, ideal)
    s.kd_tree.calculate_address_space(s)
    return (s, tokens[0], tokens[1])

   
main()