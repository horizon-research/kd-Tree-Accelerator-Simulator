/*
 * Gunnar Hammonds
 * Basic implementation of Kd tree as well as nearest neighbour search
 */


#include "KD_Tree.h"
#include <fstream> 
#include <vector>
using namespace std;
int main(int argc, char* argv[]) {
 

    if (argc != 4) {
        cout << "Invalid number of arguments\n";
        return 1;
    }
    std::string file_name = argv[3];
    KD_Tree tree(argv[1]);
    ifstream fin("../Search_Inputs/" + string(argv[2]));
    if (fin.is_open()) {
        string line;
        float value;
        //kd-tree dimension found
        getline(fin, line);
        int num_dimensions = stoi(line);
        if (num_dimensions != tree.get_num_dimensions()) {
            cout << "Tree and Search dimensions do not match" << endl;
            exit(0);
        }
        //Each line of file is read
        int query_num = 0;
        while (getline(fin, line)) {
            ofstream fout;
            fout.open("../Trace_Files/" + file_name + "_" + to_string(query_num));
            tree.memory->set_fout(&fout);
            istringstream sin(line);
            string query_type;
            sin >> query_type;
            float values[num_dimensions];
            if (query_type == "RANGE") {
                float range[3][2];
                sin >> range[0][0] >> range[0][1] 
                    >> range[1][0] >> range[1][1] 
                    >> range[2][0] >> range[2][1];  
                vector<Point*> points = tree.range_search(range);
                for (auto p : points) {
                    cout << *p << endl;
                }   
            }
            else {
                for (int i = 0; i < num_dimensions; i++) {
                    sin >> value;
                    values[i] = value;
                }
                Point query(num_dimensions, values);
                if (query_type == "KNN") {
                    int k;
                    sin >> k;
                    vector<Point*> points = tree.knn_search(query, k);
                    for (auto p : points) {
                        cout << *p << endl;
                    }
                }
                else {
                    Point* p = tree.nearest_neighbour(query);
                    cout << *p << endl;
                }
            } 
            query_num++;
        }
    }
    else {
        cout << "Error opening file: " << argv[2] << endl;
        exit(0);
    }
    return 0;
}
