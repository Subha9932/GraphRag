from langgraph.graph import StateGraph, END
from agentic_copilot.schemas.state import GlobalState

def retrieve_docs(state: GlobalState):
    """
    Mock RAG retrieval. In production, this would query a VectorDB (Chroma/FAISS).
    """
    query = state["user_query"]
    # Simulated retrieval
    docs = [
        f"Doc chunk 1 relevant to '{query}'",
        f"Doc chunk 2 relevant to '{query}'"
    ]
    return {"rag_context": docs}

def create_rag_subgraph():
    workflow = StateGraph(GlobalState)
    
    workflow.add_node("retrieve_docs", retrieve_docs)
    
    workflow.set_entry_point("retrieve_docs")
    workflow.add_edge("retrieve_docs", END)
    
    return workflow.compile()
