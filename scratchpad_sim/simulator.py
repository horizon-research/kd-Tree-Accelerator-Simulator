from scratchpad import Scratchpad
import sys

#Processing Engine class, represents current status as well as curent dependencies
class PE:
    def __init__(self):
        self.stalled = False
        self.busy = False
        self.lines_processed = 0
        self.current_line = 0
        self.trace_length = 0
        self.current_query = []
        self.dependencies = set()
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
        
        

#Represents high lvel simulator, contains PEs, as well as statistics on the current simulation
class Simulator:
    def __init__(self, num_banks, size, trace_file, num_PEs):
        self.scratchpad = Scratchpad(num_banks, size)
        self.traces = []
        
            
        queries_left = True
        self.num_queries = 0
        self.current_query = 0
        #Query traces are opened
        while queries_left:
            try:
                fin = open("../Trace_Files/" + trace_file + "/" + trace_file + "_" + str(self.num_queries))
                self.traces.append(fin.readlines())
                self.num_queries += 1
            except:
                queries_left = False
            
        self.num_PEs = num_PEs
        self.PEs = []
        #PEs are initally assigned traces
        for i in range(num_PEs):
            pe = PE()
            self.assign_query(pe)
            self.PEs.append(pe) 


        self.access_num = 0
        #Statistics for simulations
        self.num_conflicts = 0
        self.stalled_cycles = 0
        self.read_nums = [0, 0, 0]
        self.write_nums = [0, 0, 0]
        self.cycles = 0


    def print_results(self):
        print("Summary:")
        print(f'Scratchpad size: {self.scratchpad.size} bytes')
        print(f'Scratchpad banks: {self.scratchpad.num_banks}')
        print(f'Num PEs: {self.num_PEs}')
        print(f'Number of queries processed: {self.num_queries}\n')


        print(f'Point reads: {self.read_nums[0]}')
        print(f'Node reads: {self.read_nums[1]}')
        print(f'Stack reads: {self.read_nums[2]}')
        print(f'Num conflicts: {self.num_conflicts}')
        print(f'Total number of stalled cycles: {self.stalled_cycles}')

        max = 0
        for pe in self.PEs:
            if pe.lines_processed > max:
                max = pe.lines_processed
        print(f'Ideal num cycles: {max}')
        print(f'Actual num cycles: {self.cycles}')


    def run(self):
        #As long as at least one PE is processing instructions, the simulation continues
        active_queries = True
        while active_queries:
            print()
            for pe in self.PEs: 
                #PE attempts to process curent trace line
                pe.process_line(self, self.access_num)
                #If the PE isn't busy, and there are remaining trace files to be processed, a new one is assigned to the PE
                if (not pe.busy) and self.current_query < self.num_queries:
                    self.assign_query(pe)
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
        if self.current_query < self.num_queries:
            pe.current_query = self.traces[self.current_query]
            pe.trace_length = len(pe.current_query)
            pe.busy = True
            self.current_query += 1
    #Checks if there are any busy PEs
    def PEs_active(self):
        for pe in self.PEs:
            if pe.busy == True:
                return True
        return False


#Takes input and runs on according simulator
def main():
    num_banks = int(sys.argv[1])
    size = int(sys.argv[2])
    num_units = int(sys.argv[3])
    file = sys.argv[4]
    s = Simulator(num_banks, size, file, num_units)
    s.run()
    s.print_results()

    
main()