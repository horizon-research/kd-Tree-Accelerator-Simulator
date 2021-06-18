#Processing Engine class, contains Pe's current status, as well as thw query it's currently assigned to
class PE:
    def __init__(self):
        self.stalled = False
        self.query = None
        self.busy = False
        self.lines_processed = 0
        self.pipeline_size = 36
        self.pipeline = [None for i in range(self.pipeline_size)]
        self.backtrack_pipeline_size = 8
        self.backtrack_pipeline = [None for i in range(self.backtrack_pipeline_size)]
    #Manages all queries currently in pipeline, processing their instrucitons for this cycle, and moving them through the pipeline if a stall hasn't occured
    def manage_pipeline(self, sim, pipeline):
        size = len(pipeline)
        #Iterates through queries in pipeline, starting with query closest to finish
        for stage in range(size - 1, -1, -1):
            query_at_stage = pipeline[stage]
            if query_at_stage:
                #Instruction is processed
                pipeline_switch = self.process_line(sim, query_at_stage)
                #If the query has not stalled, it can be advacned to the next stage of the pipeline
                if not query_at_stage.stalled:
                    #If query has gone through entire pipeline it can be added back to queue
                    if query_at_stage.finished():
                        sim.active_queries.remove(query_at_stage)
                        pipeline[stage] = None
                    elif pipeline_switch or stage == size - 1:
                        pipeline[stage] = None
                        if query_at_stage.backtrack:
                            sim.backtrack_queue.append(query_at_stage)
                        else:
                            sim.query_queue.append(query_at_stage)
                    elif pipeline[stage + 1] is None:
                        pipeline[stage] = None
                        pipeline[stage + 1] = query_at_stage

                        
                
            
    def pipeline_open(self, pipelined):
        if pipelined:
            return self.pipeline[0] is None
        else:
            for stage in self.pipeline:
                if stage is not None:
                    return False
            return True
    def backtrack_pipeline_open(self, pipelined):
        if pipelined:
            return self.backtrack_pipeline[0] is None
        else:
            for stage in self.backtrack_pipeline:
                if stage is not None:
                    return False
            return True
    #Attempts to process next instruction
    def process_line(self, sim, query):
        #If the PE isn't currently processing a query, nothing is done
        
        #Loads next instruction if not currently stalled
        if query.stalled:
            sim.stalled_cycles += 1
        else:
            self.lines_processed += 1
        line = query.current_instruction
        #Read
        if line[0] == "R" or line[0] == "W":
            access_type = line[1]
            if not query.stalled:
                sim.read_nums[access_type] += 1
            address = line[2]
            
            #If true is returned there was a bank conflict
            if sim.split:
                scratchpad = sim.scratchpads[access_type]
            else:
                scratchpad = sim.scratchpads[0]
            if scratchpad.read(address):
                sim.num_conflicts += 1
                query.stalled = True
            else:
                query.stalled = False
            
        if query.backtrack:
            sim.bcycles += 1
        else:
            sim.ncycles += 1

        pipeline_switch = False
        #If there are no more instructions to be processed, the query is removed from the list of active queries, and the PE is ready to be assigned a new query
        if query.instructions[0] == "BT":
            if not query.stalled:
                query.next_instruction()
                pipeline_switch = True
                query.backtrack = not query.backtrack
        if not query.stalled:
            query.next_instruction()
        return pipeline_switch                    
        