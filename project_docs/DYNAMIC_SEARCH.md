# Dynamic Search Method Selection - Implementation Guide

## 🎯 What Was Implemented

The system now **automatically selects** the best GraphRAG search method (LOCAL, GLOBAL, or COMMUNITY) based on:
1. **User intent** (from Intent Agent)
2. **Query keywords** (detected patterns)

---

## 🧠 How It Works

### **Decision Logic**

```python
def select_search_method(state: GlobalState):
    intent = state.get("intent", "general")
    query = state.get("user_query", "").lower()
    
    # 1. Check intent
    if intent in ["general", "impact_analysis"]:
        return "global"  # Broad questions need global view
    
    # 2. Check for global keywords
    if "architecture" in query or "overview" in query:
        return "global"
    
    # 3. Check for community keywords
    if "module" in query or "system" in query:
        return "community"
    
    # 4. Default to local
    return "local"  # Most specific questions
```

---

## 📋 Selection Rules

### **GLOBAL Search Selected When:**

**Intent-based:**
- Intent = "general"
- Intent = "impact_analysis"

**Keyword-based:**
- "architecture"
- "overview"
- "structure"
- "organization"
- "components"
- "modules"
- "system design"
- "high level"
- "what are all"
- "what technologies"
- "how is organized"

**Example Queries:**
```
✅ "What is the overall architecture?"
✅ "Give me an overview of the system"
✅ "What are all the components?"
✅ "How is the codebase organized?"
✅ "What technologies are used?"
```

---

### **COMMUNITY Search Selected When:**

**Keyword-based:**
- "module"
- "package"
- "layer"
- "subsystem"
- "authentication system"
- "payment system"
- "api layer"
- "database layer"
- "frontend module"
- "backend module"

**Example Queries:**
```
✅ "How does the authentication module work?"
✅ "Explain the payment system"
✅ "What's in the API layer?"
✅ "How is the database layer organized?"
```

---

### **LOCAL Search Selected When:**

**Default for:**
- Intent = "explain"
- Intent = "debug"
- Intent = "refactor"
- Specific function/class questions
- Any query not matching above patterns

**Example Queries:**
```
✅ "How does the login function work?"
✅ "What does authenticate() do?"
✅ "Where is the JWT token generated?"
✅ "Debug the password validation"
✅ "Refactor the user service"
```

---

## 🎬 Real Examples

### **Example 1: Architecture Question**

**User asks:** "What is the overall architecture?"

```python
# Step 1: Intent Agent
intent = "general"  # Classified by GPT-4

# Step 2: Search Method Selection
select_search_method(state)
→ Checks intent: "general" → GLOBAL
→ Returns: "global"

# Step 3: GraphRAG Query
cmd = ["graphrag", "query", "--method", "global", ...]

# Step 4: Result
Response includes:
"[Using GLOBAL search method]
 
 The system follows a 3-tier architecture:
 - Frontend: React
 - Backend: FastAPI
 - Database: PostgreSQL
 ..."
```

---

### **Example 2: Module Question**

**User asks:** "How does the authentication module work?"

```python
# Step 1: Intent Agent
intent = "explain"

# Step 2: Search Method Selection
select_search_method(state)
→ Checks keywords: "authentication module" → COMMUNITY
→ Returns: "community"

# Step 3: GraphRAG Query
cmd = ["graphrag", "query", "--method", "community", ...]

# Step 4: Result
Response includes:
"[Using COMMUNITY search method]
 
 The authentication module consists of:
 - AuthController
 - UserService
 - PasswordHasher
 - JWTGenerator
 ..."
```

---

### **Example 3: Specific Function Question**

**User asks:** "How does the login function work?"

```python
# Step 1: Intent Agent
intent = "explain"

# Step 2: Search Method Selection
select_search_method(state)
→ No global keywords
→ No community keywords
→ Returns: "local" (default)

# Step 3: GraphRAG Query
cmd = ["graphrag", "query", "--method", "local", ...]

# Step 4: Result
Response includes:
"[Using LOCAL search method]
 
 The login function is in AuthController.login():
 
 ```python
 @app.post('/auth/login')
 def login(credentials):
     ...
 ```
 ..."
```

---

## 🔍 How to See Which Method Was Used

The system now **tells you** which method it used:

```markdown
[Using LOCAL search method]

The login function works by...
```

```markdown
[Using GLOBAL search method]

The overall architecture consists of...
```

```markdown
[Using COMMUNITY search method]

The authentication module includes...
```

---

## 🎯 Benefits

### **Before (Static):**
```
All queries → LOCAL search
- Architecture questions got too detailed
- Module questions missed context
```

### **After (Dynamic):**
```
Architecture questions → GLOBAL search ✅
Module questions → COMMUNITY search ✅
Specific questions → LOCAL search ✅

Each query gets the BEST search method!
```

---

## 🔧 Customization

### **Add New Keywords:**

```python
# In agentic_copilot/graphs/graphrag_subgraph.py

# Add to global_keywords:
global_keywords = [
    "architecture", "overview",
    "tech stack",  # ← Add new
    "dependencies"  # ← Add new
]

# Add to community_keywords:
community_keywords = [
    "module", "package",
    "service layer",  # ← Add new
    "controller layer"  # ← Add new
]
```

### **Adjust Intent Mapping:**

```python
# Make "debug" use community search
if intent in ["general", "impact_analysis", "debug"]:
    return "global"
```

---

## 📊 Decision Flow Diagram

```
User Query
    ↓
Intent Agent (GPT-4)
    ↓
┌─────────────────────────────────┐
│ select_search_method()          │
│                                 │
│ 1. Check intent                 │
│    → "general"? → GLOBAL        │
│                                 │
│ 2. Check global keywords        │
│    → "architecture"? → GLOBAL   │
│                                 │
│ 3. Check community keywords     │
│    → "module"? → COMMUNITY      │
│                                 │
│ 4. Default                      │
│    → LOCAL                      │
└─────────────────────────────────┘
    ↓
GraphRAG CLI with selected method
    ↓
Better, more relevant results!
```

---

## 🚀 Testing

### **Test Different Query Types:**

```bash
# Restart backend to apply changes
python -m uvicorn simple_rag_app.main:app --host 0.0.0.0 --port 8000
```

**Try these queries:**

1. **"What is the architecture?"** → Should use GLOBAL
2. **"How does the auth module work?"** → Should use COMMUNITY
3. **"How does login work?"** → Should use LOCAL

**Look for the method indicator in responses:**
```
[Using GLOBAL search method]
[Using COMMUNITY search method]
[Using LOCAL search method]
```

---

## 💡 Summary

**What Changed:**
- ✅ Added `select_search_method()` function
- ✅ Keyword detection for GLOBAL/COMMUNITY
- ✅ Intent-based routing
- ✅ Method indicator in responses

**Result:**
- 🎯 **Smarter** - Right search for each question
- ⚡ **Faster** - No wasted broad searches
- 📊 **Better answers** - Appropriate detail level
- 🔍 **Transparent** - Shows which method was used

**The system is now INTELLIGENT about how it searches!** 🚀
