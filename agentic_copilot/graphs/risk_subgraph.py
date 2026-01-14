from langgraph.graph import StateGraph, END
from agentic_copilot.schemas.state import GlobalState

def analyze_risk(state: GlobalState):
    """
    Analyzes the risk of proposed changes or the query intent.
    """
    intent = state.get("intent", "")
    risks = []
    
    if intent == "refactor":
        risks.append("HIGH RISK: Refactoring may break dependent modules.")
    elif "delete" in state["user_query"].lower():
        risks.append("CRITICAL: Deletion of files detected.")
    else:
        risks.append("Low risk: Query is informational.")
        
    return {"risk_signals": risks}

def create_risk_subgraph():
    workflow = StateGraph(GlobalState)
    
    workflow.add_node("analyze_risk", analyze_risk)
    
    workflow.set_entry_point("analyze_risk")
    workflow.add_edge("analyze_risk", END)
    
    return workflow.compile()
