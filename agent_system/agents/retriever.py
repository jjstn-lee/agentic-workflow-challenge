from langgraph import Command
from pathlib import Path
import pandas as pd
from clients.duckdb_client import DuckDBClient
from langchain_google_genai import ChatGoogleGenerativeAI

from state.global_state import GLOBAL_STATE

# Initialize DuckDB
# Retriever is the only model that needs access to the data, so keep it this way for safety
duckdb_client = DuckDBClient(db_path=":memory:")

def nl_to_sql(nl_query: str) -> str:
    """
    Convert NL query to SQL using LangChain LLM.
    """
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro")
    prompt = f"Convert the following natural language query to SQL for a DuckDB table 'sample_data':\n\n{nl_query}"
    sql_query = llm(prompt)
    return sql_query

def tweak_query_on_error(query: str, error: Exception) -> str:
    # Basic fallback logic
    return "SELECT * FROM sample_data LIMIT 10"


def retrieval_agent(state) -> Command:
    """
    Retriever: Fetches relevant documents based on the search query.
    """
    try:
        # # Example: register CSV if not already done
        # csv_path = state.get("csv_path", "data/sample.csv")
        # table_name = "sample_data"

        # if table_name not in duckdb_client.list_tables():
        #     duckdb_client.register_csv(table_name, csv_path)

        # Example query (can be dynamic)
        nl_query = GLOBAL_STATE.get("query")
        df = duckdb_client.query(query)

        # Update workflow state
        return Command(
            update={"retrieved_data": df},
            goto=None  # Let Orchestrator decide next agent
        )

    except Exception as e:
        return Command(
            update={"error": str(e)},
            goto=None
        )
