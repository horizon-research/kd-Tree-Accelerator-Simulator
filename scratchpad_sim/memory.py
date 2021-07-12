

import numpy as np
import queue
READ = 0
WRITE = 1

POINT = 0
NODE = 1
STACK = 2
END = 3
X = 0
Y = 4
Z = 8

P = 0
LEFT = 8
RIGHT = 16

#Constants which make trace writes more readable
data_sizes = [16, 24, 40]

class Memory:
    def __init__(self, scratchpads, dram):
        self.scratchpads = scratchpads
        self.split = len(self.scratchpads) > 1
        self.DRAM = dram
    def calculate_address_space(self, sim):
        #Pointers in memory to start of scratchpad sections are calculated
        self.memory_ptrs[NODE] = data_sizes[POINT] * (self.num_nodes + 1)
        self.memory_ptrs[STACK] =self.memory_ptrs[NODE] + (data_sizes[NODE] *self.num_nodes)
        self.memory_ptrs[END] =self.memory_ptrs[STACK] + (data_sizes[STACK] * self.tree_depth)
    
    #Computes address for given address based on data type, data index, and offset, and writes it to the trace in a tuple
    
    def read(self, access_type, address):
        if self.split:
                scratchpad = self.scratchpads[access_type]
        else:
            scratchpad = self.scratchpads[0]
        return scratchpad.read(address)

    def address(self, data_type, index, offset):
        address = (data_sizes[data_type] * index) + offset
        if not self.split:
            address += self.memory_ptrs[data_type]
        return address
           
#Represents scratchpad architecture
class Scratchpad:
    
    def __init__(self,  size_in, banks_in):
        #Scratchpad line size
        self.linesize = 32
        self.num_banks = banks_in
        self.size = size_in
    
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


class DRAM:
    def __init__(self, size):
        self.size = 0