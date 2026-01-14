from langgraph.graph import StateGraph, END
from agentic_copilot.schemas.state import GlobalState
import pandas as pd
import os
import glob
# Removed broken graphrag internal imports. We rely on CLI or standard LangChain if needed.
import tiktoken
from dotenv import load_dotenv

load_dotenv()

# Configuration
INPUT_DIR = "c:/Users/202317/Graph Knowledge/GraphRag/ragtest/output"
COMMUNITY_LEVEL = 2
API_KEY = os.environ.get("GRAPHRAG_API_KEY")
LLM_MODEL = "gpt-4o"
EMBEDDING_MODEL = "text-embedding-3-small"

def get_latest_output_dir():
    # 1. Check if artifacts exist directly in INPUT_DIR (Flat structure)
    if os.path.exists(os.path.join(INPUT_DIR, "entities.parquet")):
        print(f"DEBUG: Found artifacts directly in {INPUT_DIR}")
        return INPUT_DIR

    # 2. Find the latest timestamped directory in output
    search_path = os.path.join(INPUT_DIR, "*")
    dirs = [d for d in glob.glob(search_path) if os.path.isdir(d)]
    if not dirs:
        return None
    
    latest = max(dirs, key=os.path.getmtime)
    print(f"DEBUG: Found latest artifact dir: {latest}")
    return latest

def select_search_method(state: GlobalState):
    """
    Use GPT-4 to intelligently select search method based on intent and query.
    
    Returns: "local", "global", or "community"
    """
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    
    intent = state.get("intent", "general")
    query = state.get("user_query", "")
    
    print("\n" + "="*80)
    print("🔍 SEARCH METHOD SELECTOR - Choosing Best Method")
    print("="*80)
    print(f"📝 Query: '{query}'")
    print(f"🎯 Intent: '{intent}'")
    print("🤖 Asking GPT-4 Mini to select optimal search method...")
    
    # Use GPT-4 to determine best search method
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)  # Use mini for speed
    
    system_prompt = """You are a search method selector for a code analysis system.

Given a user query and their intent, select the BEST GraphRAG search method:

**LOCAL**: For specific, detailed questions about particular functions, classes, or code snippets
- Examples: "How does the login function work?", "What does authenticate() do?", "Give me the code for AccountSlackNotifyJob"
- Use when: User asks about specific code elements, file logic, or asks to see the "full code" or "implementation"

**GLOBAL**: For broad, high-level questions about overall architecture or system design
- Examples: "What is the architecture?", "What are all the components?", "Summarize the project"
- Use when: User wants overview, architecture, or system-wide information. DO NOT use for specific file/class lookups.

**COMMUNITY**: For questions about specific modules, packages, or subsystems
- Examples: "How does the auth module work?", "Explain the payment system"
- Use when: User asks about a module, layer, or subsystem (not a single function)

Respond with ONLY one word: "local", "global", or "community"
"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", """Query: {query}
Intent: {intent}

Which search method should be used?""")
    ])
    
    chain = prompt | llm
    result = chain.invoke({
        "query": query,
        "intent": intent
    })
    
    # Extract method from response
    method = result.content.strip().lower()
    
    # Validate response
    if method not in ["local", "global", "community"]:
        print(f"⚠️  Warning: GPT-4 returned invalid method '{method}', defaulting to 'local'")
        method = "local"
    
    print(f"✅ Selected Method: '{method.upper()}'")
    print(f"💡 Reasoning: {method.upper()} search is best for this type of query")
    print("="*80 + "\n")
    
    return method


def lookup_source_code(query, output_dir):
    """
    Attempts to find raw source code by matching entity names in the query.
    Returns: content string or None
    """
    try:
        # Simple extraction of "potential entity names" from query
        # This is a heuristic: look for capitalized words or words with .cls, .js etc.
        import re
        
        # 1. Extract potential targets
        # Remove common phrases
        clean_query = query.lower()
        for phrase in ["give me", "full code", "source code", "implementation", "show me", " for "]:
            clean_query = clean_query.replace(phrase, " ")
            
        import re
        # Split by whitespace
        raw_keywords = [w.strip() for w in re.split(r'\s+', clean_query) if len(w) > 2]
        
        keywords = []
        for kw in raw_keywords:
            # Strip extensions if present
            base_kw = os.path.splitext(kw)[0]
            keywords.append(base_kw)
            # Also keep original if it was different, just in case
            if base_kw != kw:
                keywords.append(kw)
        
        print(f"DEBUG: Lookup Keywords: {keywords}")
        
        if not keywords: return None
        
        entities_path = os.path.join(output_dir, "entities.parquet")
        text_units_path = os.path.join(output_dir, "text_units.parquet")
        
        if not os.path.exists(entities_path) or not os.path.exists(text_units_path):
            return None
            
        df_entities = pd.read_parquet(entities_path)
        
        # Search for best match
        target_entity = None
        for kw in keywords:
            # Try exact match first (case insensitive)
            match = df_entities[df_entities['title'].str.lower() == kw.lower()]
            if not match.empty:
                target_entity = match.iloc[0]
                break
                
            # Try contains
            match = df_entities[df_entities['title'].str.contains(kw, case=False, na=False)]
            if not match.empty:
                target_entity = match.iloc[0]  # Take first match
                break
        
        if target_entity is None:
            return None
            
        # Get Text Units
        ids = target_entity['text_unit_ids']
        if not isinstance(ids, list) and not hasattr(ids, '__iter__'):
             ids = [ids]
             
        if not ids: return None
        
        # Load Text Units
        df_text = pd.read_parquet(text_units_path)
        sources = df_text[df_text['id'].isin(ids)]
        
        if sources.empty: return None
        
        # Construct Output
        content = f"**Source Code Retrieved for {target_entity['title']}**\n\n"
        for _, row in sources.iterrows():
            content += f"{row['text']}\n\n"
            
        return content

    except Exception as e:
        print(f"Direct lookup failed: {e}")
        return None

def reason_over_code(state: GlobalState):
    query = state["user_query"]
    output_dir = get_latest_output_dir()
    
    print("\n" + "="*80)
    print("📊 GRAPHRAG AGENT - Hybrid Search (Direct Parquet + GraphRAG)")
    print("="*80)
    
    if not output_dir:
        print("❌ Error: No GraphRAG output directory found")
        print("="*80 + "\n")
        return {"graphrag_context": ["Error: No GraphRAG output directory found. Please run indexing first."]}
    
    print(f"🔎 Step 1: Direct parquet search for exact matches...")
    
    # Get direct parquet results
    direct_result = direct_parquet_query(query, output_dir)
    
    print(f"🔎 Step 2: GraphRAG LOCAL search for semantic context...")
    
    # Also get GraphRAG CLI results for richer context (using LOCAL search which is more grounded)
    cli_result = CLI_query(query, output_dir, method="local")
    
    # Combine both results
    combined_context = []
    
    # Add direct parquet results first (most reliable)
    if direct_result.get("graphrag_context"):
        combined_context.append("## Direct Parquet Matches (Exact Data)\n")
        combined_context.extend(direct_result["graphrag_context"])
        combined_context.append("\n---\n")
    
    # Add GraphRAG CLI results (semantic search)
    if cli_result.get("graphrag_context"):
        combined_context.append("## GraphRAG Semantic Analysis\n")
        combined_context.extend(cli_result["graphrag_context"])
    
    result = {"graphrag_context": combined_context}
    
    # Preview
    if combined_context:
        preview = str(combined_context[0])[:200].replace('\n', ' ')
        print(f"✅ Hybrid Results: {preview}...")
    
    print("="*80 + "\n")
    return result

def CLI_query(query, output_dir, method="local"):
    """
    Calls GraphRAG CLI with strict prompt to minimize hallucinations.
    Using LOCAL search which is more grounded in actual data.
    """
    import subprocess
    from dotenv import load_dotenv
    
    try:
        # Load environment variables from .env file
        load_dotenv()
        
        root_path = "ragtest"
        cmd = ["graphrag", "query", "--root", root_path, "--method", method, "--query", query]
        
        # Get environment with loaded .env variables
        env = os.environ.copy()
        
        # Ensure required keys are present
        if not env.get('GRAPHRAG_API_KEY') and not env.get('OPENAI_API_KEY'):
            return {"graphrag_context": ["GraphRAG CLI error: GRAPHRAG_API_KEY or OPENAI_API_KEY not found in environment"]}
        
        result = subprocess.run(cmd, capture_output=True, text=True, env=env, encoding='utf-8', errors='replace')
        
        if result.returncode != 0:
             return {"graphrag_context": [f"GraphRAG CLI error: {result.stderr}"]}
             
        return {"graphrag_context": [result.stdout]}
        
    except Exception as e:
        import traceback
        return {"graphrag_context": [f"GraphRAG CLI exception: {str(e)}\n{traceback.format_exc()}"]}

def direct_parquet_query(query, output_dir):
    """
    Directly reads parquet files and returns matching data WITHOUT any LLM synthesis.
    This prevents hallucinations by returning ONLY indexed data.
    """
    try:
        entities_path = os.path.join(output_dir, "entities.parquet")
        text_units_path = os.path.join(output_dir, "text_units.parquet")
        relationships_path = os.path.join(output_dir, "relationships.parquet")
        
        if not os.path.exists(entities_path):
            return {"graphrag_context": ["Error: entities.parquet not found. Please run indexing first."]}
        
        # Read parquet files
        df_entities = pd.read_parquet(entities_path)
        
        # Extract keywords from query
        import re
        query_lower = query.lower()
        # Remove common words
        for phrase in ["give me", "full code", "source code", "implementation", "show me", "what is", "how does", "explain", "why"]:
            query_lower = query_lower.replace(phrase, " ")
        
        keywords = [w.strip() for w in re.split(r'\s+', query_lower) if len(w) > 2]
        
        # Filter out common stop words
        stop_words = {'the', 'is', 'are', 'was', 'were', 'about', 'this', 'that', 'with', 'for', 'and', 'or', 'but', 'not', 'can', 'will', 'from', 'has', 'have', 'had', 'does', 'did', 'why', 'what', 'how', 'when', 'where', 'who'}
        keywords = [kw for kw in keywords if kw not in stop_words]
        
        print(f"DEBUG: Search keywords: {keywords}")
        
        if not keywords:
            return {"graphrag_context": ["No valid search terms found in query."]}
        
        # Search for matching entities
        matching_entities = []
        for kw in keywords:
            try:
                # Search in entity titles (case-insensitive)
                if 'title' in df_entities.columns:
                    matches = df_entities[df_entities['title'].astype(str).str.contains(kw, case=False, na=False)]
                    if not matches.empty:
                        matching_entities.extend(matches.to_dict('records'))
            except Exception as e:
                print(f"DEBUG: Error searching titles for '{kw}': {e}")
        
        # Also search in descriptions
        for kw in keywords:
            try:
                if 'description' in df_entities.columns:
                    # Convert description to string first (it might be a list/array)
                    desc_series = df_entities['description'].apply(lambda x: str(x) if x is not None else "")
                    matches = df_entities[desc_series.str.contains(kw, case=False, na=False)]
                    if not matches.empty:
                        matching_entities.extend(matches.to_dict('records'))
            except Exception as e:
                print(f"DEBUG: Error searching descriptions for '{kw}': {e}")
        
        # Remove duplicates
        seen_ids = set()
        unique_entities = []
        for entity in matching_entities:
            if entity['id'] not in seen_ids:
                seen_ids.add(entity['id'])
                unique_entities.append(entity)
        
        if not unique_entities:
            return {"graphrag_context": [f"No entities found in parquet files matching: {', '.join(keywords)}"]}
        
        # Build response from matched entities
        response = "# Direct Parquet Query Results\n\n"
        response += f"**Search Keywords:** {', '.join(keywords)}\n"
        response += f"**Entities Found:** {len(unique_entities)}\n\n"
        
        # Load text units if available
        df_text = None
        if os.path.exists(text_units_path):
            df_text = pd.read_parquet(text_units_path)
        
        for i, entity in enumerate(unique_entities[:10], 1):  # Limit to top 10
            response += f"## {i}. {entity.get('title', 'Unknown')}\n\n"
            
            # Add description
            if entity.get('description'):
                response += f"**Description:** {entity['description']}\n\n"
            
            # Add type
            if entity.get('type'):
                response += f"**Type:** {entity['type']}\n\n"
            
            # Get associated text units (source code)
            if df_text is not None and entity.get('text_unit_ids') is not None:
                text_ids = entity['text_unit_ids']
                
                # Robustly convert to list
                if hasattr(text_ids, 'tolist'):  # numpy array
                    text_ids = text_ids.tolist()
                elif isinstance(text_ids, str):  # single id as string
                    text_ids = [text_ids]
                elif not isinstance(text_ids, list): # other iterable
                     # try to iterate, if not possible make single list
                     try:
                         text_ids = list(text_ids)
                     except:
                         text_ids = [text_ids]

                matching_texts = df_text[df_text['id'].isin(text_ids)]
                if not matching_texts.empty:
                    response += "**Source Code/Text:**\n\n"
                    for _, text_row in matching_texts.iterrows():
                        response += f"```\n{text_row['text']}\n```\n\n"
            
            response += "---\n\n"
        
        if len(unique_entities) > 10:
            response += f"\n*Showing 10 of {len(unique_entities)} results. Refine your query for more specific results.*\n"
        
        return {"graphrag_context": [response]}
        
    except Exception as e:
        import traceback
        error_msg = f"Error reading parquet files: {str(e)}\n{traceback.format_exc()}"
        return {"graphrag_context": [error_msg]}


def create_graphrag_subgraph():
    workflow = StateGraph(GlobalState)
    workflow.add_node("reason_over_code", reason_over_code)
    workflow.set_entry_point("reason_over_code")
    workflow.add_edge("reason_over_code", END)
    return workflow.compile()
