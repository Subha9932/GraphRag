from langgraph.graph import StateGraph, END, START
from agentic_copilot.schemas.state import GlobalState

# Import subgraphs
from agentic_copilot.graphs.intent_subgraph import create_intent_subgraph
from agentic_copilot.graphs.rag_subgraph import create_rag_subgraph
from agentic_copilot.graphs.graphrag_subgraph import create_graphrag_subgraph
from agentic_copilot.graphs.tool_subgraph import create_tool_subgraph
from agentic_copilot.graphs.risk_subgraph import create_risk_subgraph
from agentic_copilot.agents.reasoning_agent import final_reasoning

def create_main_graph():
    workflow = StateGraph(GlobalState)
    
    # 1. Define Nodes
    # We treat compiled subgraphs as nodes
    workflow.add_node("intent_analyzer", create_intent_subgraph())
    
    # Parallel nodes
    # workflow.add_node("rag_agent", create_rag_subgraph())
    workflow.add_node("graphrag_agent", create_graphrag_subgraph())
    # workflow.add_node("tool_agent", create_tool_subgraph())
    # workflow.add_node("risk_agent", create_risk_subgraph())
    
    # Reducer/Final node
    workflow.add_node("final_reasoner", final_reasoning)
    
    # 2. Define Edges
    # Start -> Intent
    workflow.add_edge(START, "intent_analyzer")
    
    # Intent -> Parallel Agents
    # workflow.add_edge("intent_analyzer", "rag_agent")
    workflow.add_edge("intent_analyzer", "graphrag_agent")
    # workflow.add_edge("intent_analyzer", "tool_agent")
    # workflow.add_edge("intent_analyzer", "risk_agent")
    
    # All parallel agents feed into the final reasoner
    # workflow.add_edge("rag_agent", "final_reasoner")
    workflow.add_edge("graphrag_agent", "final_reasoner")
    # workflow.add_edge("tool_agent", "final_reasoner")
    # workflow.add_edge("risk_agent", "final_reasoner")
    
    # End
    workflow.add_edge("final_reasoner", END)
    
    return workflow.compile()
