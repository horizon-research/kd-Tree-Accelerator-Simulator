class Point:
    def __init__(self, values_in):
        self.values = [float(val) for val in values_in]

    def dimension(self):
        return len(self.values)

    def distance(self, p):
        sum = 0
        for i in range(len(self.values)):
            diff = self.values[i] - p.values[i]
            sum += diff**2
        return sum

    def dim_value(self, dim):
        return self.values[dim]

    def __str__(self):
        s = ''
        for val in self.values:
            s += str(val) + ' '
        return s
        
    __repr__ = __str__