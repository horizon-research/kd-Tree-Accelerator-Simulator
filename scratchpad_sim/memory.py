
from copy import deepcopy
import numpy as np
import queue
READ = 0
WRITE = 1

POINT = 0
NODE = 1
TOPTREE_POINT = 2
TOPTREE_NODE = 3
QUERY = 4
STACK = 5

X = 0
Y = 4
Z = 8

P = 0
LEFT = 8
RIGHT = 16
LOAD_CYCLES = 10
#Constants which make trace writes more readable
data_sizes = [16, 24, 16, 24, 40, 24]

class Memory:
    def __init__(self,  duplicated, scratchpads,  dram):
        #self.scratchpads = scratchpads
        self.memory_ptrs = [0, 0, 0, 0, 0, 0]
        self.scratchpads = scratchpads
        self.active = [0, 0, 0, 0, 0, 0]
        self.ready = [True, True, True, True, True, True]
        self.processing_loads = []
        if duplicated:
            for i in range(len(scratchpads)):
                spad = scratchpads[i]
                self.scratchpads.append(deepcopy(spad))
        self.num_scratchpads = len(scratchpads)
        
        self.split = len(self.scratchpads) > 1
        self.DRAM = dram
    def calculate_address_space(self, subtree_size, toptree_size, depth):
        #Pointers in memory to start of scratchpad sections are calculated
        self.memory_ptrs[POINT] = 0
        self.memory_ptrs[NODE] = data_sizes[POINT] * subtree_size
        self.memory_ptrs[TOPTREE_POINT] =self.memory_ptrs[NODE] + (data_sizes[NODE] *  subtree_size)
        self.memory_ptrs[TOPTREE_NODE] =self.memory_ptrs[TOPTREE_POINT] + (data_sizes[TOPTREE_POINT] * toptree_size)
        self.memory_ptrs[QUERY] =self.memory_ptrs[TOPTREE_NODE] + (data_sizes[NODE] * toptree_size)
        self.memory_ptrs[STACK] =self.memory_ptrs[QUERY] + (data_sizes[STACK] * depth)

        
    
    #Computes address for given address based on data type, data index, and offset, and writes it to the trace in a tuple
    
    def read(self, access_type, address):
        if self.split:
                active_scratchpad = self.active[access_type]
                if active_scratchpad == -1:
                    print("*********************")
                    return True
                scratchpad = self.scratchpads[active_scratchpad]
        else:
            scratchpad = self.scratchpads[0]
        return scratchpad.read(address)

    def address(self, data_type, index, offset):
        address = (data_sizes[data_type] * index) + offset
        if not self.split:
            address += self.memory_ptrs[data_type]
        return address
    def load(self, data_type):
        scratchpad = 0 if self.active[data_type] == 1 else 0
        scratchpad_num = scratchpad * self.num_scratchpads + data_type
        self.processing_loads.append([scratchpad_num, data_type, LOAD_CYCLES])
    def clear_banks(self):
        for spad in self.scratchpads:
            spad.clear_banks()
    def process_loads(self):
        if self.processing_loads:
            for load in self.processing_loads:
                if load[2] == 0:
                    self.ready[load[0]] = True
                    self.active[load[1]] = load[0]
                else:
                    load[2] -= 1

#Represents scratchpad architecture
class Scratchpad:
    
    def __init__(self,  size_in, banks_in):
        #Scratchpad line size
        self.linesize = 32
        self.num_banks = banks_in
        self.size = size_in
        self.ready = False
        #Number of bits needed to represent bank and offset are calculated
        self.offset_bits = int(np.log2(self.linesize))
        self.bank_bits = int(np.log2(self.num_banks))
        #Mask to find proper offset
        self.offset_mask = self.linesize - 1
        #Mask to find proper bank
        self.bank_mask = (self.num_banks  - 1) << self.offset_bits
        #Mask to determine line number
        self.line_mask = ~self.bank_mask
        

        self.num_lines = self.size / self.linesize
        #Queue datastrcuture created for each bank, represents the memory acceses still waiting to be processed
        self.bank_reads = [None for i in range(self.num_banks)]
        self.memory_segments = []
    

    #Bank is determined from physical address
    def get_bank(self, address):
        return (address & self.bank_mask) >> self.offset_bits

    #Offset is determined from physical address
    def get_offset(self, address):
        return (address & self.offset_mask)

    #Read command is processed, determines whether there is a bank conflict for the given read, and returns true if the read was processed with no conflict
    def read(self, address):
        if address > self.size:
            print("Read out of bounds")
            return False

        conflict = False
        bank = self.get_bank(address)
        #If respective bank queue is not empty, a conflict has occured
        if self.bank_reads[bank] != None and self.bank_reads[bank] != address:
            conflict = True
        else:
            self.bank_reads[bank] = address
        return conflict




    #Removes first element in each bank queue, representing the reads processed for this cycle
    def clear_banks(self):
        for i in range(self.num_banks):
            self.bank_reads[i] = None

    def copy(self):
        return Scratchpad(self.size, self.num_banks)
class DRAM:
    def __init__(self, size):
        self.size = 0