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
    
    system_prompt = """You are a search method selector for a Salesforce code analysis system.

Given a user query and their intent, select the BEST GraphRAG search method:

**LOCAL**: For specific, detailed questions about particular functions, classes, or code snippets
- Examples: "How does the login function work?", "What does authenticate() do?", "Give me the code for AccountSlackNotifyJob"
- Use when: User asks about specific code elements, file logic, or asks to see the "full code" or "implementation"

**COMMUNITY**: For questions about project features, capabilities, or what the codebase does
- Examples: "What is the project about?", "What are the key features?", "What does this system do?", "What functionality is available?"
- Use when: User wants to understand the business purpose, features, or capabilities of the codebase

**GLOBAL**: For broad architectural questions or system-wide technical design
- Examples: "What is the technical architecture?", "How are components organized?", "What design patterns are used?"
- Use when: User asks about architecture, technical design, or system-wide structure (NOT business features)

IMPORTANT: 
- "What is the project about" = COMMUNITY (features/capabilities)
- "What is the architecture" = GLOBAL (technical design)
- "How does X work" = LOCAL (specific implementation)

Respond with ONLY one word: "local", "global", or "community"
"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", """Query: {query}
Intent: {intent}

Which search method should be used?""")
    ])
    
    try:
        chain = prompt | llm
        result = chain.invoke({
            "query": query,
            "intent": intent
        })
        
        # Extract method from response
        method = result.content.strip().lower()
        
        # Validate response
        if method not in ["local", "global", "community"]:
            print(f"⚠️  Warning: GPT-4 returned invalid method '{method}', defaulting to 'community'")
            method = "community"
            
        print(f"✅ Selected Method: '{method.upper()}'")
        print(f"💡 Reasoning: {method.upper()} search is best for this type of query")
    except Exception as e:
        print(f"⚠️  Search Method Selection Failed: {e}")
        print("🔄 Defaulting to 'local' search (safest option)")
        method = "local"

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

def classify_query_type(query):
    """
    Use LLM to classify the query type instead of hardcoded phrase matching.
    Returns: dict with 'type' and 'entity_type'
    """
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    import json
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a query classifier for a Salesforce codebase analysis system.

Classify the user's query into ONE of these types:

1. **list_all**: User wants a complete list of entities
   - Examples: "what all apex classes", "list all test classes", "give me all XML files"
   - Entity types: apex_class, test_class, xml, sobject, lwc, trigger, method, field

2. **project_overview**: User wants to understand what the project does
   - Examples: "what is this project about", "key features", "what does this do"

3. **specific_query**: User asks about specific implementation or how something works
   - Examples: "how does SlackNotifier work", "what objects does X use"

Respond with JSON only:
{
  "type": "list_all" | "project_overview" | "specific_query",
  "entity_type": "apex_class" | "test_class" | "xml" | "sobject" | "lwc" | "trigger" | null
}"""),
        ("user", "Query: {query}")
    ])
    
    try:
        result = llm.invoke(prompt.format_messages(query=query))
        classification = json.loads(result.content.strip())
        return classification
    except Exception as e:
        print(f"⚠️  Query Classification Failed: {e}")
        # Fallback to specific_query if classification fails
        return {"type": "specific_query", "entity_type": None}

def reason_over_code(state: GlobalState):
    """
    Universal hybrid search - always combines direct parquet + GraphRAG.
    No hardcoded routing - LLM in final_reasoning handles all formatting.
    """
    query = state["user_query"]
    output_dir = get_latest_output_dir()
    
    print("\n" + "="*80)
    print("📊 GRAPHRAG AGENT - Universal Hybrid Search")
    print("="*80)
    
    if not output_dir:
        print("❌ Error: No GraphRAG output directory found")
        print("="*80 + "\n")
        return {"graphrag_context": ["Error: No GraphRAG output directory found. Please run indexing first."]}
    
    # Step 1: Direct parquet search
    print(f"🔎 Step 1: Direct parquet search...")
    direct_result = direct_parquet_query(query, output_dir)
    
    # Step 2: Dynamically select GraphRAG search method
    search_method = select_search_method(state)
    print(f"🔎 Step 2: GraphRAG {search_method.upper()} search...")
    cli_result = CLI_query(query, output_dir, method=search_method)
    
    # Combine results
    combined_context = []
    
    if direct_result.get("graphrag_context"):
        combined_context.extend(direct_result["graphrag_context"])
    
    if cli_result.get("graphrag_context"):
        combined_context.extend(cli_result["graphrag_context"])
    
    result = {"graphrag_context": combined_context}
    
    if combined_context:
        preview = str(combined_context[0])[:150].replace('\n', ' ')
        print(f"✅ Results collected: {len(combined_context)} items")
        print(f"   Preview: {preview}...")
    
    print("="*80 + "\n")
    return result
    query = state["user_query"]
    output_dir = get_latest_output_dir()
    
    print("\n" + "="*80)
    print("📊 GRAPHRAG AGENT - Intelligent Query Routing")
    print("="*80)
    
    if not output_dir:
        print("❌ Error: No GraphRAG output directory found")
        print("="*80 + "\n")
        return {"graphrag_context": ["Error: No GraphRAG output directory found. Please run indexing first."]}
    
    # Classify query using LLM
    print("🤖 Classifying query type...")
    classification = classify_query_type(query)
    query_type = classification.get("type", "specific_query")
    entity_type = classification.get("entity_type")
    
    print(f"✅ Query Type: {query_type}")
    if entity_type:
        print(f"   Entity Type: {entity_type}")
    
    # Route based on classification
    if query_type == "list_all":
        print("📋 Routing to: Complete List Handler")
        result = get_complete_list(query, entity_type, output_dir)
        print("="*80 + "\n")
        return result
    
    elif query_type == "project_overview":
        print("🎯 Routing to: Project Overview Handler")
        result = get_project_overview(output_dir)
        print("="*80 + "\n")
        return result
    
    else:  # specific_query
        print("🔍 Routing to: Hybrid Search (Parquet + GraphRAG)")
        
        print(f"🔎 Step 1: Direct parquet search for exact matches...")
        direct_result = direct_parquet_query(query, output_dir)
        
        # Dynamically select search method
        search_method = select_search_method(state)
        
        print(f"🔎 Step 2: GraphRAG {search_method.upper()} search for semantic context...")
        cli_result = CLI_query(query, output_dir, method=search_method)
        
        # Combine results
        combined_context = []
        
        if direct_result.get("graphrag_context"):
            combined_context.append("## Direct Parquet Matches (Exact Data)\n")
            combined_context.extend(direct_result["graphrag_context"])
            combined_context.append("\n---\n")
        
        if cli_result.get("graphrag_context"):
            combined_context.append(f"## GraphRAG {search_method.upper()} Search Results\n")
            combined_context.extend(cli_result["graphrag_context"])
        
        result = {"graphrag_context": combined_context}
        
        if combined_context:
            preview = str(combined_context[0])[:200].replace('\n', ' ')
            print(f"✅ Hybrid Results: {preview}...")
        
        print("="*80 + "\n")
        return result

def get_complete_list(query, entity_type, output_dir):
    """
    Handler for "list all X" questions - returns COMPLETE lists without truncation.
    Uses LLM-provided entity_type instead of hardcoded matching.
    """
    try:
        entities_path = os.path.join(output_dir, "entities.parquet")
        df_entities = pd.read_parquet(entities_path)
        
        response = "# Complete Entity List\n\n"
        
        # Map entity_type to actual filtering logic
        if entity_type == "apex_class":
            entities = df_entities[df_entities['type'] == 'APEX_CLASS']
            response += f"## All Apex Classes ({len(entities)} total)\n\n"
        
        elif entity_type == "test_class":
            entities = df_entities[
                (df_entities['type'] == 'APEX_CLASS') & 
                (df_entities['title'].str.contains('Test', case=False, na=False))
            ]
            response += f"## All Test Classes ({len(entities)} total)\n\n"
        
        elif entity_type == "xml":
            entities = df_entities[
                (df_entities['title'].str.contains('XML|CUSTOMOBJECT|ALLOW_IN', case=False, na=False)) |
                (df_entities['type'].str.contains('XML', case=False, na=False))
            ]
            response += f"## All XML/Metadata Files ({len(entities)} total)\n\n"
        
        elif entity_type == "sobject":
            entities = df_entities[df_entities['type'] == 'SOBJECT']
            response += f"## All Salesforce Objects ({len(entities)} total)\n\n"
        
        elif entity_type == "lwc":
            entities = df_entities[df_entities['type'] == 'LWC_COMPONENT']
            response += f"## All Lightning Web Components ({len(entities)} total)\n\n"
        
        elif entity_type == "trigger":
            entities = df_entities[df_entities['type'].str.contains('TRIGGER', case=False, na=False)]
            response += f"## All Triggers ({len(entities)} total)\n\n"
        
        elif entity_type == "method":
            entities = df_entities[df_entities['type'] == 'METHOD']
            response += f"## All Methods ({len(entities)} total)\n\n"
        
        elif entity_type == "field":
            entities = df_entities[df_entities['type'] == 'FIELD']
            response += f"## All Fields ({len(entities)} total)\n\n"
        
        else:
            # Fallback: show all entity types
            response += "## All Entities by Type\n\n"
            type_counts = df_entities['type'].value_counts()
            for etype, count in type_counts.items():
                if pd.notna(etype) and etype:
                    response += f"### {etype} ({count} items)\n"
                    entities_of_type = df_entities[df_entities['type'] == etype]
                    for _, entity in entities_of_type.head(20).iterrows():
                        response += f"- {entity['title']}\n"
                    if count > 20:
                        response += f"  *(and {count - 20} more...)*\n"
                    response += "\n"
            return {"graphrag_context": [response]}
        
        # Add entities to response
        for _, entity in entities.iterrows():
            desc = entity.get('description', '')
            if desc:
                response += f"- **{entity['title']}**: {desc}\n"
            else:
                response += f"- **{entity['title']}**\n"
        
        return {"graphrag_context": [response]}
        
    except Exception as e:
        import traceback
        return {"graphrag_context": [f"Error getting complete list: {str(e)}\n{traceback.format_exc()}"]}
    query = state["user_query"]
    output_dir = get_latest_output_dir()
    
    print("\n" + "="*80)
    print("📊 GRAPHRAG AGENT - Hybrid Search (Direct Parquet + GraphRAG)")
    print("="*80)
    
    if not output_dir:
        print("❌ Error: No GraphRAG output directory found")
        print("="*80 + "\n")
        return {"graphrag_context": ["Error: No GraphRAG output directory found. Please run indexing first."]}
    
    # Special handling for "list all" questions
    is_list_all = any(phrase in query.lower() for phrase in 
                     ["what all", "list all", "all the", "give me all", "show me all", 
                      "name of all", "all apex", "all test", "all xml", "all lwc"])
    
    if is_list_all:
        print("📋 'List All' Question Detected - Querying Complete Entity Lists")
        result = get_complete_list(query, output_dir)
        print("="*80 + "\n")
        return result
    
    # Special handling for project overview questions
    is_project_overview = any(phrase in query.lower() for phrase in 
                              ["what is the project", "what does this project", "key features", 
                               "what functionality", "what capabilities", "project about"])
    
    if is_project_overview:
        print("🎯 Project Overview Question Detected - Using Business Entity Query")
        result = get_project_overview(output_dir)
        print("="*80 + "\n")
        return result
    
    print(f"🔎 Step 1: Direct parquet search for exact matches...")
    
    # Get direct parquet results
    direct_result = direct_parquet_query(query, output_dir)
    
    # Dynamically select search method based on query
    search_method = select_search_method(state)
    
    print(f"🔎 Step 2: GraphRAG {search_method.UPPER()} search for semantic context...")
    
    # Get GraphRAG CLI results with selected method
    cli_result = CLI_query(query, output_dir, method=search_method)
    
    # Combine both results
    combined_context = []
    
    # Add direct parquet results first (most reliable)
    if direct_result.get("graphrag_context"):
        combined_context.append("## Direct Parquet Matches (Exact Data)\n")
        combined_context.extend(direct_result["graphrag_context"])
        combined_context.append("\n---\n")
    
    # Add GraphRAG CLI results (semantic search)
    if cli_result.get("graphrag_context"):
        combined_context.append(f"## GraphRAG {search_method.upper()} Search Results\n")
        combined_context.extend(cli_result["graphrag_context"])
    
    result = {"graphrag_context": combined_context}
    
    # Preview
    if combined_context:
        preview = str(combined_context[0])[:200].replace('\n', ' ')
        print(f"✅ Hybrid Results: {preview}...")
    
    print("="*80 + "\n")
    return result

def get_complete_list(query, output_dir):
    """
    Handler for "list all X" questions - returns COMPLETE lists without truncation.
    """
    try:
        entities_path = os.path.join(output_dir, "entities.parquet")
        df_entities = pd.read_parquet(entities_path)
        
        query_lower = query.lower()
        response = "# Complete Entity List\n\n"
        
        # Detect what type of list is requested
        if "apex class" in query_lower or "apexclass" in query_lower:
            apex_classes = df_entities[df_entities['type'] == 'APEX_CLASS']
            response += f"## All Apex Classes ({len(apex_classes)} total)\n\n"
            for _, cls in apex_classes.iterrows():
                desc = cls.get('description', '')
                if desc:
                    response += f"- **{cls['title']}**: {desc}\n"
                else:
                    response += f"- **{cls['title']}**\n"
        
        elif "test class" in query_lower or "test" in query_lower:
            # Filter for test classes (usually contain "Test" in name)
            test_classes = df_entities[
                (df_entities['type'] == 'APEX_CLASS') & 
                (df_entities['title'].str.contains('Test', case=False, na=False))
            ]
            response += f"## All Test Classes ({len(test_classes)} total)\n\n"
            for _, cls in test_classes.iterrows():
                desc = cls.get('description', '')
                if desc:
                    response += f"- **{cls['title']}**: {desc}\n"
                else:
                    response += f"- **{cls['title']}**\n"
        
        elif "xml" in query_lower:
            # XML-related entities (CustomObject, metadata files)
            xml_entities = df_entities[
                (df_entities['title'].str.contains('XML|CUSTOMOBJECT|ALLOW_IN', case=False, na=False)) |
                (df_entities['type'].str.contains('XML', case=False, na=False))
            ]
            response += f"## All XML/Metadata Files ({len(xml_entities)} total)\n\n"
            for _, entity in xml_entities.iterrows():
                desc = entity.get('description', '')
                if desc:
                    response += f"- **{entity['title']}** ({entity.get('type', 'Unknown')}): {desc}\n"
                else:
                    response += f"- **{entity['title']}** ({entity.get('type', 'Unknown')})\n"
        
        elif "sobject" in query_lower or "object" in query_lower:
            sobjects = df_entities[df_entities['type'] == 'SOBJECT']
            response += f"## All Salesforce Objects ({len(sobjects)} total)\n\n"
            for _, obj in sobjects.iterrows():
                desc = obj.get('description', '')
                if desc:
                    response += f"- **{obj['title']}**: {desc}\n"
                else:
                    response += f"- **{obj['title']}**\n"
        
        elif "lwc" in query_lower or "component" in query_lower:
            lwc = df_entities[df_entities['type'] == 'LWC_COMPONENT']
            response += f"## All Lightning Web Components ({len(lwc)} total)\n\n"
            for _, comp in lwc.iterrows():
                desc = comp.get('description', '')
                if desc:
                    response += f"- **{comp['title']}**: {desc}\n"
                else:
                    response += f"- **{comp['title']}**\n"
        
        elif "trigger" in query_lower:
            triggers = df_entities[df_entities['type'].str.contains('TRIGGER', case=False, na=False)]
            response += f"## All Triggers ({len(triggers)} total)\n\n"
            for _, trig in triggers.iterrows():
                desc = trig.get('description', '')
                if desc:
                    response += f"- **{trig['title']}**: {desc}\n"
                else:
                    response += f"- **{trig['title']}**\n"
        
        else:
            # Generic "all" - show summary by type
            response += "## All Entities by Type\n\n"
            type_counts = df_entities['type'].value_counts()
            for entity_type, count in type_counts.items():
                if pd.notna(entity_type) and entity_type:
                    response += f"### {entity_type} ({count} items)\n"
                    entities_of_type = df_entities[df_entities['type'] == entity_type]
                    for _, entity in entities_of_type.head(20).iterrows():  # Limit to 20 per type for readability
                        response += f"- {entity['title']}\n"
                    if count > 20:
                        response += f"  *(and {count - 20} more...)*\n"
                    response += "\n"
        
        return {"graphrag_context": [response]}
        
    except Exception as e:
        import traceback
        return {"graphrag_context": [f"Error getting complete list: {str(e)}\n{traceback.format_exc()}"]}


def get_project_overview(output_dir):
    """
    Special handler for project overview questions.
    Queries business-relevant entities directly instead of using GraphRAG CLI.
    """
    try:
        entities_path = os.path.join(output_dir, "entities.parquet")
        df_entities = pd.read_parquet(entities_path)
        
        # Get business-relevant entities
        apex_classes = df_entities[df_entities['type'] == 'APEX_CLASS']
        sobjects = df_entities[df_entities['type'] == 'SOBJECT']
        lwc_components = df_entities[df_entities['type'] == 'LWC_COMPONENT']
        
        response = "# Project Overview - Business Features\n\n"
        
        if not apex_classes.empty:
            response += "## Apex Classes (Business Logic)\n"
            for _, cls in apex_classes.head(10).iterrows():
                response += f"- **{cls['title']}**: {cls.get('description', 'No description')}\n"
            response += "\n"
        
        if not sobjects.empty:
            response += "## Salesforce Objects (Data Model)\n"
            for _, obj in sobjects.head(10).iterrows():
                response += f"- **{obj['title']}**: {obj.get('description', 'No description')}\n"
            response += "\n"
        
        if not lwc_components.empty:
            response += "## Lightning Web Components (UI)\n"
            for _, comp in lwc_components.head(10).iterrows():
                response += f"- **{comp['title']}**: {comp.get('description', 'No description')}\n"
            response += "\n"
        
        return {"graphrag_context": [response]}
        
    except Exception as e:
        import traceback
        return {"graphrag_context": [f"Error getting project overview: {str(e)}\n{traceback.format_exc()}"]}

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
        
        # INTELLIGENT OVERVIEW HANDLING:
        # If query is generic (e.g. "what is the project", "overview") or if keywords are weak,
        # we explicitly fetch business entities to give the LLM something to summarize.
        is_overview = any(phrase in query.lower() for phrase in 
                         ["project", "overview", "what is this", "features", "capabilities", "functionality"])
        
        if is_overview or len(unique_entities) < 3:
            print("DEBUG: Detected overview/generic query - fetching business entities...")
            try:
                # Fetch sample business entities to augment results
                business_types = ['APEX_CLASS', 'SOBJECT', 'LWC_COMPONENT']
                for b_type in business_types:
                    # Get top 10 of each type
                    sample = df_entities[df_entities['type'] == b_type].head(10).to_dict('records')
                    for entity in sample:
                        if entity['id'] not in seen_ids:
                            seen_ids.add(entity['id'])
                            unique_entities.append(entity)
            except Exception as e:
                print(f"DEBUG: Error fetching business samples: {e}")
        
        # CRITICAL: Filter out Salesforce DX configuration noise
        # These are infrastructure/setup entities, not business features
        config_noise_patterns = [
            'SFDX_PROJECT', 'DX_PROJECT', 'SALESFORCE_DX',
            'SOURCEAPIVERSION', 'PATH', 'DEFAULT',
            'PACKAGE_DIRECTORIES', 'NAMESPACE', 'SFDX',
            'JEST_CONFIG', 'HUSKY', 'LINT', 'PRETTIER'
        ]
        
        business_entities = []
        for entity in unique_entities:
            title = str(entity.get('title', '')).upper()
            # Skip if title matches configuration patterns
            if not any(pattern in title for pattern in config_noise_patterns):
                business_entities.append(entity)
            else:
                print(f"DEBUG: Filtered out config entity: {entity.get('title')}")
        
        unique_entities = business_entities
        
        if not unique_entities:
            return {"graphrag_context": [f"No business entities found matching: {', '.join(keywords)}"]}
        
        # Build response from matched entities
        response = "# Direct Parquet Query Results\n\n"
        response += f"**Search Keywords:** {', '.join(keywords)}\n"
        response += f"**Entities Found:** {len(unique_entities)}\n\n"
        
        # Load text units if available
        df_text = None
        if os.path.exists(text_units_path):
            df_text = pd.read_parquet(text_units_path)
        
        for i, entity in enumerate(unique_entities, 1):  # Return ALL entities
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
        
        # Note: No longer showing "X of Y results" message since we return ALL
        
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
