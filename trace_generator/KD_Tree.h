#include "Point.h"
#include <stdlib.h>
#include <float.h>
#include <stack>
#include <map>
#include <fstream> 
#include <sstream>
#include <vector>
#include <queue>
#include <set>
#include "Memory.h"

#define NEG_FLT_MAX -1 * FLT_MAX



//Internal node struct
struct Node {
    Point* p;
    Node* left;
    Node* right;
};
class KD_Tree {
    int num_nodes;
    int num_dimensions;
    
    Node* root;
    std::map<Node*, int>* node_nums;
    std::map<Point*, int>* point_nums;
    std::stack<int>* call_stack;



    void free_node(Node* tree);
    Node* insert_rec(Node* tree, int level, float values_in[]);
    void print_rec(Node* tree, int level);
    
    void knn_rec(Point& target, std::priority_queue<std::pair<float, Point*>>& max_heap, Node* tree, unsigned int k, int level);
    void nearest_neighbour_rec(Point* target, std::pair<float, Point*> &current_best, Node* tree, int level);
    void range_search_rec(Node* tree, float range[3][2], float BB[3][2], std::vector<Point*> &in_range, int level);

    void add_subtree(Node* tree, std::vector<Point*> &in_range);
    inline bool subset(float range[3][2],float BB[3][2]);
    inline bool overlap(float range[3][2],float BB[3][2]);
    inline bool point_in_range(float range[3][2], Point* p);

    

    void assign_nums(Node* tree, int n, std::vector<Point*>& point_list, std::vector<Node*>& node_list);
    void build_tree(std::string file_in);
    int node_index(Node* n);
    int point_index(Point* p);



    public:
        KD_Tree(std::string file_in, std::string file_out, int num_parallel_queries);
        int get_num_dimensions();
        void insert(float values_in[]);
        void print();
        std::vector<Point*> knn_search(Point& target_in, unsigned int k);
        std::vector<Point*> range_search(float range[3][2]);
        Memory* memory;
        Point* nearest_neighbour(Point& target_in);
        ~KD_Tree();
      
};