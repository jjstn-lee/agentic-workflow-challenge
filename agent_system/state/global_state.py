class State(): 
    """
    State object that flows through the graph.
    Each node reads from and writes to this state.
    """
    
    def __init__():
        # user input
        query: str
        
        # orchestrator outputs
        task_type: str # for now, will be a single task type
        
        # Retriever outputs
        retrieved_docs: list[str]
        
        # analyzer outputs
        summary: str
        suggestion: str
        
        # Metadata
        # messages: Annotated[list[str], operator.add]  # Accumulates messages
        
GLOBAL_STATE = State()