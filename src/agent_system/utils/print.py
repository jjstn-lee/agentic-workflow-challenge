from pathlib import Path
from typing import Dict, Any
import json
import pandas as pd

def append_to_file(relative_path: str, text: str):
    """
    Append a string to a file in the 'src/data' directory, one level up from this file.

    Parameters:
    - relative_path (str): Path relative to the 'src/data' directory, e.g., "report.txt"
    - text (str): Text to append
    """
    src_dir = Path(__file__).resolve().parents[2]  # one level up

    file_path = src_dir / "data" / relative_path

    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("a", encoding="utf-8") as f:
        f.write(text + "\n\n-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-\n\n")  # add newlines for each append

    print(f"Appended text to {file_path}")

def print_agent_arrival(agent_name: str):
    """Print a clean arrival message for an agent."""
    print(f"\n{'='*60}")
    print(f"{agent_name.upper()} AGENT - ARRIVAL")
    print(f"{'='*60}")

def print_agent_step(agent_name: str, step_description: str):
    """Print the current step an agent is performing."""
    print(f"{agent_name.upper()} - {step_description}")

def print_state_update(agent_name: str, updates: Dict[str, Any]):
    """Print what the agent is updating in the state."""
    print(f"{agent_name.upper()} - UPDATING STATE:")
    for key, value in updates.items():
        if isinstance(value, str) and len(value) > 100:
            display_value = value[:100] + "..."
        else:
            display_value = value
        print(f"   • {key}: {display_value}")

def print_final_state(agent_name: str, state: Dict[str, Any]):
    """Print the current state after agent completion."""
    print(f"\n{agent_name.upper()} - FINAL STATE:")
    print(f"{'─'*50}")
    
    for key, value in state.items():
        if value is not None:
            if key == "extracted_df" and hasattr(value, 'shape'):
                print_dataframe_pandas_style(value)
            elif key == "analysis" and isinstance(value, str) and len(value) > 200:
                print(f"   {key}: {value[:200]}...")
            elif key == "doc" and isinstance(value, str) and len(value) > 100:
                print(f"   {key}: {value[:100]}...")
            else:
                print(f"   {key}: {value}")
    
    print(f"{'─'*50}")
    print(f"{agent_name.upper()} AGENT COMPLETED")
    print(f"{'='*60}\n")

def print_state_clear(state: Dict[str, Any], title: str = "STATE"):
    """
    Print State in a clear and concise way, better than Python's default dict printing.
    
    Parameters:
    - state: The State dictionary to print
    - title: Optional title for the state display
    """
    print(f"\n{title.upper()}")
    print(f"{'═'*60}")
    
    user_input_fields = ['query']
    orchestrator_fields = ['task_type']
    sql_fields = ['extracted_df']
    kb_fields = ['best_score', 'doc']
    analyzer_fields = ['analysis']
    
    print("USER INPUT:")
    for field in user_input_fields:
        if field in state and state[field] is not None:
            value = state[field]
            if isinstance(value, str) and len(value) > 80:
                print(f"   • {field}: {value[:80]}...")
            else:
                print(f"   • {field}: {value}")
    
    print("\nORCHESTRATOR:")
    for field in orchestrator_fields:
        if field in state and state[field] is not None:
            print(f"   • {field}: {state[field]}")
    
    print("\nSQL RETRIEVER:")
    for field in sql_fields:
        if field in state and state[field] is not None:
            if field == "extracted_df" and hasattr(state[field], 'shape'):
                print_dataframe_pandas_style(state[field])
            else:
                print(f"   • {field}: {state[field]}")
    
    print("\nKB RETRIEVER:")
    for field in kb_fields:
        if field in state and state[field] is not None:
            value = state[field]
            if field == "doc" and isinstance(value, str) and len(value) > 100:
                print(f"   • {field}: {value[:100]}...")
            else:
                print(f"   • {field}: {value}")
    
    print("\nANALYZER:")
    for field in analyzer_fields:
        if field in state and state[field] is not None:
            value = state[field]
            if isinstance(value, str) and len(value) > 200:
                print(f"   • {field}: {value[:200]}...")
            else:
                print(f"   • {field}: {value}")
    
    print(f"{'═'*60}")

def print_dataframe_summary(df: pd.DataFrame, max_rows: int = 10, max_cols: int = 8):
    """
    Print a comprehensive Pandas-esque summary of a DataFrame.
    
    Parameters:
    - df: pandas DataFrame to print
    - max_rows: Maximum number of rows to display (default: 10)
    - max_cols: Maximum number of columns to display (default: 8)
    """
    if df is None or df.empty:
        print("   DataFrame: Empty or None")
        return
    
    print(f"   DataFrame Summary:")
    print(f"   ┌─ Shape: {df.shape[0]} rows × {df.shape[1]} columns")
    print(f"   ├─ Memory usage: {df.memory_usage(deep=True).sum() / 1024:.2f} KB")
    print(f"   ├─ Index type: {type(df.index).__name__}")
    print(f"   └─ Column dtypes:")
    
    for i, (col, dtype) in enumerate(df.dtypes.items()):
        if i < max_cols:
            print(f"      • {col}: {dtype}")
        elif i == max_cols:
            print(f"      • ... and {len(df.columns) - max_cols} more columns")
            break
    
    print(f"\n   Data Preview (first {min(max_rows, len(df))} rows):")
    print("   " + "─" * 80)
    
    preview_df = df.head(max_rows)
    
    if len(df.columns) > max_cols:
        preview_df = preview_df.iloc[:, :max_cols]
        print("   " + str(preview_df.to_string(index=True, max_cols=max_cols)).replace('\n', '\n   '))
        print(f"   ... and {len(df.columns) - max_cols} more columns")
    else:
        print("   " + str(preview_df.to_string(index=True)).replace('\n', '\n   '))
    
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        print(f"\n   Numeric Summary:")
        print("   " + "─" * 50)
        stats = df[numeric_cols].describe()
        print("   " + str(stats.to_string()).replace('\n', '\n   '))
    
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    if len(categorical_cols) > 0:
        print(f"\n   Categorical Summary:")
        print("   " + "─" * 50)
        for col in categorical_cols[:3]:            
            print(f"   {col} value counts:")
            value_counts = df[col].value_counts().head(5)
            for val, count in value_counts.items():
                print(f"      • {val}: {count}")
            if len(df[col].unique()) > 5:
                print(f"      • ... and {len(df[col].unique()) - 5} more unique values")

def print_dataframe_pandas_style(df: pd.DataFrame, max_rows: int = 15, max_cols: int = 10):
    """
    Print a DataFrame in a more authentic Pandas style with better formatting.
    
    Parameters:
    - df: pandas DataFrame to print
    - max_rows: Maximum number of rows to display (default: 15)
    - max_cols: Maximum number of columns to display (default: 10)
    """
    if df is None or df.empty:
        print("   DataFrame: Empty or None")
        return
    
    print(f"   DataFrame ({df.shape[0]} rows × {df.shape[1]} columns)")
    print("   " + "=" * 60)
    
    print("   Index:")
    print("   " + "─" * 40)
    print(f"   RangeIndex: {df.index.start if hasattr(df.index, 'start') else 0} to {df.index.stop if hasattr(df.index, 'stop') else len(df)-1}, step {df.index.step if hasattr(df.index, 'step') else 1}")
    
    print(f"\n   Data columns (total {len(df.columns)} columns):")
    print("   " + "─" * 40)
    
    col_info = []
    for i, (col, dtype) in enumerate(df.dtypes.items()):
        non_null = df[col].count()
        null_count = len(df) - non_null
        col_info.append(f"   {i:2d}  {col:<20} {str(dtype):<10} {non_null:>6} non-null")
        if null_count > 0:
            col_info[-1] += f" ({null_count} null)"
    
    for line in col_info:
        print(line)
    
    memory_usage = df.memory_usage(deep=True).sum()
    print(f"\n   Memory usage: {memory_usage / 1024:.2f} KB")
    
    print(f"\n   Data Preview:")
    print("   " + "─" * 60)
    
    preview_df = df.head(max_rows)
    
    if len(df.columns) > max_cols:
        preview_df = preview_df.iloc[:, :max_cols]
        print("   " + str(preview_df.to_string(index=True, max_cols=max_cols, line_width=80)).replace('\n', '\n   '))
        print(f"   ... and {len(df.columns) - max_cols} more columns")
    else:
        print("   " + str(preview_df.to_string(index=True, line_width=80)).replace('\n', '\n   '))
    
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        print(f"\n   Summary Statistics:")
        print("   " + "─" * 50)
        stats = df[numeric_cols].describe()
        stats_str = str(stats.to_string())
        for line in stats_str.split('\n'):
            print("   " + line)
    
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    if len(categorical_cols) > 0:
        print(f"\n   Categorical Data:")
        print("   " + "─" * 50)
        for col in categorical_cols[:3]:         
            unique_count = df[col].nunique()
            print(f"   {col}: {unique_count} unique values")
            if unique_count <= 10:               
                value_counts = df[col].value_counts()
                for val, count in value_counts.items():
                    print(f"      • {val}: {count}")
            else:                
                value_counts = df[col].value_counts().head(5)
                print(f"      Top values:")
                for val, count in value_counts.items():
                    print(f"      • {val}: {count}")
                print(f"      ... and {unique_count - 5} more unique values")

def print_agent_error(agent_name: str, error: str):
    """Print an error message for an agent."""
    print(f"\n{agent_name.upper()} AGENT ERROR:")
    print(f"   {error}")
    print(f"{'='*60}\n")
