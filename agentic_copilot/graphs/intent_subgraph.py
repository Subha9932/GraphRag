from langgraph.graph import StateGraph, END
from agentic_copilot.schemas.state import GlobalState
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize LLM lazily
def get_llm():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("WARNING: OPENAI_API_KEY not found in environment.")
    return ChatOpenAI(model="gpt-4o", temperature=0, api_key=api_key)

def analyze_intent(state: GlobalState):
    query = state["user_query"]
    llm = get_llm()
    
    print("\n" + "="*80)
    print("🧠 INTENT AGENT - Analyzing Query")
    print("="*80)
    print(f"📝 User Query: '{query}'")
    
    system_prompt = """You are an intent classifier for an engineering system.
    Classify the query into one of these categories:
    - explain: Explaining concepts, architecture, or code flow.
    - refactor: improving or changing code structure.
    - debug: fixing errors or issues.
    - impact_analysis: assessing the effect of changes.
    - general: generic questions.
    
    Return ONLY the category name.
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "{query}")
    ])
    
    try:
        chain = prompt | llm
        result = chain.invoke({"query": query})
        intent = result.content.strip().lower()
        print(f"✅ Intent Classified: '{intent}'")
    except Exception as e:
        print(f"⚠️  Intent Classification Failed (likely API Quota/Error): {e}")
        print(f"🔄 Defaulting to 'general' intent")
        intent = "general"
    print("="*80 + "\n")
    
    return {"intent": intent}

def create_intent_subgraph():
    workflow = StateGraph(GlobalState)
    workflow.add_node("analyze_intent", analyze_intent)
    workflow.set_entry_point("analyze_intent")
    workflow.add_edge("analyze_intent", END)
    return workflow.compile()
