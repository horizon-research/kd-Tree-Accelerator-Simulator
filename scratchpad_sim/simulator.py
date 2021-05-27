from scratchpad import Scratchpad
import sys

    


class Simulator:
    def __init__(self, num_banks, size, trace_file):
        self.scratchpad = Scratchpad(num_banks, size)
        fin = open(trace_file)
        self.trace_lines = fin.readlines()

        self.access_num = 0
        #Statistics for simulations
        self.num_conflicts = 0
        self.read_nums = [0, 0, 0]
        self.write_nums = [0, 0, 0]

        self.point_reads = 0
        self.point_writes = 0

        self.node_reads = 0
        self.node_writes = 0

        self.call_reads = 0
        self.call_writes = 0

    def print_results(self):
        print(f'Point reads: {self.read_nums[0]}')
        print(f'Node reads: {self.read_nums[1]}')
        print(f'Call reads: {self.read_nums[2]}')

    def run(self):
        while self.access_num < len(self.trace_lines):
            line = self.trace_lines[self.access_num]
            line_tokens = line.split()
            #Second token in trace file represents the data type being accessed
            access_type = int(line_tokens[1])
            #Read
            if line_tokens[0] == "R":
                    #Address converted from hexadecimal
                    address = int(line_tokens[2], 16)
                    self.read_nums[access_type] += 1
                    #If false was returned, there was a conflict
                    if not self.scratchpad.read(address):
                        self.num_conflicts += 1
                    self.scratchpad.clear_banks()
            #Increments index to next access
            self.access_num += 1
        


def main():
    num_banks = int(sys.argv[1])
    size = int(sys.argv[2])
    file = sys.argv[3]
    s = Simulator(num_banks, size, file)
    s.run()
    s.print_results()

    
main()