import queue
class Query:
    def __init__(self):
        self.traces = []
        self.dependencies = set()
        self.current_line = 0
    def add(self, instruction):
        self.traces.append(instruction)
    
            
