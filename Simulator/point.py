#Class representing point in space
class Point:
    def __init__(self, values_in):
        self.values = [float(val) for val in values_in]

    def dimension(self):
        return len(self.values)

    #Returns square of distance
    def distance(self, p):
        sum = 0
        for i in range(len(self.values)):
            diff = self.values[i] - p.values[i]
            sum += diff**2
        return sum
        
    #valuef for given dimensiona
    def dim_value(self, dim):
        return self.values[dim]

    #Resolves edge case in knn search where two points are equal distance from query, the point which is chosen doesn't really matter
    def __gt__(self, p2):
        return self
    def __eq__(self, p2):
        for v1, v2 in zip(self.values, p2.values):
            if v1 != v2:
                return False
            else:
                return True

    def __hash__(self):
        return id(self)
    def __str__(self):
        s = ''
        for val in self.values:
            s += str(val) + ' '
        return s
        
    __repr__ = __str__