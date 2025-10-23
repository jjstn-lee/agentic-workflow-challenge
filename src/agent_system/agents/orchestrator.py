from langgraph.types import Command
from agent_system.utils.print import (
    print_agent_arrival, 
    print_agent_step, 
    print_state_update, 
    print_final_state,
    print_agent_error
)

class Orchestrator:
    def process(self, state):
        """
        Orchestrator: decides what retrieval steps to run based on the query.
        """
        print_agent_arrival("ORCHESTRATOR")
        
        try:
            print_agent_step("ORCHESTRATOR", "Analyzing query and determining task type")
            
            task_type = "general"
            next_nodes = ["sqlRetriever", "kbRetriever"]
            
            updates = {"task_type": task_type}
            print_state_update("ORCHESTRATOR", updates)
            
            updated_state = dict(state)
            updated_state.update(updates)
            print_final_state("ORCHESTRATOR", updated_state)
            
            return Command(
                update=updates,
                goto=next_nodes
            )
            
        except Exception as e:
            print_agent_error("ORCHESTRATOR", str(e))
            return Command(
                update={"error": str(e)},
                goto=[]
            )
        