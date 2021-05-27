#include "Point.h"
#include <stdlib.h>
#include <float.h>
#include <stack>
#include <map>
#include <fstream> 
#include <sstream>
#include <iomanip>
#include <vector>
#include <bitset>

//Macros to make writes to trace file more readable
#define READ true
#define WRITE false

#define X 0
#define Y 4
#define Z 8

#define P 0
#define LEFT 8
#define RIGHT 16

#define POINT 0
#define NODE 1
#define CALL 2

//Contains padded sizes for points, nodes, and stack structures
static const int mem_sizes[] = {16, 24, 8};





//Internal node struct
struct Node {
    Point* p;
    Node* left;
    Node* right;
};
class KD_Tree {
    int num_nodes;
    int num_dimensions;

    int mem_ptrs[4];
    std::map<Node*, int>* node_nums;
    std::map<Point*, int>* point_nums;
    std::ofstream fout;
    std::stack<int>* call_stack;
    Node* root;

    void free_node(Node* tree);
    Node* insert_rec(Node* tree, int level, int values_in[]);
    void print_rec(Node* tree, int level);
    void nearest_neighbour_rec(Point* target, Point** current_best, Node* tree, double* current_distance, int level);
    void assign_nums(Node* tree, int n, std::vector<Point*>& point_list, std::vector<Node*>& node_list);
    void write_trace(bool read, int type, int num, int offset);
    void build_tree(std::string file_in);
    int node_index(Node* n);
    int point_index(Point* p);



    public:
        KD_Tree(std::string file_in, std::string file_out);
        void insert(int values_in[]);
        void print();
        Point* nearest_neighbour(Point target_in);
        ~KD_Tree();
        void memory_assignment();
      
};