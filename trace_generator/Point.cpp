#include "Point.h"

Point::Point(int num_dimensions_in, int values_in[]) {
    num_dimensions = num_dimensions_in;
    
    dimension_values = new int[num_dimensions];
    for (int i = 0; i < num_dimensions; i++) {
        dimension_values[i] = values_in[i];
    }
}
int Point::get_size() {
    return num_dimensions;
}
int Point::dimension_value(int d) {
    if (d >= num_dimensions) {
        return -1;
    }
    return dimension_values[d];
}
//Calculates distance by find sqaure root of the sum of the squares of the differences
double Point::distance(Point* p) {
    int sum = 0;
    for (int i = 0; i < num_dimensions; i++) {
        int difference = dimension_value(i) - p->dimension_value(i);
        sum += pow(difference, 2);
    }
    return sqrt(sum);
}
std::ostream& operator<<(std::ostream& os, const Point& p) {
    os << "[";
    for (int i = 0; i < p.num_dimensions - 1; i++) {
        os << p.dimension_values[i] << " ";
    }
    os << p.dimension_values[p.num_dimensions - 1] << "]";
    return os;
}
Point::~Point() {
    delete[] dimension_values;
}
