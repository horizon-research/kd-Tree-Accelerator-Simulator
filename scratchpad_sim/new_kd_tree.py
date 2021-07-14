import heapq
from query import Query
from point import Point
import time
from collections import deque
#Constants which make trace writes more readable
data_sizes = [16, 24, 16, 24, 40, 24]

READ = 0
WRITE = 1

POINT = 0
NODE = 1
TOPTREE_POINT = 3
TOPTREE_NODE = 4
QUERY = 3
STACK = 5

X = 0
Y = 4
Z = 8

P = 0
LEFT = 8
RIGHT = 16

#Represents 3d kd-Tree data structure, creates well balanced tree from inputted points
class KD_Tree:  
    
    #Constructs kd-Tree and initializes tracing information
    def __init__(self, data_in):
        self.num_dimensions = 3
        self.num_toptree_nodes = 0
        self.num_nodes = 0
        self.num_subtrees = 0
        self.root = None
        file = open(data_in)
        lines = file.readlines()
        points = []

        #Data indices saved for address calculation
        self.memory = None
        self.stack = []
        self.subtree_roots = {}
        self.node_indices = {}
        self.toptree_node_indices = {}
        self.toptree_point_indices = {}

        
        self.point_indices = {}
        self.query_trace = None
        self.split = False
        self.memory = None
        #Array of points constructed from input file
        for line in lines:
            tokens = line.split()
            p = Point([float(tokens[0]), float(tokens[1]), float(tokens[2])])
            points.append(p)
        self.memory_ptrs = [0, 0, 0, 0]
        #Well balanced tree created from points
        self.root = self.build_tree(points, 0, len(points) - 1, 0)
        self.toptree_levels = 2
       
        self.assign_toptree(self.root, 0, self.toptree_levels)
        self.tree_depth = self.depth(self.root, 0)
        self.subtree_size = (2 ** (self.tree_depth - self.toptree_levels) - 1)
        self.toptree_size = (2 ** self.toptree_levels) - 1
        #self.print_tree()

    

    #Recursivley builds tree by selecting median points from each dimension
    def build_tree(self, points, lo, hi, level):
        if lo <= hi:
            #Median for sublist is found
            median = int((lo + hi) / 2)
            #Dimension to sort on
            dim = level % 3
            #Sublist is sorted based on current dimension
            points[lo:hi + 1] = sorted(points[lo:hi + 1], key=lambda p: p.values[dim])
            #Median point is inserted into tree
            p = points[median]
            n = Node(p)
            #self.point_indices[p] = self.num_nodes
            #self.node_indices[n] = self.num_nodes
            #self.num_nodes += 1
            #Function called recursivley to all points to the left and right of the median in the sublist, sorting dimension is incremented
            n.left = self.build_tree(points, lo, median - 1, level + 1)
            n.right = self.build_tree(points, median + 1, hi, level + 1)
            return n
        else:
            return None
    
    def assign_toptree(self, tree, level, top_level):
        if level == top_level:
            self.num_nodes = 0
            self.subtree_roots[tree] = self.num_subtrees
            self.assign_subtree(tree)
            self.num_subtrees += 1
        else:
            self.toptree_node_indices[tree] = self.num_toptree_nodes
            self.toptree_point_indices[tree.p] = self.num_toptree_nodes
            self.num_toptree_nodes += 1

            self.assign_toptree(tree.left, level + 1, top_level)
            self.assign_toptree(tree.right, level + 1, top_level)
    def assign_subtree(self, tree):
        if tree:
            self.node_indices[tree] = self.num_nodes
            self.point_indices[tree.p] = self.num_nodes
            self.num_nodes += 1
            self.assign_subtree(tree.left)
            self.assign_subtree(tree.right)


    def depth(self, tree, level):
        if tree:
            left_depth = self.depth(tree.left, level + 1)
            right_depth = self.depth(tree.right, level + 1)
            return left_depth if left_depth > right_depth else right_depth
        else:
            return level

    #Prints tree
    def print_tree(self):
        self.print_tree_rec(self.root, 0, True)

    #Recursively prints tree, insert padding based on the current nodes level in the tree
    def print_tree_rec(self, tree, level, sub):
        time.sleep(0.01)
        if tree:
            for i in range(level):
                print("  ", end='')
            if level >= self.toptree_levels and sub:
                index = self.point_indices[tree.p]
            else:
                index = self.toptree_point_indices[tree.p]
            print(f'{tree.p} {index}')
            self.print_tree_rec(tree.left, level + 1, sub)
            self.print_tree_rec(tree.right, level + 1, sub)

    #k nearest-neighbour search
    def knn(self, query, k):
        #Stack is initialized to track recursive calls
        self.stack = []
        self.stack.append(0)
        current_best = []
        #Recursive function modifies current best, when finished, it will contain the k nearest points in the tree, and their distances from the query point
        self.knn_rec(query, current_best, k, self.root, 0)
        self.backtrack()
        return current_best

    #Traverses down path as if the target point were being inserted in the tree, 
    #if any point encountered along the way is closer than the current closest point,
    #that point is then set to be closest point
    def knn_rec(self, query, current_best, k, tree, level):
        
        call = self.stack[-1]
        #RS
        self.access(READ, STACK, call, 0) #Query
        
        self.computation(1)
        if tree:
            #RN
            self.access(READ, NODE, self.node_indices[tree], 0)

            #RP
            self.access(READ, POINT, self.point_indices[tree.p], 0)

            #CD
            splitting_plane = level % self.num_dimensions

            #Values found for current point and target point
            query_val = query.dim_value(splitting_plane)
            current_val = tree.p.dim_value(splitting_plane)

            #Current point's distance to query found
            
            #Distance stored as negative to convert heap to max heap
            self.computation(18)
            distance = -query.distance(tree.p)
            current = (distance, tree.p)

            #If there are already k points in heap, add current point only if its distance is less than the farthest away point in heap
            self.computation(4)
            if len(current_best) == k:
                if distance > current_best[0][0]:
                    heapq.heapreplace(current_best, current)
            #Otherwise, add
            else:
                heapq.heappush(current_best, current)
            self.computation(2)
            if tree.right == None and tree.left == None:
                self.backtrack()
                self.access(READ, STACK, self.stack.pop(), 32)
                
                return

            #NT 
            #If target value is less than current, take left subtree
            self.computation(2)
            if  query_val < current_val:
                self.stack.append(call + 1)
                self.access(WRITE, STACK, call + 1, 0)

                self.computation(1)
                self.knn_rec(query, current_best, k, tree.left, level + 1)

                #BT
                #If the current best distance + the target value is greater than the current value,
                #it is possible that the closest point could be contained in right subtree, so it is searched as well
                self.computation(6)
                if (query_val + current_best[0][0] > current_val or k > len(current_best)):
                    self.stack.append(call + 1)
                    self.access(WRITE, STACK, call + 1, 0)
                    self.backtrack()
                    self.knn_rec(query, current_best, k, tree.right, level + 1)
                
            #If target value is greater than current, take right subtree
            else:
                self.stack.append(call + 1)
                self.access(WRITE, STACK, call + 1, 0)
                self.computation(1)
                self.knn_rec(query, current_best, k, tree.right, level + 1)

                #BT
                #If the target value - the current best distance is less than than the current value,
                #it is possible that the closest point could be contained in the left subtree, so it is searched as well
                self.computation(6)
                if (query_val - current_best[0][0] < current_val or k > len(current_best)):
                    self.stack.append(call + 1)
                    self.access(WRITE, STACK, call + 1, 0)
                    self.backtrack()
                    self.knn_rec(query, current_best, k, tree.left, level + 1)
        else:
            self.backtrack()
        self.access(READ, STACK, self.stack.pop(), 32)
        


    #Computes address for given address based on data type, data index, and offset, and writes it to the trace in a tuple
    def access(self, access_type, data_type, index, offset):
        address = self.memory.address(data_type, index, offset)
        if not self.split:
            address += self.memory_ptrs[data_type]
        self.query_trace.add(("R", data_type, address))

    #Adds desired number of non access instructions to trace
    def computation(self, num):
        for _ in range(num):
            self.query_trace.add("C")
    def backtrack(self):
        self.query_trace.add("BT")
    def insert(self, subtree):
        self.query_trace.add(("SUB", subtree))
    def load(self, subtree):
        self.query_trace.add(("L", subtree))



    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #k nearest-neighbour search
    def knn_top(self, query, k):
        #Stack is initialized to track recursive calls
        self.stack = []
        self.stack.append(0)
        current_best = []
        #Recursive function modifies current best, when finished, it will contain the k nearest points in the tree, and their distances from the query point
        self.knn_top_rec(query, current_best, k, self.root, 0)
        return current_best

    #Traverses down path as if the target point were being inserted in the tree, 
    #if any point encountered along the way is closer than the current closest point,
    #that point is then set to be closest point
    def knn_top_rec(self, query, current_best, k, tree, level):
        call = self.stack[-1]
        #RS
        self.access(READ, STACK, call, 0) #Query
        #print(tree.p)
        #print(query)
        self.computation(1)
        if tree:
            #RN
            if level == self.toptree_levels:
                subtree_num = self.subtree_roots[tree]
                self.insert(subtree_num)
                self.knn_rec(query, current_best, k, tree, level)
                return
            self.access(READ, TOPTREE_NODE, self.toptree_node_indices[tree], 0)

            #RP
            self.access(READ, TOPTREE_POINT, self.toptree_point_indices[tree.p], 0)

            #CD
            splitting_plane = level % self.num_dimensions

            #Values found for current point and target point
            query_val = query.dim_value(splitting_plane)
            current_val = tree.p.dim_value(splitting_plane)

            #Current point's distance to query found
            
            #Distance stored as negative to convert heap to max heap
            self.computation(18)
            distance = -query.distance(tree.p)
            current = (distance, tree.p)

            #If there are already k points in heap, add current point only if its distance is less than the farthest away point in heap
            self.computation(4)
            if len(current_best) == k:
                if distance > current_best[0][0]:
                    heapq.heapreplace(current_best, current)
            #Otherwise, add
            else:
                heapq.heappush(current_best, current)
            self.computation(2)
            

            #NT 
            #If target value is less than current, take left subtree
            self.computation(2)
            if  query_val < current_val:
                self.stack.append(call + 1)
                self.access(WRITE, STACK, call + 1, 0)

                self.computation(1)
                self.knn_top_rec(query, current_best, k, tree.left, level + 1)

                #BT
                #If the current best distance + the target value is greater than the current value,
                #it is possible that the closest point could be contained in right subtree, so it is searched as well
                
                
            #If target value is greater than current, take right subtree
            else:
                self.stack.append(call + 1)
                self.access(WRITE, STACK, call + 1, 0)
                self.computation(1)
                self.knn_top_rec(query, current_best, k, tree.right, level + 1)

                #BT
                #If the target value - the current best distance is less than than the current value,
                #it is possible that the closest point could be contained in the left subtree, so it is searched as well
                
        
        


#Internal node class
class Node:
        def __init__(self, p):
            self.left = None
            self.right = None
            self.p = p


#tree = KD_Tree("../kdTree_Inputs/test")
#tree.query_trace = Query()
#p = Point([24, 0, 1])
#print(tree.knn(p, 2))

