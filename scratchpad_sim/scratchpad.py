import numpy as np
import queue

def is_power2(num):
    return (num & (num - 1) == 0 and num != 0)
#PointXYZ: 16 bytes

class Scratchpad:
    
    def __init__(self, banks_in, size_in):
        self.linesize = 64
        self.num_banks = banks_in

        
        self.offset_bits = int(np.log2(self.linesize))
        self.bank_bits = int(np.log2(self.num_banks))
        #print(self.offset_bits)
        #print(self.bank_bits)
        

        self.offset_mask = self.linesize - 1
        self.bank_mask = (self.num_banks  - 1) << self.offset_bits
        self.line_mask = ~self.bank_mask
        #print(bin(self.offset_mask))
        #print(bin(self.bank_mask))

        self.size = size_in
        self.num_lines = self.size / self.linesize
        #self.lines = np.array([Line() for i in range(self.num_lines)])
        self.bank_reads = [queue.SimpleQueue() for i in range(self.num_banks)]
    
    def get_bank(self, address):
        print((address & self.bank_mask) >> self.offset_bits)
        return (address & self.bank_mask) >> self.offset_bits

    def get_offset(self, address):
        return (address & self.offset_mask)

    def read(self, address):
        bank = self.get_bank(address)
        if self.bank_reads[bank].empty():
            return True
        else:
            self.bank_reads[bank].put(address)
            return False


            
    def clear_banks(self):
        for i in range(self.num_banks):
            self.bank_reads[i].get()

class Line:
    def __init__(self):
        self.addresses_stored = []