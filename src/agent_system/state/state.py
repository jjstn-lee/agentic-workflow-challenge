import operator
from typing import Annotated, TypedDict
import pandas

class State(TypedDict):
    """
    State object that flows through the graph.
    Each node reads from and writes to this state.
    """
    
    # user input
    query: str
    
    # orchestrator outputs
    task_type: str # for now, will be a single task type
    
    # sqlRetriever outputs
    extracted_df: pandas.DataFrame
    
    # kbRetriever outputs
    best_score: float
    doc: str
    
    # analyzer outputs
    analysis: str
    