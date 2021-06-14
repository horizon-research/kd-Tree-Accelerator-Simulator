import queue
class Query:
    def __init__(self):
        self.instructions = []
        self.dependencies = set()
        self.length = 0
    def add(self, instruction):
        self.instructions.append(instruction)
        self.length += 1
    def add_dependency(self, dep):
        self.dependencies.add(dep)
    def num_dependencies(self):
        return len(self.dependencies)
    def remove_dependency(self, dep):
        self.dependencies.discard(dep)
    def finished(self):
        return len(self.instructions) == 0
    def next_instruction(self):
        return self.instructions.pop(0)
            
