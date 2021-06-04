#ifndef Point_H
#define Point_H
#include <iostream>
#include <stdlib.h>
#include <math.h>
//Point class which supports points of an dimension
class Point {
    private:
        int num_dimensions;
        float* dimension_values;
    public:
        Point(int num_dimensions_in, float values_in[]);
        Point() = default;
        int get_size() const;
        float dimension_value(int d) const;
        ~Point();
        float distance(Point* p);
        Point* copy();
        friend std::ostream& operator<<(std::ostream& os, const Point& p);
        Point& operator=(const Point& p);


    };
#endif