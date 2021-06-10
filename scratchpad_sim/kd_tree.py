import numpy as np
import heapq
from query import Query
from point import Point
data_sizes = [16, 24, 32]
READ = 0
WRITE = 1

POINT = 0
NODE = 1
STACK = 2
END = 3
X = 0
Y = 1
Z = 2

P = 0
LEFT = 1
RIGHT = 2

class KD_Tree:  
    

    def __init__(self, data_in):
        self.num_dimensions = 3
        self.num_nodes = 0
        self.root = None
        file = open(data_in)
        lines = file.readlines()
        points = []

        
        self.stack = []
        self.node_indices = {}
        self.point_indices = {}
        self.query_trace = None

        for line in lines:
            tokens = line.split()
            p = Point([float(tokens[0]), float(tokens[1]), float(tokens[2])])
            points.append(p)
        self.build_tree(points, 0, len(points) - 1, 0)
        self.memory_ptrs = [0, 0, 0, 0]
        self.memory_ptrs[NODE] = data_sizes[POINT] * (self.num_nodes + 1)
        self.memory_ptrs[STACK] =self.memory_ptrs[NODE] + (data_sizes[NODE] *self.num_nodes)
        self.memory_ptrs[END] =self.memory_ptrs[STACK] + (data_sizes[STACK] *self.num_nodes)



        


    def build_tree(self, points, lo, hi, level):
        if lo <= hi:
            median = int((lo + hi) / 2)
            dim = level % 3
            points[lo:hi + 1] = sorted(points[lo:hi + 1], key=lambda p: p.values[dim])
            p = points[median]
            self.insert(p)
            self.build_tree(points, lo, median - 1, level + 1)
            self.build_tree(points, median + 1, hi, level + 1)


    def insert(self, p):
        self.root = self.insert_rec(p, self.root, 0)

    def insert_rec(self, p, tree, level):
        if tree is None:
            self.point_indices[p] = self.num_nodes
            self.node_indices[tree] = self.num_nodes
            self.num_nodes += 1
            return Node(p)
        else:
            splitting_plane = level % 3
            if p.dim_value(splitting_plane) < tree.p.dim_value(splitting_plane):
                tree.left = self.insert_rec(p, tree.left, level + 1)
            else:
                tree.right = self.insert_rec(p, tree.right, level + 1)
            return tree
    def print_tree(self):
        self.print_tree_rec(self.root, 0)

    def print_tree_rec(self, tree, level):
        if tree:
            for i in range(level):
                print("  ", end='')
            print(tree.p)
            self.print_tree_rec(tree.left, level + 1)
            self.print_tree_rec(tree.right, level + 1)

    def knn(self, query, k):
        self.stack = []
        self.stack.append(0)
        current_best = []
        self.knn_rec(query, current_best, k, self.root, 0)
        return current_best


    def knn_rec(self, query, current_best, k, tree, level):
        call = self.stack[-1]
        self.access(READ, STACK, call, 16)
        if tree:
            self.access(READ, STACK, call, 24)
            self.computation(1)
            splitting_plane = level % self.num_dimensions

            query_val = query.dim_value(splitting_plane)
            current_val = tree.p.dim_value(splitting_plane)

            self.write_distance(tree.p, query)
            distance = -query.distance(tree.p)
            current = (distance, tree.p)

            if len(current_best) == k:
                if distance < current_best[0][0]:
                    heapq.heapreplace(current_best, current)
            else:
                heapq.heappush(current_best, current)
                
            self.access(READ, POINT, self.num_nodes, 0)
            self.access(READ, POINT, self.point_indices[tree.p], 0)
            self.computation(1)
            if  query_val < current_val:
                self.stack.append(call + 1)
                self.computation(1)
                self.knn_rec(query, current_best, k, tree.left, level + 1)

                self.access(READ, POINT, self.num_nodes, 0)
                self.access(READ, POINT, self.point_indices[tree.p], 0)
                self.computation(2)
                if (query_val + current_best[0][0] > current_val or k > len(current_best)):
                    self.stack.append(call + 1)
                    self.computation(1)
                    self.knn_rec(query, current_best, k, tree.right, level + 1)
            else:
                self.stack.append(call + 1)
                self.computation(1)
                self.knn_rec(query, current_best, k, tree.right, level + 1)

                self.access(READ, POINT, self.num_nodes, 0)
                self.access(READ, POINT, self.point_indices[tree.p], 0)
                self.computation(2)
                if (query_val - current_best[0][0] < current_val or k > len(current_best)):
                    self.stack.append(call + 1)
                    self.computation(1)
                    self.knn_rec(query, current_best, k, tree.left, level + 1)

        self.access(READ, STACK, self.stack.pop(), 32)

    def access(self, access_type, data_type, index, offset):
        address = self.memory_ptrs[data_type] + (data_sizes[data_type] * index) + offset
        self.query_trace.add(("R", data_type, address))

    def computation(self, num):
        for _ in range(num):
            self.query_trace.add("I")
    def write_distance(self, p1, p2):
        self.access(READ, POINT, self.point_indices[p1], X)
        self.access(READ, POINT, self.num_nodes, X)
        self.computation(6)

        self.access(READ, POINT, self.point_indices[p1], Y)
        self.access(READ, POINT, self.num_nodes, Y)
        self.computation(6)

        self.access(READ, POINT, self.point_indices[p1], Z)
        self.access(READ, POINT, self.num_nodes, Z)
        self.computation(8)
    

    #def build_tree():    


class Node:
        def __init__(self, p):
            self.left = None
            self.right = None
            self.p = p

tree = KD_Tree("test")
tree.print_tree()
tree.query_trace = Query()
print(tree.knn(Point([1,1,1]), 2))
print(tree.query_trace.traces)