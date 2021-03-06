#include "Point.h"

Point::Point(int num_dimensions_in, float values_in[]) {
    num_dimensions = num_dimensions_in;
    
    dimension_values = new float[num_dimensions];
    for (int i = 0; i < num_dimensions; i++) {
        dimension_values[i] = values_in[i];
    }
}
int Point::get_size() const {
    return num_dimensions;
}
float Point::dimension_value(int d) const{
    if (d >= num_dimensions) {
        return -1;
    }
    return dimension_values[d];
}
//Calculates distance by find sqaure root of the sum of the squares of the differences
float Point::distance(Point* p) {
    int sum = 0;
    for (int i = 0; i < num_dimensions; i++) {
        float difference = dimension_value(i) - p->dimension_value(i);
        sum += pow(difference, 2);
    }
    return sqrt(sum);
}
Point* Point::copy() {
    float values_copy[num_dimensions];
    for (int i = 0; i < num_dimensions; i++) {
        values_copy[i] = dimension_value(i);
    }
    return new Point(num_dimensions, values_copy);
}
std::ostream& operator<<(std::ostream& os, const Point& p) {
    os << "[";
    for (int i = 0; i < p.num_dimensions - 1; i++) {
        os << p.dimension_values[i] << " ";
    }
    os << p.dimension_values[p.num_dimensions - 1] << "]";
    return os;
}
Point& Point::operator=(const Point& p) {
    num_dimensions = p.get_size();
    for (int i = 0; i < num_dimensions; i++) {
        dimension_values[i] = p.dimension_value(i);
    }
    return *this;
}

Point::~Point() {
    delete[] dimension_values;
}
