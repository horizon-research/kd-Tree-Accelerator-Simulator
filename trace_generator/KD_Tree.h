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





//Internal node struct
struct Node {
    Point* p;
    Node* left;
    Node* right;
};
class KD_Tree {
    int num_nodes;
    int num_dimensions;
    int num_parallel_queries;
    
    Node* root;
    std::map<Node*, int>* node_nums;
    std::map<Point*, int>* point_nums;
    std::stack<int>* call_stack;


    Memory* memory;

    void free_node(Node* tree);
    Node* insert_rec(Node* tree, int level, float values_in[]);
    void print_rec(Node* tree, int level);
    void knn_rec(Point& target, std::priority_queue<std::pair<double, Point*>>& max_heap, Node* tree, unsigned int k, int level);
    void nearest_neighbour_rec(Point* target, std::pair<double, Point*> &current_best, Node* tree, int level);

    void assign_nums(Node* tree, int n, std::vector<Point*>& point_list, std::vector<Node*>& node_list);
    void build_tree(std::string file_in);
    int node_index(Node* n);
    int point_index(Point* p);



    public:
        KD_Tree(std::string file_in, std::string file_out);
        int get_num_dimensions();
        void insert(float values_in[]);
        void print();
        std::vector<Point*> knn_search(Point& target_in, unsigned int k);
        Point* nearest_neighbour(Point& target_in);
        ~KD_Tree();
      
};