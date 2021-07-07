#Processing Engine class, contains Pe's current status, as well as thw query it's currently assigned to
from os import pipe


class PE:
    def __init__(self, pipeline_size, backtrack_pipeline_size):
        self.stalled = False
        self.query = None
        self.busy = False
        self.lines_processed = 0
        self.pipeline_size = pipeline_size
        self.pipeline = [None for i in range(self.pipeline_size)]
        self.backtrack_pipeline_size = backtrack_pipeline_size
        self.backtrack_pipeline = [None for i in range(self.backtrack_pipeline_size)]
    #Manages all queries currently in pipeline, processing their instrucitons for this cycle, and moving them through the pipeline if a stall hasn't occured
    def manage_pipeline(self, sim):
        
        #Iterates through queries in pipeline, starting with query closest to finish
        for stage in range(self.pipeline_size - 1, -1, -1):
            query_at_stage = self.pipeline[stage]
            if query_at_stage:
                #Instruction is processed
                self.process_line(sim, query_at_stage, sim.ideal)
                #If the query has not stalled, it can be advacned to the next stage of the pipeline
                if not query_at_stage.stalled:
                    #The the query has been completely finished it can be fully removed
                    if sim.query_to_queue(self, query_at_stage, stage):
                        self.pipeline[stage] = None
                    #Otherwise, if the next stage of the pipeline is empty, i.e the next query being processed hasn't stalled, the query can be moved forward in the queue
                    elif self.pipeline[stage + 1] is None:
                        self.pipeline[stage] = None
                        self.pipeline[stage + 1] = query_at_stage
                    
                else:
                    sim.stages_stalled += stage + 1

                        
                
            
    def pipeline_open(self, pipelined):
        if pipelined:
            return self.pipeline[0] is None
        else:
            for stage in self.pipeline:
                if stage is not None:
                    return False
            return True
    
    #Attempts to process next instruction
    def process_line(self, sim, query, ideal):
        #If the PE isn't currently processing a query, nothing is done
        
        #Loads next instruction if not currently stalled
        if query.stalled:
            sim.stalled_cycles += 1
        else:
            self.lines_processed += 1
        line = query.current_instruction
        #Read
        print(line)
        if line[0] == "R":
            access_type = line[1]
            if not query.stalled:
                sim.access_nums[access_type] += 1
            address = line[2]
            
            #If true is returned there was a bank conflict
            if sim.split:
                scratchpad = sim.scratchpads[access_type]
            else:
                scratchpad = sim.scratchpads[0]
            if scratchpad.read(address):
                sim.num_conflicts += 1
                if not ideal:
                    query.stalled = True
            else:
                query.stalled = False
        elif query.instructions[0][0] == "SUB":
            print("SUB")
            query.subtree = int(query.instructions[0][1])
            query.next_instruction()
            return True
        #If there are no more instructions to be processed, the query is removed from the list of active queries, and the PE is ready to be assigned a new query
        elif query.instructions[0] == "BT":
            if not query.stalled:
                query.next_instruction()
                pipeline_switch = True
                query.backtrack = not query.backtrack
                return True
        if not query.stalled:
            query.next_instruction()
        return False