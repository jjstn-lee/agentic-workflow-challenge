import json
from dotenv import load_dotenv
import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.types import Command
from langchain.prompts import PromptTemplate
from langgraph.prebuilt import create_react_agent

from agent_system.utils.tools import analysis_tools
from agent_system.state.state import State

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class Analyzer():
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=GEMINI_API_KEY)
    agent = create_react_agent(llm, analysis_tools)
    
    def summarize(self, query, df_json, score, doc):
        template = """
        For each assignment you receive, follow these steps carefully:

        1. **Analyze the provided data** using the available tools. 
        - Tools can calculate metrics like ROI, CTR, conversion rate, or stability.
        - Tools can also interact with an external knowledge base.
        - Use filtering or summarization tools when needed.
        2. **Summarize your findings** clearly.
        - Include key insights, commentary, and data-driven recommendations.
        - Highlight patterns, anomalies, and trends in performance.
        3. **Be concise but insightful.**
        - Use natural language and, when helpful, simple tables or bullet points.
        - Always explain your reasoning briefly.
        
        If no data or parameters are given, you may make assumptions *ONLY* if
        you clarify your line of reasoning.
        
        For context, this is the query: {query}
        
        This is the data you were given as a JSON file: {df_json}
        
        The most relevant document found had a score of {score}: {doc}
        """
        
        prompt = PromptTemplate(input_variables=["query", "score", "doc", "df_json"], template=template)
        prompt_text = prompt.format(query=query, df_json=df_json, score=score, doc=doc)
        analysis = self.llm.invoke(prompt_text).content
        
        return analysis
        
    def process(self, state):
        from agent_system.utils.print import (
            print_agent_arrival, 
            print_agent_step, 
            print_state_update, 
            print_final_state,
            print_agent_error
        )
        
        print_agent_arrival("ANALYZER")
        
        try:
            df_json = state.get("extracted_df", "[]")
            query = state.get("query", "")
            best_score = state.get("best_score", "")
            doc = state.get("doc", "")

            print_agent_step("ANALYZER", "Extracting data from state")
            print_agent_step("ANALYZER", f"Processing query: '{query}'")
            print_agent_step("ANALYZER", f"Using knowledge base document with score: {best_score}")

            if isinstance(df_json, str):
                data_list = json.loads(df_json)
            else:
                data_list = df_json

            print_agent_step("ANALYZER", f"Analyzing {len(data_list)} data records")
            print_agent_step("ANALYZER", "Generating comprehensive analysis using AI tools")

            analysis = self.summarize(query, data_list, best_score, doc)
            
            print_agent_step("ANALYZER", "Analysis completed")
            print(f"   Analysis preview: {analysis[:150]}{'...' if len(analysis) > 150 else ''}")

            updates = {"analysis": analysis}
            print_state_update("ANALYZER", updates)
            
            updated_state = dict(state)
            updated_state.update(updates)
            print_final_state("ANALYZER", updated_state)

            return Command(
                update=updates,
            )

        except Exception as e:
            print_agent_error("ANALYZER", str(e))
            return Command(update={"error": str(e)})