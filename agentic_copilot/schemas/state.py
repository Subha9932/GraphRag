from typing import TypedDict, List, Annotated, Optional
import operator

def _keep_first(left, right):
    """Reducer that keeps the first value and ignores subsequent updates"""
    return left if left else right

class GlobalState(TypedDict):
    """
    Global state for the Agentic Engineering Knowledge Copilot.
    
    Attributes:
        user_query: The original query from the user.
        intent: The classified intent of the query (e.g., "explain", "refactor").
        rag_context: List of strings retrieved from document RAG.
        graphrag_context: List of strings retrieved from code GraphRAG.
        tool_results: List of outputs from tool executions.
        risk_signals: List of risk factors identified.
        merged_insights: Consolidated insights from all subgraphs.
        final_answer: The final response generated for the user.
    """
    # Use custom reducer to prevent concurrent update errors
    user_query: Annotated[str, _keep_first]
    intent: Annotated[str, _keep_first]
    
    # Reducers: append new items to the list
    rag_context: Annotated[List[str], operator.add]
    graphrag_context: Annotated[List[str], operator.add]
    tool_results: Annotated[List[str], operator.add]
    risk_signals: Annotated[List[str], operator.add]
    
    merged_insights: Annotated[List[str], operator.add]
    
    # final_answer can be updated multiple times, last write wins
    final_answer: Annotated[str, _keep_first]
