from scratchpad import Scratchpad
import sys
import queue
class PE:
    def __init__(self):
        self.stalled = False
        self.busy = False
        self.current_line = 0
        self.trace_length = 0
        self.current_query = []
        self.dependencies = set()

    def process_line(self, sim, access_num):
        if not self.stalled:
            if self.current_line == self.trace_length:
                self.busy = False
                return False

            line = self.current_query[self.current_line]
            line_tokens = line.split()

            if line_tokens[0] == "R":
                sim.access_num += 1
                access_type = int(line_tokens[1])
                sim.read_nums[access_type] += 1
                address = int(line_tokens[2], 16)
                self.dependencies.add(access_num)
                if not sim.scratchpad.read(address, access_num):
                    sim.num_conflicts += 1

            if line_tokens[0] == "I":
                if len(self.dependencies) > 0:
                    self.stalled = True
                    sim.stalled_cycles += 1

            self.current_line += 1
        else:
            sim.stalled_cycles += 1
        return True


    def remove_dependencies(self, accesses):
        for access in accesses:
            self.dependencies.discard(access)
        if len(self.dependencies) == 0:
            self.stalled = False
        


class Simulator:
    def __init__(self, num_banks, size, trace_file, num_PEs):
        self.scratchpad = Scratchpad(num_banks, size)
        self.traces = []
        
            
        queries_left = True
        self.num_queries = 0
        self.current_query = 0
        while queries_left:
            try:
                fin = open("../Trace_Files/" + trace_file + "_" + str(self.num_queries))
                self.traces.append(fin.readlines())
                self.num_queries += 1
            except:
                queries_left = False
            
        self.num_PEs = num_PEs
        self.PEs = []
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
        print(f'Point reads: {self.read_nums[0]}')
        print(f'Node reads: {self.read_nums[1]}')
        print(f'Call reads: {self.read_nums[2]}')
        print(f'Num conflicts: {self.num_conflicts}')
        print(f'Cumulative stalled cycles: {self.stalled_cycles}')
        print(f'Num cycles: {self.cycles}')


    def run(self):
        access_num = 0
        while self.PEs_active():
            for pe in self.PEs: 
                if (not pe.process_line(self, self.access_num)) and (self.current_query < self.num_queries):
                    self.assign_query(pe)
            processed_accesses = self.scratchpad.clear_banks()
            for pe in self.PEs:
                pe.remove_dependencies(processed_accesses)
            self.cycles += 1



    

    def assign_query(self, pe):
        if self.current_query < self.num_queries:
            pe.current_query = self.traces[self.current_query]
            pe.trace_length = len(pe.current_query)
            pe.busy = True
            self.current_query += 1

    def PEs_active(self):
        for pe in self.PEs:
            if pe.busy == True:
                return True
        return False



def main():
    num_banks = int(sys.argv[1])
    size = int(sys.argv[2])
    file = sys.argv[3]
    num_units = int(sys.argv[4])
    s = Simulator(num_banks, size, file, num_units)
    s.run()
    s.print_results()

    
main()