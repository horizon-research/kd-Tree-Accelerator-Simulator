#include "Memory.h"
void Memory::write_access(int access_type, int data_type, int index, int offset) {
    if (access_type == 0) {
        //Address is calculated from starting memory pointer, pointer index, and given offset
        int address = mem_ptrs[data_type] + (index * mem_sizes[data_type]) + offset;
        if (address > mem_ptrs[data_type + 1]) {
            fout_arr[current_file] << "Not enough memory assigned!" << std::endl;
        }
        //Write to file, for type: 0=point, 1=node, 2=call
        else {
            fout_arr[current_file] << "R " << data_type << " 0x" << std::setw(6) << std::setfill('0') << std::hex << address << std::endl;
        }
    }
}
void Memory::write_instruction(int num) {
    for (int i = 0; i < num; i++) {
        fout_arr[current_file] << "I" << std::endl;
    }
}

//Assigns each point and node a number, and adding the pair to a dictonary
//Then assigns pointers in simulated memory for various data structures
Memory::Memory(int num_nodes, int num_trace_files_in, std::string file_out) {
    num_trace_files = num_trace_files_in;
    for (int i = 0; i < num_trace_files_in; i++) {
        fout_arr.push_back(std::ofstream());
        fout_arr.at(i).open("../Trace_Files/" + file_out + "_" + std::to_string(i));
    }
    //Areas of memory are allocated for each data type, based on the maximum possible number of allocations
    mem_ptrs[POINT] = 0;
    mem_ptrs[NODE] = mem_sizes[POINT] * (num_nodes + 1);
    mem_ptrs[STACK] = mem_ptrs[NODE] + (mem_sizes[NODE] * num_nodes);
    mem_ptrs[STRUCTURE] = mem_ptrs[STACK] + (mem_sizes[STACK] * (num_nodes + 1));
    mem_ptrs[4] = mem_ptrs[STRUCTURE] + (mem_sizes[STRUCTURE] * (num_nodes + 1));
    //Prints memory addresses to trace file
    fout_arr.at(0) << "0x" << std::hex << std::setw(6) << std::setfill('0') << mem_ptrs[POINT]  
         << " 0x" << std::hex << std::setw(6) << std::setfill('0') << mem_ptrs[NODE] 
         << " 0x" << std::hex << std::setw(6) << std::setfill('0') << mem_ptrs[STACK] 
         << " 0x" << std::hex << std::setw(6) << std::setfill('0') <<  mem_ptrs[3] << std::endl;
}

//Sepcialized function to write traces for distance calculation
void Memory::write_distance(int p1_index, int p2_index) {
    write_access(READ, POINT, p1_index, X);
    write_access(READ, POINT, p2_index, X);
    write_instruction(3);

    write_access(READ, POINT, p1_index, Y);
    write_access(READ, POINT, p2_index, Y);
    write_instruction(3);


    write_access(READ, POINT, p1_index, Z);
    write_access(READ, POINT, p2_index, Z);
    write_instruction(4);

}
void Memory::set_fout(int num) {
    current_file = num;
}