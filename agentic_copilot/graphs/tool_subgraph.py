from langgraph.graph import StateGraph, END
from agentic_copilot.schemas.state import GlobalState

def execute_repo_tools(state: GlobalState):
    """
    Executes real-time tools on the repo (e.g., grep, ls).
    """
    # Mock tool execution results
    results = [
        "Ran 'ls -R': Found 150 files.",
        "Ran 'grep -r TODO': Found 23 pending tasks."
    ]
    return {"tool_results": results}

def create_tool_subgraph():
    workflow = StateGraph(GlobalState)
    
    workflow.add_node("execute_repo_tools", execute_repo_tools)
    
    workflow.set_entry_point("execute_repo_tools")
    workflow.add_edge("execute_repo_tools", END)
    
    return workflow.compile()
