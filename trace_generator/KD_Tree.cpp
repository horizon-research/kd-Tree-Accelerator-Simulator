#include "KD_Tree.h"

//Constructs kd-tree based on inputted file
KD_Tree::KD_Tree(std::string file_in) {
    num_nodes = 0;
    root = NULL;
    //File to write trace to
    //Contain indices for points in nodes, used for calculating trace addresses
    node_nums = new std::map<Node*, int>();
    point_nums = new std::map<Point*, int>();
    //Simulates recursive call stack
    call_stack = new std::stack<int>();
    //Tree is constructed
    build_tree(file_in);
    memory = new Memory(num_nodes);
}
KD_Tree::~KD_Tree() {
    free_node(root);
}
//Calls recursive insert function
void KD_Tree::insert(Point &p_in) {
    root = insert_rec(root, 0, p_in);
}
//Adds point to proper location in tree, based on comparison with each nodes splitting plane value
Node* KD_Tree::insert_rec(Node* tree, int level, Point &p_in) {
    //End of tree, new node created
    if (tree == NULL) {
        tree = new Node();
        tree->p = p_in.copy();
        return tree;
    }
    else {
        int splitting_plane = level % num_dimensions;
        int current_value = tree->p->dimension_value(splitting_plane);
        //If the desired point's splitting plane value is less than the current node's move to the left child.
        //Otherwise, move to the right child
        if (current_value > p_in.dimension_value(splitting_plane)) {
            tree->left = insert_rec(tree->left, level + 1, p_in);
        }
        else {
            tree->right = insert_rec(tree->right, level + 1, p_in);
        }
        return tree;
    }   
}
Point* KD_Tree::nearest_neighbour(Point& target_in) {
    Point* target = &target_in;
    //Closest distance found yet set to maximim float value
    std::pair<float, Point*> current_best(DBL_MAX, NULL);
    //First call added to stack
    call_stack->push(0);
    //Target node added to list of point indices
    point_nums->insert(std::pair<Point*, int>(target, num_nodes));
    //Pointers to nearest and best_distance inputted to recursive function
    nearest_neighbour_rec(target, current_best, root,  0);

    return current_best.second->copy();
}
//Traverses down path as if the target point were being inserted in the tree, 
//if any point encountered along the way is closer than the current closest point,
//that point is then set to be closest point
void KD_Tree::nearest_neighbour_rec(Point* target, std::pair<float, Point*> &current_best, Node* tree, int level) {
    int call_num = call_stack->top() + 1;
    memory->write_access(READ, STACK, call_num, 16);
    memory->write_instruction(1);
    if (tree) {

        memory->write_access(READ, STACK, call_num, 24);
        memory->write_instruction(2);
        int splitting_plane = level % num_dimensions;

        //Values found for current point and target point
        memory->write_access(READ, STACK, call_num, 0);
        memory->write_access(READ, POINT, point_index(target), splitting_plane * 4);
        memory->write_instruction(1);
        int target_value = target->dimension_value(splitting_plane);

        memory->write_access(READ, STACK, call_num, 16);
        memory->write_access(READ, NODE, node_index(tree), P);
        memory->write_access(READ, POINT, point_index(tree->p), splitting_plane * 4);
        int current_value = tree->p->dimension_value(splitting_plane);
        


        //If target value is less than current, take left subtree
        memory->write_instruction(2);
        if (target_value < current_value) {
            call_stack->push(call_num + 1);
            memory->write_instruction(1);
            memory->write_access(READ, NODE, node_index(tree), LEFT);
            nearest_neighbour_rec(target, current_best, tree->left, level + 1);
            //If the current best distance + the target value is greater than the current value,
            //it is possible that the closest point could be contained in right subtree, so it is searched as well
            memory->write_access(READ, STACK, call_num, 12);
            memory->write_instruction(3);
            if (target_value + current_best.first > current_value) {
                call_stack->push(call_num + 1);
                memory->write_access(READ, NODE, node_index(tree), RIGHT);
                nearest_neighbour_rec(target, current_best, tree->right,  level + 1);
            }
        }
        //If target value is greater than current, take right subtree
        else {
            call_stack->push(call_num + 1);
            memory->write_access(READ, NODE, node_index(tree), RIGHT);
            memory->write_instruction(1);
            nearest_neighbour_rec(target, current_best, tree->right, level + 1);
            //If the target value - the current best distance is less than than the current value,
            //it is possible that the closest point could be contained in the left subtree, so it is searched as well
            memory->write_access(READ, STACK, call_num, 12);
            memory->write_instruction(4);
            if (target_value - current_best.first < current_value) {
                call_stack->push(call_num + 1);
                memory->write_access(READ, NODE, node_index(tree), LEFT);
                nearest_neighbour_rec(target, current_best, tree->left,  level + 1);
            }
        }
        //Writes traces for distance computation, in the future a more elegant solution can be found
        memory->write_access(READ, STACK, call_num, 0);
        memory->write_access(READ, NODE, node_nums->find(tree)->second, P);
        memory->write_distance(point_index(target), point_index(tree->p));


        float distance = tree->p->distance(target);
        //Comparisons start at leaf nodes at works back up the tree
        memory->write_access(READ, STACK, call_num, 16);
        memory->write_instruction(1);
        if (distance < current_best.first) {
            memory->write_access(READ, NODE, node_index(tree), P);
            memory->write_instruction(2);
            current_best.second = tree->p;
            current_best.first = distance;
        }    
    }
    //When returning to caller function, pop index off stack and write it to the trace file
    call_stack->pop();
    if (!call_stack->empty()) {
        memory->write_access(READ, STACK,  call_stack->top(), 40);
    }
}
//Recursive function to find the closest point in the tree to the given point, could be modified to find closest n points
std::vector<Point*> KD_Tree::knn_search(Point& target_in, unsigned int k) {
    std::priority_queue<std::pair<float, Point*>> max_heap;
    max_heap.push(std::pair<float, Point*>(DBL_MAX, NULL));
    Point* target = &target_in;
    //Closest distance found yet set to maximum float value
    //Address of closest point in tree
    //First call added to stack
    call_stack->push(0);
    //Target node added to list of point indices
    point_nums->insert(std::pair<Point*, int>(target, num_nodes));
    //Pointers to nearest and best_distance inputted to recursive function
    knn_rec(target_in, max_heap, root, k, 0);
    std::vector<Point*>k_points;
    while (max_heap.size() != 0) {
        k_points.push_back(max_heap.top().second->copy());
        max_heap.pop();
    }
    return k_points;
}
//Traverses down path as if the target point were being inserted in the tree, 
//if any point encountered along the way is closer than the current closest point,
//that point is then set to be closest point
void KD_Tree::knn_rec(Point& target, std::priority_queue<std::pair<float, Point*>>& max_heap, Node* tree, unsigned int k, int level) {
    int call_num = call_stack->top() + 1;
    if (tree) {
        int splitting_plane = level % num_dimensions;
        //Values found for current point and target point
        int target_value = target.dimension_value(splitting_plane);
        memory->write_access(READ, POINT, point_index(&target), splitting_plane * 4);

        int current_value = tree->p->dimension_value(splitting_plane);
        memory->write_access(READ, NODE, node_index(tree), P);
        memory->write_access(READ, POINT, point_index(tree->p), splitting_plane * 4);


        //If target value is less than current, take left subtree
        if (target_value < current_value) {
            call_stack->push(call_num + 1);
            memory->write_access(READ, NODE, node_index(tree), LEFT);
            knn_rec(target, max_heap, tree->left, k, level + 1);
            //If the current best distance + the target value is greater than the current value,
            //it is possible that the closest point could be contained in right subtree, so it is searched as well
            if (target_value +  max_heap.top().first > current_value) {
                call_stack->push(call_num + 1);
                memory->write_access(READ, NODE, node_index(tree), RIGHT);
                knn_rec(target, max_heap, tree->right, k, level + 1);
            }
        }
        //If target value is greater than current, take right subtree
        else {
            call_stack->push(call_num + 1);
            memory->write_access(READ, NODE, node_index(tree), RIGHT);
            knn_rec(target, max_heap, tree->right, k, level + 1);
            //If the target value - the current best distance is less than than the current value,
            //it is possible that the closest point could be contained in the left subtree, so it is searched as well
            if (target_value - max_heap.top().first < current_value) {
                call_stack->push(call_num + 1);
                memory->write_access(READ, NODE, node_index(tree), LEFT);
                knn_rec(target, max_heap, tree->left, k, level + 1);
            }
        }
        //Writes traces for distance computation, in the future a more elegant solution can be found
        memory->write_access(READ, NODE, node_nums->find(tree)->second, P);
        memory->write_distance(point_index(&target), point_index(tree->p));


        float distance = tree->p->distance(&target);
        //Comparisons start at leaf nodes at works back up the tree
        if (max_heap.size() < k) {
            max_heap.push(std::pair<float, Point*>(distance, tree->p));
        }
        else if (distance < max_heap.top().first) {
            max_heap.pop();
            max_heap.push(std::pair<float, Point*>(distance, tree->p));
        }
    }
    //When returning to caller function, pop index off stack and write it to the trace file
    call_stack->pop();
    if (!call_stack->empty()) {
        memory->write_access(READ, STACK,  call_stack->top(), 0);
    }
}


std::vector<Point*> KD_Tree::range_search(float range[3][2]) {
    std::vector<Point*> in_range;
    float BB[3][2] = {{NEG_FLT_MAX, FLT_MAX}, {NEG_FLT_MAX, FLT_MAX}, {NEG_FLT_MAX, FLT_MAX}};

    range_search_rec(root, range, BB, in_range, 0);
    return in_range;
}

void  KD_Tree::range_search_rec(Node* tree, float range[3][2], float BB[3][2], std::vector<Point*> &in_range, int level) {
    if (tree) {
        if (overlap(range, BB)) {
            if (subset(range, BB)) {
                add_subtree(tree, in_range);
            }
            else {
                if(point_in_range(range, tree->p)) {
                    in_range.push_back(tree->p);
                }
                int splitting_plane = level % num_dimensions;
                float BB_left[3][2] = {{BB[0][0], BB[0][1]}, {BB[1][0], BB[1][1]}, {BB[2][0], BB[2][1]}};
                BB_left[splitting_plane][1] = tree->p->dimension_value(splitting_plane);

                float BB_right[3][2] = {{BB[0][0], BB[0][1]}, {BB[1][0], BB[1][1]}, {BB[2][0], BB[2][1]}};
                BB_left[splitting_plane][0] = tree->p->dimension_value(splitting_plane);

                range_search_rec(tree->left, range, BB_left, in_range, level + 1);
                range_search_rec(tree->right, range, BB_right, in_range, level + 1);

            }
        }
    }
}
void  KD_Tree::add_subtree(Node* tree, std::vector<Point*> &in_range) {
    if (tree) {
        in_range.push_back(tree->p);
        add_subtree(tree->left, in_range);
        add_subtree(tree->right, in_range);
    }
}
inline bool KD_Tree::point_in_range(float range[3][2], Point* p) {
    for (int i = 0; i < 3; i ++) {
        if (!(p->dimension_value(i) >= range[i][0] && p->dimension_value(i) <= range[i][1])) {
            return false;
        }
    }
    return true;
}



inline bool KD_Tree::subset(float range[3][2],float BB[3][2]) {
    for (int i = 0; i < 3; i ++) {
        if (!(BB[i][0] >= range[i][0] && BB[i][1] <= range[i][1])) {
            return false;
        }
    }
    return true;
}
inline bool KD_Tree::overlap(float range[3][2],float BB[3][2]) {
    for (int i = 0; i < 3; i ++) {
        if (BB[i][0] > range[i][0]) {
            if (range[i][1] > BB[i][0]) {
                return true;
            }
        }
        else {
            if (BB[i][1] > range[i][0]) {
                return true;
            }
        }
    }
    return false;
}

//Recursively frees nodes
void KD_Tree::free_node(Node* tree) {
    if (tree == NULL) {
        return;
    }
    else {
        free_node(tree->right);
        free_node(tree->left);
        delete tree->p;
        delete tree;
    }
}
//Prints tree to stdout, showing each nodes current level in the tree, its splitting plane, and its point
void KD_Tree::print() {
    print_rec(root, 0);
    std::cout << std::endl;
}
void KD_Tree::print_rec(Node* tree, int level) {
    if (tree) {
        for (int i = 0; i < level; ++i) {
            std::cout << "     ";
        }
        std::cout << *tree->p << ":" << level % num_dimensions << std::endl;

        print_rec(tree->left, level + 1);
        print_rec(tree->right, level + 1);
    }
}



void KD_Tree::assign_nums(Node* tree, int n, std::vector<Point*>& point_list, std::vector<Node*>& node_list) {
    if (tree) {
        point_list.push_back(tree->p);
        node_list.push_back(tree);
        assign_nums(tree->left, n + 1, point_list, node_list);
        assign_nums(tree->right, n + 2, point_list, node_list);
    }
    
}



//Builds tree based on input file
void KD_Tree::build_tree(std::string file_in) {

    std::ifstream fin("../kdTree_Inputs/" + file_in);
    if (fin.is_open()) {
        std::string line;
        float value;
        num_dimensions = 3;
        std::vector<Point*> points;
        //Each line of file is read
        while (getline(fin, line)) {
            std::istringstream sin(line);
            float values[num_dimensions];
            //Point is created and added to tree
            for (int i = 0; i < num_dimensions; i++) {
                sin >> value;
                values[i] = value;
            }
            Point* p = new Point(3, values);
            points.push_back(p);
            num_nodes++;
        }
      
        well_balanced_insert(points, 0, num_nodes - 1, 0);

        std::vector<Point*> point_list;
        std::vector<Node*> node_list;
        //Points and nodes are recursively assigned indices, and added to vectors    
        assign_nums(root, 0, point_list, node_list);
        int size = point_list.size();
        for (int i = 0; i < size; i++) {
            Node* n = node_list.at(i);
            Point* p = point_list.at(i);
            node_nums->insert(std::pair<Node*, int>(n, i));
            point_nums->insert(std::pair<Point*, int>(p, i));
        }
    }
    else {
        std::cout << "Error opening file" << std::endl;
        exit(0);
    }
}
void KD_Tree::well_balanced_insert(std::vector<Point*> &vectors, int lo, int hi, int level) {
    if (hi >= lo) {
        int dimension = level % 3;
        auto comp = [dimension](const Point* a, const Point* b) {return a->dimension_value(dimension) < b->dimension_value(dimension);};
        auto it_lo = vectors.begin() + lo;
        auto it_hi = vectors.begin() + hi;
        std::sort(it_lo, it_hi, comp);

        int median = (hi + lo) / 2;
        Point p = *vectors.at(median);
        insert(p);
        well_balanced_insert(vectors, lo, median - 1, level + 1);
        well_balanced_insert(vectors, median + 1, hi, level + 1);
    }
}
//Returns index for given node
int KD_Tree::node_index(Node* n) {
    return node_nums->find(n)->second;
}

//Returns index for given point
int KD_Tree::point_index(Point* p) {
    return point_nums->find(p)->second;
}
int KD_Tree::get_num_dimensions() {
    return num_dimensions;
}
