from collections import deque



#Class representing indivudal query, contains list of instructions to be processed, as well as all current dependencies
class Query:
    def __init__(self):
        #self.instructions = []
        self.instructions = deque()
        self.length = 0
        self.stalled = False
        self.backtrack = False

    #Adds instruction tuple to list
    def add(self, instruction):
        self.instructions.append(instruction)
        self.length += 1


    #There are no more instructions to process
    def finished(self):
        return not self.instructions
        
    #Removes instruction from top of list and returns it
    def next_instruction(self):
        if self.instructions:
            if not self.stalled:
                self.current_instruction = self.instructions.popleft()
        else:
            return "?"
        
            
