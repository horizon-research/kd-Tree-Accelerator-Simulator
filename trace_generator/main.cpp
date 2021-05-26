/*
 * Gunnar Hammonds
 * Basic implementation of Kd tree as well as nearest neighbour search
 */


#include "KD_Tree.h"
#include <fstream> 
int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cout << "Invalid number of arguments\n";
        return 1;
    }
    KD_Tree tree(argv[1], argv[2]);
    int p1_values[] = {0, 0, 0};
    Point* p = tree.nearest_neighbour(Point(3, p1_values));
    std::cout << *p << std::endl;

    return 0;
}
