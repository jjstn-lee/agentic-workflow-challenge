import re
from dotenv import load_dotenv
import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.types import Command
from langchain.prompts import PromptTemplate
from langchain.output_parsers import RegexParser

from agent_system.clients.duckdb_client import DuckDBClient
from agent_system.state.state import State

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class sqlRetriever():
    # sqlRetriever is the only model that needs access to the data, so keep it this way for safety
    duckdb_client = DuckDBClient(db_path=":memory:")

    def nl_to_sql(self, nl_query: str) -> str:
        """
        Convert NL query to SQL using LangChain LLM.
        """
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=GEMINI_API_KEY)
        
        template = """
        You are an expert SQL generator. For the following assignment, you need to determine what information you
        need to retrieve and write a SQL query that can extract that information.

        CRITICAL RULES:
        - Write ONLY a SELECT query that retrieves raw data from the table
        - Do NOT use any aggregate functions (COUNT, SUM, AVG, STDDEV, MIN, MAX, etc.)
        - Do NOT use any mathematical operations or expressions in SELECT, WHERE, ORDER BY, or any other clause
        - Do NOT perform any calculations whatsoever - no arithmetic operations like +, -, *, /
        - ONLY use simple column selections and basic filtering (WHERE with =, IN, LIKE, etc.)
        - The data retrieved will be processed separately after the query runs

        Return ONLY the SQL query and nothing else. Do NOT add commentary, recommendations, or analysis.

        Assignment: {nl_query}

        For context, the table name is always "campaign_performance" and its data has the following shape:
        campaign_id,brand_area,quarter,tactic,spend,impressions,clicks,conversions,revenue
        1000,Cardiology,2025Q1,Email,21921,60742,634,123,9272.49
        1001,Cardiology,2025Q1,Display,7583,143768,643,86,3772.91
        """

        # 1. Create PromptTemplate
        prompt = PromptTemplate(input_variables=["nl_query"], template=template)

        # 2. Format it to a string with actual query
        prompt_text = prompt.format(nl_query=nl_query)

        # 3a. For plain LLM invoke
        sql_query = llm.invoke(prompt_text).content
        
        # cleaning
        sql_query = sql_query.strip()
        sql_query = re.sub(r"^```(sql)?\s*|\s*```$", "", sql_query, flags=re.IGNORECASE)
        if (sql_query.startswith('"') and sql_query.endswith('"')) or (sql_query.startswith("'") and sql_query.endswith("'")):
            sql_query = sql_query[1:-1]
        
        print(f"SQL_QUERY: {sql_query}")
        return sql_query

    def tweak_query_on_error(self, query: str, error: Exception) -> str:
        return "SELECT * FROM sample_data LIMIT 10"

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
        
        print_agent_arrival("SQL RETRIEVER")
        
        try:
            nl_query = state.get("query", "")
            print_agent_step("SQL RETRIEVER", f"Processing natural language query: '{nl_query}'")
            
            print_agent_step("SQL RETRIEVER", "Converting natural language to SQL")
            sql_query = self.nl_to_sql(nl_query)
            
            print_agent_step("SQL RETRIEVER", "Executing SQL query against database")
            df = self.duckdb_client.query(sql_query)

            print_agent_step("SQL RETRIEVER", "Parsing and validating SQL query")
            parser = RegexParser(
                regex=r"(?i)(SELECT|INSERT|UPDATE|DELETE).*",  # matches SQL statement
                output_keys=["sql_query"]
            )
            
            parsed = parser.parse(sql_query)
            sql_query = parsed["sql_query"]
            
            print_agent_step("SQL RETRIEVER", f"Retrieved {len(df)} rows of data")
            print(f"   Data preview: {df.head(3).to_string() if len(df) > 0 else 'No data found'}")

            updates = {
                "extracted_df": df.to_dict(orient="records")
            }
            print_state_update("SQL RETRIEVER", updates)
            
            updated_state = dict(state)
            updated_state.update(updates)
            print_final_state("SQL RETRIEVER", updated_state)

            return Command(
                update=updates,
                goto="analyzer"
            )

        except Exception as e:
            print_agent_error("SQL RETRIEVER", str(e))
            return Command(
                update={"error": str(e)},
                goto=[]
            )
