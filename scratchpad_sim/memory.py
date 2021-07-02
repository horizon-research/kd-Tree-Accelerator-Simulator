

import numpy as np
import queue


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