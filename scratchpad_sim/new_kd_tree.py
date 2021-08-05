import heapq
from query import Query
from point import Point
import time
from collections import deque
from memory import Memory, Scratchpad
#Constants which make trace writes more readable
data_sizes = [40, 40, 64]

READ = 0
WRITE = 1

POINT = 0
TOPTREE_POINT = 1
QUERY = 2

X = 0
Y = 4
Z = 8

P = 0
LEFT = 8
RIGHT = 16

#Represents 3d kd-Tree data structure, creates well balanced tree from inputted points
class KD_Tree:  
    
    #Constructs kd-Tree and initializes tracing information
    def __init__(self, data_in, num_levels, approximation):
        self.num_dimensions = 3
        self.num_toptree_nodes = 0
        self.num_nodes = 0
        self.num_subtrees = 0
        self.root = None
        file = open(data_in)
        lines = file.readlines()
        self.points = []
        #Data indices saved for address calculation
        self.memory = None
        self.stack = []
        self.subtree_roots = {}
        self.toptree_point_indices = {}

        
        self.point_indices = {}
        self.query_trace = None
        self.split = False
        self.memory = None
        #Array of points constructed from input file
        for line in lines:
            tokens = line.split()
            p = Point([float(tokens[0]), float(tokens[1]), float(tokens[2])])
            self.points.append(p)
        self.memory_ptrs = [0, 0, 0, 0]
        #Well balanced tree created from points
        self.root = self.build_tree(self.points, 0, len(self.points) - 1, 0)
        self.toptree_levels = num_levels
        self.approximation = approximation
        self.terminate_distance = -5
        self.assign_toptree(self.root, 0, self.toptree_levels)
        self.tree_depth = self.depth(self.root, 0)
        self.subtree_size = (2 ** (self.tree_depth - self.toptree_levels) - 1)
        self.toptree_size = (2 ** self.toptree_levels) - 1
        #self.print_tree()
    
    def size(self, tree):
        if tree:
            return 1 + self.size(tree.right) + self.size(tree.left)
        else:
            return 0
    

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
    #Assigns nodes in the toptree to indices
    def assign_toptree(self, tree, level, top_level):
        if level == top_level:
            self.num_nodes = 0
            self.subtree_roots[tree] = self.num_subtrees
            self.assign_subtree(tree)
            self.num_subtrees += 1
        else:
            self.toptree_point_indices[tree.p] = self.num_toptree_nodes
            self.num_toptree_nodes += 1

            self.assign_toptree(tree.left, level + 1, top_level)
            self.assign_toptree(tree.right, level + 1, top_level)

    #Assigns nodes in the given subtree to indices
    def assign_subtree(self, tree):
        if tree:
            self.point_indices[tree.p] = self.num_nodes
            self.num_nodes += 1
            self.assign_subtree(tree.left)
            self.assign_subtree(tree.right)

    #Finds depth of tree
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
        self.access(READ, QUERY, call, 0) 
        
        self.computation(1)
        if tree and not (self.approximation == 1 and current_best[0][0] > self.terminate_distance):

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
                self.access(READ, QUERY, self.stack.pop(), 32)
                
                return

            #NT 
            #If target value is less than current, take left subtree
            self.computation(2)
            if  query_val < current_val:
                self.stack.append(call + 1)
                self.access(WRITE, QUERY, call + 1, 0)
                self.computation(1)
                self.knn_rec(query, current_best, k, tree.left, level + 1)

                #BT
                #If the current best distance + the target value is greater than the current value,
                #it is possible that the closest point could be contained in right subtree, so it is searched as well
                if self.approximation != 0:
                    self.computation(6)
                    if query_val + -(current_best[0][0]) > current_val:
                        self.stack.append(call + 1)
                        self.access(WRITE, QUERY, call + 1, 0)
                        self.knn_rec(query, current_best, k, tree.right, level + 1)
                        self.backtrack()

                
            #If target value is greater than current, take right subtree
            else:
                self.stack.append(call + 1)
                self.access(WRITE, QUERY, call + 1, 0)
                self.computation(1)
                self.knn_rec(query, current_best, k, tree.right, level + 1)

                #BT
                #If the target value - the current best distance is less than than the current value,
                #it is possible that the closest point could be contained in the left subtree, so it is searched as well
                if self.approximation != 0:
                    self.computation(6)
                    if query_val - -(current_best[0][0]) < current_val:
                        self.stack.append(call + 1)
                        self.access(WRITE, QUERY, call + 1, 0)
                        self.knn_rec(query, current_best, k, tree.left, level + 1)
                        self.backtrack()

        else:
            self.backtrack()
        self.access(READ, QUERY, self.stack.pop(), 32)
        


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
        self.access(READ, QUERY, call, 0) #Query
        #print(tree.p)
        #print(query)
        self.computation(1)
        if tree:
            if level == self.toptree_levels:
                subtree_num = self.subtree_roots[tree]
                self.insert(subtree_num)
                self.knn_rec(query, current_best, k, tree, level)
                return

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
                self.access(WRITE, QUERY, call + 1, 0)

                self.computation(1)
                self.knn_top_rec(query, current_best, k, tree.left, level + 1)

                #BT
                #If the current best distance + the target value is greater than the current value,
                #it is possible that the closest point could be contained in right subtree, so it is searched as well
                
                
            #If target value is greater than current, take right subtree
            else:
                self.stack.append(call + 1)
                self.access(WRITE, QUERY, call + 1, 0)
                self.computation(1)
                self.knn_top_rec(query, current_best, k, tree.right, level + 1)

                #BT
                #If the target value - the current best distance is less than than the current value,
                #it is possible that the closest point could be contained in the left subtree, so it is searched as well
                
        
         #k nearest-neighbour search
    def knn_ideal(self, query, k):
        #Stack is initialized to track recursive calls
        current_best = []
        #Recursive function modifies current best, when finished, it will contain the k nearest points in the tree, and their distances from the query point
        self.knn_ideal_rec(query, current_best, k, self.root, 0)
        return current_best

    #Traverses down path as if the target point were being inserted in the tree, 
    #if any point encountered along the way is closer than the current closest point,
    #that point is then set to be closest point
    def knn_ideal_rec(self, query, current_best, k, tree, level):
        if tree:
            splitting_plane = level % self.num_dimensions

            #Values found for current point and target point
            query_val = query.dim_value(splitting_plane)
            current_val = tree.p.dim_value(splitting_plane)

            #Current point's distance to query found
            
            #Distance stored as negative to convert heap to max heap
            distance = -query.distance(tree.p)
            current = (distance, tree.p)

            #If there are already k points in heap, add current point only if its distance is less than the farthest away point in heap
            if len(current_best) == k:
                if distance > current_best[0][0]:
                    heapq.heapreplace(current_best, current)
            #Otherwise, add
            else:
                heapq.heappush(current_best, current)
            if tree.right == None and tree.left == None:
                return

            #If target value is less than current, take left subtree
            if  query_val < current_val:

                self.knn_ideal_rec(query, current_best, k, tree.left, level + 1)

                #BT
                #If the current best distance + the target value is greater than the current value,
                #it is possible that the closest point could be contained in right subtree, so it is searched as well
                if (query_val + -(current_best[0][0]) > current_val or k > len(current_best)):
                    self.knn_ideal_rec(query, current_best, k, tree.right, level + 1)
                
            #If target value is greater than current, take right subtree
            else:
                self.knn_ideal_rec(query, current_best, k, tree.right, level + 1)
                #If the target value - the current best distance is less than than the current value,
                #it is possible that the closest point could be contained in the left subtree, so it is searched as well
                if (query_val - -(current_best[0][0]) < current_val or k > len(current_best)):
                    self.knn_ideal_rec(query, current_best, k, tree.left, level + 1)
        

class Bucket_KD_Tree:
    def insert(self, tree, p, level):
        if level == self.levels:
            self.buckets[tree].append(p)
            self.point_indices[p] = self.num_points
            self.num_points += 1
        else:
            dimension = level % 3
            if tree.p.dim_value(dimension) > p.dim_value(dimension):
                self.insert(tree.left, p, level + 1)
            else:
                self.insert(tree.right, p, level + 1)
    def __init__(self, data_in, levels):
        file = open(data_in)
        lines = file.readlines()
        points = []
        self.point_indices = {}
        self.toptree_point_indices = {}
        self.memory = None
        self.num_points = 0
        self.toptree_size = 0
        self.levels = levels
        self.buckets = {}
        self.split = False
        self.memory_ptrs = [0, 0, 0, 0]
        self.query_trace = Query()
        self.num_dimensions = 3
        self.approximation = -1
        for line in lines:
            tokens = line.split()
            p = Point(tokens[0:3])
            points.append(p)
        self.root = self.build_toptree(points, 0, len(points) - 1, 0, levels)
        for p in points:
            self.insert(self.root, p, 0)
        #self.print_tree_rec(self.root, 0, False)
        for b in self.buckets:
            print(len(self.buckets[b]))
    def build_toptree(self, points, lo, hi, level, max):
        #Median for sublist is found
        median = int((lo + hi) / 2)
        #Dimension to sort on
        dim = level % 3
        #Sublist is sorted based on current dimension
        points[lo:hi + 1] = sorted(points[lo:hi + 1], key=lambda p: p.values[dim])
        #Median point is inserted into tree
        p = points[median]
        n = Node(p)
        self.toptree_point_indices[n] = self.toptree_size
        self.toptree_size += 1
        if level < max:
            #Function called recursivley to all points to the left and right of the median in the sublist, sorting dimension is incremented
            n.left = self.build_toptree(points, lo, median - 1, level + 1, max)
            n.right = self.build_toptree(points, median + 1, hi, level + 1, max)
            return n
        else:
            self.buckets[n] = []
            return n
    
    def print_tree_rec(self, tree, level, sub):
        time.sleep(0.01)
        if tree.left == None and tree.right == None:
            
            for i in range(level):
                print("  ", end='')
            for p in self.buckets[tree]:
                print(p, end=' ')
            print()
            
        else:
            for i in range(level):
                print("  ", end='')
            
            print(tree.p)
            self.print_tree_rec(tree.left, level + 1, sub)
            self.print_tree_rec(tree.right, level + 1, sub)
    def knn(self, query, k):
        #Stack is initialized to track recursive calls
        self.stack = []
        self.stack.append(0)
        current_best = []
        #Recursive function modifies current best, when finished, it will contain the k nearest points in the tree, and their distances from the query point
        self.knn_rec(query, current_best, k, self.root, 0)
        return current_best
    def knn_rec(self, query, current_best, k, tree, level):
        
        call = self.stack[-1]
        #RS
        self.access(READ, QUERY, call, 0) 
        
        self.computation(1)
        if tree:
            self.computation(2)
            if tree in self.buckets:
                self.exhaustive_search(query, current_best, self.buckets[tree], k)
                return
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
                self.access(READ, QUERY, self.stack.pop(), 32)
                
                return

            #NT 
            #If target value is less than current, take left subtree
            self.computation(2)
            if  query_val < current_val:
                self.stack.append(call + 1)
                self.access(WRITE, QUERY, call + 1, 0)
                self.computation(1)
                self.knn_rec(query, current_best, k, tree.left, level + 1)

             
            #If target value is greater than current, take right subtree
            else:
                self.stack.append(call + 1)
                self.access(WRITE, QUERY, call + 1, 0)
                self.computation(1)
                self.knn_rec(query, current_best, k, tree.right, level + 1)

               
        else:
            self.backtrack()
        self.access(READ, QUERY, self.stack.pop(), 32)
        
    def exhaustive_search(self, query, current_best, bucket, k):
        for p in bucket:
            self.access(READ, POINT, self.point_indices[p], 0)
            self.computation(18)
            distance = -p.distance(query)
            self.computation(4)
            if len(current_best) == k:
                if current_best[0][0] < distance:
                    heapq.heapreplace(current_best, (distance, p))
            else:
                heapq.heappush(current_best, (distance, p))
            
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
    
    def load(self, subtree):
        self.query_trace.add(("L", subtree))


#Internal node class
class Node:
        def __init__(self, p):
            self.left = None
            self.right = None
            self.p = p


tree = Bucket_KD_Tree("../kdTree_Inputs/frame_16", 3)
tree.memory = Memory(True, [Scratchpad(5000, 8)], None)
print(tree.knn(Point([0,0,0]), 2))
