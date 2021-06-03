#include <stack>
#include <map>
#include <fstream> 
#include <iomanip>
#include <vector>

//Macros to make writes to trace file more readable
#define READ 0
#define WRITE 1
#define X 0
#define Y 4
#define Z 8

#define P 0
#define LEFT 8
#define RIGHT 16

#define POINT 0
#define NODE 1
#define STACK 2
#define STRUCTURE 3
//Contains padded sizes for points, nodes, and stack structures
const int mem_sizes[] = {16, 24, 48, 16};


class Memory {
    int num_trace_files;
    int current_file;
    int mem_ptrs[5];
    std::ofstream* fout;
    public:
        void write_access(int access_type, int data_type, int index, int offset);
        void write_instruction(int num);
        void write_distance(int p1_index, int p2_index);
        void set_fout(std::ofstream* fout_in);
        Memory(int num_nodes);
};
