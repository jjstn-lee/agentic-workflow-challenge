from langgraph.types import Command
from dotenv import load_dotenv
import os

from agent_system.clients.naive_kb import KBClient
from agent_system.state.state import State

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class kbRetriever():
    # kbRetriever is the only model that needs access to the data, so keep it this way for safety
    kb_client = KBClient()
    
    def process(self, state):
        """
        Retriever: Fetches relevant documents based on the search query.
        """
        from agent_system.utils.print import (
            print_agent_arrival, 
            print_agent_step, 
            print_state_update, 
            print_final_state,
            print_agent_error
        )
        
        print_agent_arrival("KB RETRIEVER")
        
        try:
            query = state.get("query", "")
            print_agent_step("KB RETRIEVER", f"Searching knowledge base for: '{query}'")
            
            print_agent_step("KB RETRIEVER", "Computing semantic similarity scores")
            best_score, doc = self.kb_client.find_nearest(query)
            
            print_agent_step("KB RETRIEVER", f"Found best match with score: {best_score:.4f}")
            text_preview = doc["text"][:100]
            print(f"   Document preview: {text_preview}{'...' if len(doc['text']) > 100 else ''}")

            updates = {
                "best_score": best_score,
                "doc": doc
            }
            print_state_update("KB RETRIEVER", updates)
            
            updated_state = dict(state)
            updated_state.update(updates)
            print_final_state("KB RETRIEVER", updated_state)

            return Command(
                update=updates,
                goto="analyzer"
            )

        except Exception as e:
            print_agent_error("KB RETRIEVER", str(e))
            return Command(
                update={"error": str(e)},
                goto=[]
            )
