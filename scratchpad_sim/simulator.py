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
        self.queue = queue.SimpleQueue()

    def process_line(self, sim, access_num):
        if not self.stalled:
            line = self.current_query[self.current_line]
            line_tokens = line.split()
            if self.current_line == self.trace_length:
                self.busy = False
                return False

            if line_tokens[0] == "R":
                access_type = line_tokens[1]
                sim.read_nums[access_type] += 1
                address = int(line_tokens[2], 16)
                if not sim.scratchpad.read(address, access_num):
                    sim.num_conflicts += 1

            if line_tokens[0] == "I":
                if not self.queue.empty():
                    self.stalled = True
        return True
        


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
            self.PEs[i] = pe 


        self.access_num = 0
        #Statistics for simulations
        self.num_conflicts = 0
        self.read_nums = [0, 0, 0]
        self.write_nums = [0, 0, 0]

    def print_results(self):
        print(f'Point reads: {self.read_nums[0]}')
        print(f'Node reads: {self.read_nums[1]}')
        print(f'Call reads: {self.read_nums[2]}')
        print(f'Num conflicts: {self.num_conflicts}')

    def run(self):
        access_num = 0
        while self.PEs_active:
            for pe in self.PEs:
                if pe.process_line(self, access_num):
                    access_num += 1
                elif self.current_query < self.num_queries:
                    self.assign_query(pe)
        


    

    def assign_query(self, pe):
        pe.current_query = self.traces[self.current_query]
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