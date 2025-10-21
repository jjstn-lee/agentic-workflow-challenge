from typing import TypedDict, Annotated
import operator
from langgraph.graph import StateGraph, END
from datastore import DuckDBClient

# initialize database client via DuckDB
def initialize_db(csv_path: str = "data/campaign_performance.csv"):
    """Initialize the DuckDB client and register the campaign data."""
    global db_client
    db_client = DuckDBClient(db_path=":memory:")
    db_client.register_csv("campaigns", csv_path)
    return db_client

class State(): 
    """
    State object that flows through the graph.
    Each node reads from and writes to this state.
    """
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
    messages: Annotated[list[str], operator.add]  # Accumulates messages
    
    # initialzie database client via duckDB and add to agent system state
    db = initialize_db()

def orchestrator_node(state: State) -> dict:
    """
    Orchestrator: Analyzes the query and decides what needs to be retrieved.
    """
    
    query = state["query"]
    
    # In a real implementation, you'd use an LLM here
    # For demo purposes, simple logic:
    if "weather" in query.lower():
        task_type = "weather_lookup"
        search_query = f"current weather for query: {query}"
    elif "news" in query.lower():
        task_type = "news_search"
        search_query = f"latest news about: {query}"
    else:
        task_type = "general_search"
        search_query = query
    
    return {
        "task_type": task_type,
        "search_query": search_query,
        "messages": [f"Orchestrator: Determined task type '{task_type}'"]
    }

def retriever_node(state: State) -> dict:
    """
    Retriever: Fetches relevant documents based on the search query.
    """
    search_query = state["search_query"]
    task_type = state["task_type"]
    
    # In a real implementation, you'd call a vector DB, search API, etc.
    # Mock retrieval:
    mock_docs = [
        f"Document 1 about {search_query}",
        f"Document 2 related to {task_type}",
        f"Document 3 with additional context"
    ]
    
    return {
        "retrieved_docs": mock_docs,
        "messages": [f"Retriever: Found {len(mock_docs)} documents"]
    }
    


def analyzer_node(state: State) -> dict:
    """
    Analyzer: Processes retrieved documents and generates final response.
    """
    query = state["query"]
    docs = state["retrieved_docs"]
    
    # In a real implementation, you'd use an LLM to analyze docs
    # Mock analysis:
    analysis = f"Analyzed {len(docs)} documents for query: '{query}'"
    final_response = f"Based on the retrieved information:\n"
    final_response += f"- Found {len(docs)} relevant sources\n"
    final_response += f"- Key insight: {docs[0]}\n"
    final_response += f"- Summary: This is the analyzed response to your query."
    
    return {
        "analysis": analysis,
        "final_response": final_response,
        "messages": ["Analyzer: Completed analysis and generated response"]
    }


def create_workflow():
    """
    Creates and compiles the LangGraph workflow.
    """
    # Initialize the graph with our state schema
    workflow = StateGraph(State)
    
    # Add nodes (agents)
    workflow.add_node("orchestrator", orchestrator_node)
    workflow.add_node("retriever", retriever_node)
    workflow.add_node("analyzer", analyzer_node)
    
    # Define the flow (edges)
    workflow.set_entry_point("orchestrator")  # Start here
    workflow.add_edge("orchestrator", "retriever")  # Then go to retriever
    workflow.add_edge("retriever", "analyzer")  # Then go to analyzer
    workflow.add_edge("analyzer", END)  # Finally, end
    
    # Compile the graph
    app = workflow.compile()
    
    return app