/*
 * Gunnar Hammonds
 * Basic implementation of Kd tree as well as nearest neighbour search
 */


#include "KD_Tree.h"
#include <fstream> 
#include <vector>
int main(int argc, char* argv[]) {
    if (argc != 4) {
        std::cout << "Invalid number of arguments\n";
        return 1;
    }
    KD_Tree tree(argv[1], argv[3]);
    
    std::ifstream fin("../Search_Inputs/" + std::string(argv[2]));

    if (fin.is_open()) {
        std::string line;
        float value;
        //kd-tree dimension found
        getline(fin, line);
        int num_dimensions = stoi(line);
        if (num_dimensions != tree.get_num_dimensions()) {
            std::cout << "Tree and Search dimensions do not match" << std::endl;
            exit(0);
        }
        //Each line of file is read
        while (getline(fin, line)) {
            std::istringstream sin(line);
            std::string query_type;
            sin >> query_type;
            float values[num_dimensions];
            bool KNN = false;
            if (query_type == "KNN") {
                KNN = true;
            }
            //Point is created and added to tree
            for (int i = 0; i < num_dimensions; i++) {
                sin >> value;
                values[i] = value;
            }
            Point query(num_dimensions, values);
            if (KNN) {
                int k;
                sin >> k;
                std::vector<Point*> points = tree.knn_search(query, k);
                for (auto p : points) {
                    std::cout << *p << std::endl;
                }
            }
            else {
                Point* p = tree.nearest_neighbour(query);
                std::cout << *p << std::endl;
            }
            
        }
    }
    else {
        std::cout << "Error opening file: " << argv[2] << std::endl;
        exit(0);
    }
    
    return 0;
}
