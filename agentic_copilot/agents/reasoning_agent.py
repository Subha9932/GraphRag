from agentic_copilot.schemas.state import GlobalState
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os

def final_reasoning(state: GlobalState):
    """
    Universal query handler using comprehensive LLM prompt - NO hardcoding.
    """
    intent = state.get("intent", "general")
    query = state.get("user_query", "")
    rag_data = state.get("rag_context", [])
    code_data = state.get("graphrag_context", [])
    tool_data = state.get("tool_results", [])
    risks = state.get("risk_signals", [])
    
    print("\n" + "="*80)
    print("🎨 FINAL REASONING AGENT - Universal Query Handler")
    print("="*80)
    print(f"📝 Query: '{query}'")
    print(f"🎯 Intent: '{intent}'")
    print(f"📚 Context Sources:")
    print(f"   - RAG Data: {len(rag_data)} items")
    print(f"   - Code Data: {len(code_data)} items")
    print(f"   - Tool Results: {len(tool_data)} items")
    print(f"   - Risk Signals: {len(risks)} items")
    
    # Build context for LLM
    context_parts = []
    
    if code_data:
        context_parts.append("**Code Analysis Data:**\n" + "\n".join([str(c) for c in code_data]))
    
    if rag_data:
        context_parts.append("**Documentation:**\n" + "\n".join([str(d) for d in rag_data]))
    
    if tool_data:
        context_parts.append("**Tool Results:**\n" + "\n".join([str(t) for t in tool_data]))
    
    if risks:
        context_parts.append("**Risk Signals:**\n" + "\n".join([str(r) for r in risks]))
    
    all_context = "\n\n".join(context_parts) if context_parts else "No data available."
    
    print(f"🤖 Processing with GPT-4 using universal prompt...")
    
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an elite Salesforce Solutions Architect with 10+ years of experience analyzing enterprise Salesforce implementations.

**YOUR EXPERTISE:**
You deeply understand Salesforce architecture and can distinguish between:
- **Business Features** (what the system DOES for users)
- **Configuration Boilerplate** (sfdx-project.json, package.xml, metadata files)
- **Technical Infrastructure** (DX setup, deployment scripts, build tools)

**CRITICAL FILTERING RULES:**
When analyzing a Salesforce project, IGNORE and DO NOT mention:
- ❌ "Salesforce DX project configuration" (this is just tooling)
- ❌ sfdx-project.json, package.xml (these are setup files, not features)
- ❌ "deployment options", "scripts for linting/testing" (infrastructure, not features)
- ❌ Generic metadata like API versions, package directories

INSTEAD, FOCUS ON:
- ✅ Custom Apex Classes that implement business logic
- ✅ Custom SObjects that model business data
- ✅ LWC Components that provide user interfaces
- ✅ Integrations (Named Credentials, HTTP callouts)
- ✅ Automation (Triggers, Batch Jobs, Queueable)

**SALESFORCE ENTITY CLASSIFICATION:**

1. **Business Logic (Apex Classes)**:
   - Services: AccountSummaryService, NotificationService
   - Jobs: Batch, Queueable, Schedulable classes
   - Utilities: SlackNotifier, EmailHandler
   - Test Classes: *Test.cls (ignore these for project overview)

2. **Data Model (SObjects)**:
   - Standard: Account, Contact, Opportunity
   - Custom: Account_Feedback__c, Custom_Settings__c
   - NOT SObjects: Http, HttpRequest, String, Integer

3. **User Interface (LWC)**:
   - Components that users interact with
   - Forms, displays, interactive elements

4. **Automation**:
   - Triggers: AccountPhoneUpdateTrigger
   - Scheduled Jobs, Batch processes

**RESPONSE STRATEGY BY QUERY TYPE:**

1. **"List all X"** → Return COMPLETE list with descriptions:
   ```
   ## All Apex Classes (18 total)
   - **ClassName1**: What it does
   - **ClassName2**: What it does
   (ALL items, no truncation)
   ```

2. **"What is this project about"** → Business-focused overview:
   ```
   This Salesforce project provides [BUSINESS CAPABILITIES]:
   
   **Core Features:**
   - Feature 1: [Apex class] enables [business value]
   - Feature 2: [LWC component] allows users to [action]
   
   **Data Model:**
   - [Custom objects] store [business data]
   
   **Integrations:**
   - [Integration] connects to [external system]
   ```
   
   DO NOT mention: DX configuration, deployment scripts, package.xml

3. **"How does X work"** → Technical explanation:
   - Focus on the specific component
   - Explain logic flow
   - Mention dependencies

**EXAMPLE - GOOD vs BAD:**

❌ BAD: "The project is about configuring a Salesforce DX project using sfdx-project.json..."
✅ GOOD: "This Salesforce project enables account feedback collection and Slack notifications. Key features include..."

**YOUR INTELLIGENCE:**
- Recognize that EVERY Salesforce project has DX config - it's not a feature
- Understand that test classes are for quality, not user features
- Know that business value comes from custom Apex, custom objects, and UI components
- Filter noise and focus on what makes THIS project unique

**CRITICAL RULES:**
1. ONLY use data provided below
2. For project overviews: Focus on BUSINESS FEATURES, ignore infrastructure
3. For lists: Return EVERY item without truncation
4. For "objects": ONLY list SObjects (not Apex utility classes)
5. If no business features found, say "This appears to be a basic Salesforce DX template"

REMEMBER: Your value is in understanding Salesforce architecture and providing MEANINGFUL insights, not regurgitating configuration details."""),
        ("user", """Question: {query}

Data:
{context}

Analyze the data with your Salesforce expertise. Filter out configuration noise and focus on actual business features and capabilities.""")
    ])
    
    chain = prompt | llm
    result = chain.invoke({
        "query": query,
        "context": all_context
    })
    
    print(f"✅ Response Generated: {len(result.content)} characters")
    print("="*80 + "\n")
    
    return {"final_answer": result.content}


