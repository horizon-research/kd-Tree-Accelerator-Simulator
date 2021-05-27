#ifndef Point_H
#define Point_H
#include <iostream>
#include <stdlib.h>
#include <math.h>
//Point class which supports points of an dimension
class Point {
    private:
        int num_dimensions;
        int* dimension_values;
    public:
        Point(int num_dimensions_in, int values_in[]);
        Point() = default;
        int get_size();
        int dimension_value(int d);
        ~Point();
        double distance(Point* p);
        Point copy();
        friend std::ostream& operator<<(std::ostream& os, const Point& p);

    };
#endif