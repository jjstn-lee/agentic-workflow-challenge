from langgraph.graph import StateGraph, END

from pathlib import Path

from agent_system.state.state import State
from agent_system.agents.orchestrator import Orchestrator
from agent_system.agents.sql_retriever import sqlRetriever
from agent_system.agents.kb_retriever import kbRetriever
from agent_system.agents.analyzer import Analyzer
from agent_system.utils.print import append_to_file


def create_workflow():
    """Create and compile the LangGraph workflow."""
    
    orchestrator = Orchestrator()
    sql_retriever = sqlRetriever()
    kb_retriever = kbRetriever()
    analyzer = Analyzer()
    
    workflow = StateGraph(State)
    
    workflow.add_node("orchestrator", orchestrator.process)
    workflow.add_node("sqlRetriever", sql_retriever.process)
    workflow.add_node("kbRetriever", kb_retriever.process)
    workflow.add_node("analyzer", analyzer.process)
    
    workflow.set_entry_point("orchestrator")
    
    workflow.add_edge("orchestrator", "sqlRetriever")
    workflow.add_edge("orchestrator", "kbRetriever")
    
    workflow.add_edge("sqlRetriever", "analyzer")
    workflow.add_edge("kbRetriever", "analyzer")
    
    workflow.add_edge("analyzer", END)
    
    return workflow.compile()

def run_query(query: str):
    """Run a query through the workflow."""
    app = create_workflow()
    
    result = app.invoke({
        "query": query,
        "messages": []
    })
    
    return result

def load_sample_queries():
    """Load queries from the sample_queries.txt file."""
    sample_file = Path(__file__).parent / "data" / "sample_queries.txt"
    
    if not sample_file.exists():
        print(f"Sample queries file not found: {sample_file}")
        return []
    
    queries = []
    with open(sample_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if line and line[0].isdigit() and ') ' in line:
                    query = line.split(') ', 1)[1] if ') ' in line else line
                else:
                    query = line
                if query:
                    queries.append(query)
    
    return queries

def run_sample_queries():
    """Run all sample queries in succession."""
    queries = load_sample_queries()
    
    if not queries:
        print("No sample queries found.")
        return
    
    print(f"\nRunning {len(queries)} sample queries...")
    print("=" * 60)
    
    all_results = []
    
    for i, query in enumerate(queries, 1):
        print(f"\nQuery {i}/{len(queries)}: {query[:50]}{'...' if len(query) > 50 else ''}")
        print("-" * 60)
        
        try:
            result = run_query(query)
            analysis = result.get("analysis", "")
            
            if analysis:
                print(f"\nAnalysis {i}:")
                print("-" * 40)
                print(analysis)
                print("-" * 40)
                all_results.append(f"Query {i}: {query}\nAnalysis: {analysis}\n")
            else:
                print(f"\nNo analysis result for query {i}.")
                all_results.append(f"Query {i}: {query}\nAnalysis: No result\n")
                
        except Exception as e:
            print(f"\nError processing query {i}: {str(e)}")
            all_results.append(f"Query {i}: {query}\nError: {str(e)}\n")
    
    save_all = input(f"\n💾 Save all {len(queries)} results to report file? (y/n): ").strip().lower()
    if save_all in ['y', 'yes']:
        path_to_report = "./report.md"
        for result in all_results:
            append_to_file(path_to_report, result)
        print(f"Saved all results to {path_to_report}")
    
    print(f"\nCompleted {len(queries)} sample queries!")

def main():
    """Simple REPL for running queries through the workflow."""
    print("Medscape Analytics REPL")
    print("=" * 50)
    print("Enter your analytics queries below.")
    print("Type 'quit', 'exit', or 'q' to stop.")
    print("Type 'sample' or 'run-sample' to run all sample queries.")
    print("=" * 50)
    
    while True:
        try:
            query = input("\n📊 Enter query here! (or 'q' to quit): ").strip()
            
            if query.lower() in ['quit', 'exit', 'q', '']:
                print("Goodbye!")
                break
            
            if query.lower() in ['sample', 'run-sample', 'run_sample']:
                run_sample_queries()
                continue
            
            print("\nProcessing query...")
            
            result = run_query(query)
            
            analysis = result.get("analysis", "")
            if analysis:
                print("\nAnalysis:")
                print("-" * 40)
                print(analysis)
                print("-" * 40)
            else:
                print("\nNo analysis result found.")
            
            save_to_file = input("\n💾 Save to report file? (y/n): ").strip().lower()
            if save_to_file in ['y', 'yes']:
                path_to_report = "./report.md"
                append_to_file(path_to_report, analysis)
                print(f"Saved to {path_to_report}")
                
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Please try again.")

if __name__ == "__main__":
    main()