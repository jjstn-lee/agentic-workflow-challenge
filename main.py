from typing import TypedDict, Annotated
import operator
from langgraph.graph import StateGraph, END
from agent_system.clients.duckdb_client import DuckDBClient

from agent_system import run_query, initialize_db

# initialize mock database via duckdb
db = DuckDBClient()
db.register_csv("campaign_performance", "data/campaign_performance.csv")

