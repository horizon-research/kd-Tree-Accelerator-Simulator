#Class representing indivudal query, contains list of instructions to be processed, as well as all current dependencies
class Query:
    def __init__(self):
        self.instructions = []
        self.length = 0
        self.stalled = False
        self.backtrack = False

    #Adds instruction tuple to list
    def add(self, instruction):
        self.instructions.append(instruction)
        self.length += 1

    #Adds dependency to set
    def add_dependency(self, dep):
        self.dependencies.add(dep)

    def num_dependencies(self):
        return len(self.dependencies)

    #Removes processed depency from list
    def remove_dependency(self, dep):
        self.dependencies.discard(dep)

    #There are no more instructions to process
    def finished(self):
        return not self.instructions
        
    #Removes instruction from top of list and returns it
    def next_instruction(self):
        if self.instructions:
            if not self.stalled:
                self.current_instruction = self.instructions.pop(0)
        else:
            return "?"
        
            
