#include <stack>
#include <map>
#include <fstream> 
#include <iomanip>

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
#define CALL 2
#define STRUCTURE 3
//Contains padded sizes for points, nodes, and stack structures
const int mem_sizes[] = {16, 24, 8, 16};


class Memory {
    int mem_ptrs[5];
    std::ofstream fout;
    public:
        void write_access(int access_type, int data_type, int index, int offset);
        void write_instruction();
        void write_distance(int p1_index, int p2_index);
        Memory(int num_nodes, std::string file_out);
};
