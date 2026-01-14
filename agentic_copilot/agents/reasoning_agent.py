from agentic_copilot.schemas.state import GlobalState

def final_reasoning(state: GlobalState):
    """
    Returns raw data from parquet files WITHOUT any LLM synthesis to prevent hallucinations.
    """
    intent = state.get("intent", "general")
    query = state.get("user_query", "")
    rag_data = state.get("rag_context", [])
    code_data = state.get("graphrag_context", [])
    tool_data = state.get("tool_results", [])
    risks = state.get("risk_signals", [])
    
    print("\n" + "="*80)
    print("🎨 FINAL REASONING AGENT - Raw Data Passthrough (NO LLM SYNTHESIS)")
    print("="*80)
    print(f"📝 Query: '{query}'")
    print(f"🎯 Intent: '{intent}'")
    print(f"📚 Context Sources:")
    print(f"   - RAG Data: {len(rag_data)} items")
    print(f"   - Code Data: {len(code_data)} items")
    print(f"   - Tool Results: {len(tool_data)} items")
    print(f"   - Risk Signals: {len(risks)} items")
    print("⚠️  NO LLM PROCESSING - Returning raw parquet data only")
    
    # Build response from raw data WITHOUT any LLM processing
    response_parts = []
    
    # Add a header
    response_parts.append("# Query Results from Indexed Data\n")
    response_parts.append(f"**Query:** {query}\n")
    
    if code_data:
        response_parts.append("\n## GraphRAG Code Analysis Results\n")
        for item in code_data:
            if isinstance(item, str):
                # Show actual errors for debugging (don't hide them)
                response_parts.append(item + "\n")
    
    if rag_data:
        response_parts.append("\n## Documentation Context\n")
        for item in rag_data:
            response_parts.append(f"{item}\n")
    
    if tool_data:
        response_parts.append("\n## Tool Results\n")
        for item in tool_data:
            response_parts.append(f"{item}\n")
    
    if risks:
        response_parts.append("\n## Risk Signals\n")
        for item in risks:
            response_parts.append(f"{item}\n")
    
    if not response_parts or len(response_parts) <= 2:  # Only header
        final_response = "No data found in the indexed parquet files for this query."
    else:
        final_response = "\n".join(response_parts)
    
    # DEBUG: Print the full response to verify content
    print("DEBUG: FULL RESPONSE CONTENT START")
    print(final_response)
    print("DEBUG: FULL RESPONSE CONTENT END")
    
    print(f"✅ Raw Data Response: {len(final_response)} characters")
    print("="*80 + "\n")
    
    return {"final_answer": final_response}
