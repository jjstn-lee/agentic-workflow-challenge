# Agentic AI Workflow Challenge

A Python package implementing an agentic AI workflow.

## Installation and Usage

First, you'll want to make sure you have a virtual environment set up and have all the dependencies installed. You may also use the `pyenv` module to accomplish the same thing.

Using built-in `venv` module:
```bash
cd [root dir]                   # first, make sure you're in the root directory
python3 -m venv venv            # create venv
source venv/bin/activate        # activate venv
pip install -r requirements.txt # install dependencies
```

Then, you'll want to add your own Google API key to the `.env` file.

Once you have the virtual environment set up, dependencies installed, and API key added to `.env`, you may run the project:

```bash
cd src
python3 main.py
```

If you wanted to add more queries in order to automatically queue them through the workflow *or* if you wanted to add more data to `campaign_performance.csv` or `kb_documents.jsonl`, those files can be found in `src/data`.

## System Architecture/Project Structure

### Agent AI Workflow
This is what the AI agent workflow looks like, where each rectangle is an agent:

```bash   
                         ┌─────────────────────────┐
                         │      orchestrator       │
                         │ Input: user query       │
                         │ Output: user query      │
                         └──────────┬──────────────┘
                                    │
                     ┌──────────────┴──────────────┐
                     │                             │
         ┌──────────────────────┐       ┌──────────────────────┐
         │     sqlRetriever     │       │     kbRetriever      │
         │ Input: user query    │       │ Input: user query    │
         │ Output: SQL table    │       │ Output: most similar │
         │  subset              │       │ vector embedding +   │
         │                      │       │ similarity score     │
         └──────────┬───────────┘       └──────────┬───────────┘
                    │                              │
                    └──────────────┬───────────────┘
                                   │
                           ┌──────────────────┐
                           │     analyzer     │
                           │ Input: SQL table │
                           │ + vector info    │
                           │ Output: data     │
                           │ analysis report  │
                           └─────────┬────────┘
                                     │

                                    END
                                FINAL REPORT

```


### Agent System (`/agent_system/`)
The core of the system is built around specialized agents that work together through a shared state:

- **`/agents/`** - Contains the four main agents:
  - `orchestrator.py` - Coordinates and begins workflow.
  - `sql_retriever.py` - Writes and executes SQL queries on the campaign performance data.
  - `kb_retriever.py` - Performs search on the knowledge base documents.
  - `analyzer.py` - Combines results from both retrievers and generates final analysis.

- **`/state/`** - Implements the shared state pattern using LangGraph's TypedDict:
  - `state.py` - Defines the State class that flows through the entire workflow.
  - Each agent reads from and writes to this shared state, enabling communication.

- **`/clients/`** - Abstracts data access layers for scalability:
  - `duckdb_client.py` - Provides a clean SQL interface using DuckDB.
  - `naive_kb.py` - Implements the knowledge base search using TF-IDF vectorization.

- **`/utils/`** - Shared utilities and helper functions:
  - `print.py` - Centralized logging and output formatting for agents.
  - `tools.py` - Common utility functions used across multiple agents.

### Benefits of This Architecture

1. **Encapsulation**: Each agent has a single, well-defined responsibility.
2. **Scalability**: The client abstraction allows easy migration from in-memory to persistent storage.
3. **Maintainability**: Changes to one agent don't affect others.
5. **Flexibility**: New agents or data sources can be added without modifying existing code.

This is what the project tree looks like:

```bash
agentic-workflow-challenge
├── .env
├── .gitignore
├── README.md
├── requirements.txt
└── src
    ├── agent_system
    │   ├── __init__.py
    │   ├── agents
    │   │   ├── __init__.py
    │   │   ├── analyzer.py
    │   │   ├── kb_retriever.py
    │   │   ├── orchestrator.py
    │   │   └── sql_retriever.py
    │   ├── clients
    │   │   ├── __init__.py
    │   │   ├── duckdb_client.py
    │   │   └── naive_kb.py
    │   ├── state
    │   │   ├── __init__.py
    │   │   └── state.py
    │   └── utils
    │       ├── __init__.py
    │       ├── print.py
    │       └── tools.py
    ├── data
    │   ├── campaign_performance.csv
    │   ├── kb_documents.jsonl
    │   ├── report.md # file to keep track of query results
    │   └── sample_queries.txt
    └── main.py
```

## Key Decisions/Approach

### Designing the Agents

I was given two datasets, so I decided to go with 2 specialized agents for each of them. Of course, I also needed an Orchestrator and an agent responsible for the final data analysis, so that made it 4 agents in total for this project.

I knew that separating the job of data retrieval into 2 separate agents technically meant more space complexity, but I also knew it wouldn't have a negative impact on the time complexity of the program. In addition, modularizing the code in this way made it simpler and cleaner. This would mean better maintenance and flexibility for future changes of the codebase.

In addition, I knew that because of the way I planned on handling and querying the datasets, having a singular agent handle all that logic would quickly turn into one of those Python scripts that seem to never end.

### Handling the Datasets

While working on this project, I wanted to make sure that my solution would scale very well. Thus, one thing I did was use DuckDB in order to store the data in `campaign_performance.csv`. Even though information is still stored in-memory, I designed an interface that would remain the same even after migrating to an actual database or scaling to millions of rows of `.csv` data.

Doing something similar was much harder for `kb_documents.jsonl` because there was nothing like DuckDB for vector embeddings or vector databases. In addition, I could not find a vector embedding model API that gave me enough free tokens to continuously develop and test this project. So instead of doing anything LLM-related, I decided to use `sklearn`'s `TfidfVectorizer` to convert the text documents into numeric vectors that I could search and compare efficiently for similarity, enabling me to prototype the retrieval system without hitting token limits. Unfortunately, this vectorizer isn't semantic and is from the time when NLP wasn't driven by LLMs, but it worked surprisingly well for the queries that were given to me.

### How I would Scale to Production

Though I've already talked about scalability above, I would scale to Production by focusing on some other several key changes:

- Dockerize the application with multi-stage builds for optimized image sizes.
- Host on cloud service like AWS, Google Cloud, or Azure.
- Implement a REST API wrapper around the agent system.
- Add API rate limiting and authentication middleware.
- Use nginx or AWS Application Load Balancer for traffic distribution.
- Implement circuit breakers for fault tolerance.

### Encapsulation/Modularization

The project structure is optimized for anyone to make small changes, even if they have never seen the codebase before. I believe that if you intend on programming alongside people, this is a very important skill to have.

### Assumptions

When designing and working on this project, I assumed that every query would require some type of retrieval that then needed to be analyzed, and there is no functionality to ensure safety if there is a query that doesn't need retrieval. If this assumption were untrue, I would add that functionality to the `Orchestrator` and let them decide if the query needed retrieval, analysis, or both.

## Extra Features

### Report Generation and Persistence
The system automatically writes analysis reports to a centralized `report.md` file located in `src/data/report.md`. This feature allows you to:

- **Save individual query results**: After each query, you can choose to save the analysis to the report file.
- **Batch processing**: Run all sample queries at once and save all results to the report file.
- **Persistent storage**: All analyses are appended to the same file with clear separators for easy review.

To use the report functionality, follow instructions in the REPL.

### Comprehensive State Management
Each agent's state is tracked and displayed with detailed formatting, showing data flow through the entire pipeline.
