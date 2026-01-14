# Agent Thinking Logs - Debug Guide

## 🎯 What Was Added

The system now logs **detailed thinking process** for each agent, making it easy to understand what's happening behind the scenes!

---

## 📊 Example Log Output

When you ask: **"How does the authentication system work?"**

### **Complete Log Flow:**

```
================================================================================
🧠 INTENT AGENT - Analyzing Query
================================================================================
📝 User Query: 'How does the authentication system work?'
✅ Intent Classified: 'explain'
================================================================================

================================================================================
🔍 SEARCH METHOD SELECTOR - Choosing Best Method
================================================================================
📝 Query: 'How does the authentication system work?'
🎯 Intent: 'explain'
🤖 Asking GPT-4 Mini to select optimal search method...
✅ Selected Method: 'COMMUNITY'
💡 Reasoning: COMMUNITY search is best for this type of query
================================================================================

================================================================================
📊 GRAPHRAG AGENT - Searching Code Knowledge Graph
================================================================================
🔎 Executing GraphRAG COMMUNITY search...
✅ GraphRAG Results: [Using COMMUNITY search method]

SUCCESS: Community Search Response:

The authentication system consists of several interconnected components...
================================================================================

================================================================================
🎨 FINAL REASONING AGENT - Synthesizing Response
================================================================================
📝 Query: 'How does the authentication system work?'
🎯 Intent: 'explain'
📚 Context Sources:
   - RAG Data: 2 items
   - Code Data: 1 items
   - Tool Results: 2 items
   - Risk Signals: 1 items
🤖 Sending to GPT-4 for synthesis...
📊 Total context size: 1247 characters
✅ Response Generated: 856 characters
================================================================================
```

---

## 🔍 What Each Section Shows

### **1. Intent Agent** 🧠
```
🧠 INTENT AGENT - Analyzing Query
📝 User Query: 'How does login work?'
✅ Intent Classified: 'explain'
```

**Shows:**
- What the user asked
- How GPT-4 classified the intent

---

### **2. Search Method Selector** 🔍
```
🔍 SEARCH METHOD SELECTOR - Choosing Best Method
📝 Query: 'How does login work?'
🎯 Intent: 'explain'
🤖 Asking GPT-4 Mini to select optimal search method...
✅ Selected Method: 'LOCAL'
💡 Reasoning: LOCAL search is best for this type of query
```

**Shows:**
- Query and intent being analyzed
- AI decision process
- Which search method was chosen
- Why that method is appropriate

---

### **3. GraphRAG Agent** 📊
```
📊 GRAPHRAG AGENT - Searching Code Knowledge Graph
🔎 Executing GraphRAG LOCAL search...
✅ GraphRAG Results: [Using LOCAL search method]

The login function is implemented in AuthController.login()...
```

**Shows:**
- Which search method is being executed
- Preview of results (first 200 characters)

---

### **4. Final Reasoning Agent** 🎨
```
🎨 FINAL REASONING AGENT - Synthesizing Response
📝 Query: 'How does login work?'
🎯 Intent: 'explain'
📚 Context Sources:
   - RAG Data: 2 items
   - Code Data: 1 items
   - Tool Results: 2 items
   - Risk Signals: 1 items
🤖 Sending to GPT-4 for synthesis...
📊 Total context size: 1247 characters
✅ Response Generated: 856 characters
```

**Shows:**
- What data sources are available
- How much context is being sent to GPT-4
- Size of generated response

---

## 🎬 Different Query Examples

### **Example 1: Architecture Question**

**Query:** "What is the overall architecture?"

```
🧠 INTENT AGENT
📝 User Query: 'What is the overall architecture?'
✅ Intent Classified: 'general'

🔍 SEARCH METHOD SELECTOR
🎯 Intent: 'general'
✅ Selected Method: 'GLOBAL'  ← Uses GLOBAL for architecture
💡 Reasoning: GLOBAL search is best for this type of query

📊 GRAPHRAG AGENT
🔎 Executing GraphRAG GLOBAL search...  ← Broad search
✅ GraphRAG Results: The system follows a 3-tier architecture...

🎨 FINAL REASONING AGENT
📚 Context Sources:
   - Code Data: 1 items (GLOBAL results)
✅ Response Generated: 1024 characters
```

---

### **Example 2: Specific Function**

**Query:** "How does the login function work?"

```
🧠 INTENT AGENT
📝 User Query: 'How does the login function work?'
✅ Intent Classified: 'explain'

🔍 SEARCH METHOD SELECTOR
🎯 Intent: 'explain'
✅ Selected Method: 'LOCAL'  ← Uses LOCAL for specific function
💡 Reasoning: LOCAL search is best for this type of query

📊 GRAPHRAG AGENT
🔎 Executing GraphRAG LOCAL search...  ← Focused search
✅ GraphRAG Results: The login function is in AuthController.login()...

🎨 FINAL REASONING AGENT
📚 Context Sources:
   - Code Data: 1 items (LOCAL results)
✅ Response Generated: 645 characters
```

---

### **Example 3: Module Question**

**Query:** "Explain the payment system"

```
🧠 INTENT AGENT
📝 User Query: 'Explain the payment system'
✅ Intent Classified: 'explain'

🔍 SEARCH METHOD SELECTOR
🎯 Intent: 'explain'
✅ Selected Method: 'COMMUNITY'  ← Uses COMMUNITY for module
💡 Reasoning: COMMUNITY search is best for this type of query

📊 GRAPHRAG AGENT
🔎 Executing GraphRAG COMMUNITY search...  ← Module-level search
✅ GraphRAG Results: The payment system includes PaymentController...

🎨 FINAL REASONING AGENT
📚 Context Sources:
   - Code Data: 1 items (COMMUNITY results)
✅ Response Generated: 892 characters
```

---

## 🔧 Where to See Logs

### **Backend Terminal:**
The logs appear in the terminal where you're running:
```powershell
python -m uvicorn simple_rag_app.main:app --host 0.0.0.0 --port 8000
```

### **Example Output:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000

================================================================================
🧠 INTENT AGENT - Analyzing Query
================================================================================
📝 User Query: 'How does login work?'
✅ Intent Classified: 'explain'
================================================================================

... (more logs)
```

---

## 🎯 Benefits

### **1. Transparency**
- ✅ See exactly what each agent is doing
- ✅ Understand AI decision-making
- ✅ Track data flow through system

### **2. Debugging**
- ✅ Identify where issues occur
- ✅ See which search method was chosen
- ✅ Verify context is being gathered

### **3. Learning**
- ✅ Understand how the system works
- ✅ See AI reasoning process
- ✅ Learn when each search method is used

### **4. Optimization**
- ✅ See context sizes
- ✅ Track response lengths
- ✅ Identify bottlenecks

---

## 🧪 Testing

### **Restart Backend:**
```powershell
# Stop current server (CTRL+C)
python -m uvicorn simple_rag_app.main:app --host 0.0.0.0 --port 8000
```

### **Watch the Logs:**
1. Ask a question in the UI
2. Switch to backend terminal
3. Watch the agent thinking process unfold!

### **Try Different Queries:**
```
"What is the architecture?"          → Watch for GLOBAL selection
"How does auth module work?"         → Watch for COMMUNITY selection
"How does login function work?"      → Watch for LOCAL selection
```

---

## 📊 Log Emoji Guide

| Emoji | Meaning |
|-------|---------|
| 🧠 | Intent Agent (classification) |
| 🔍 | Search Method Selector (AI decision) |
| 📊 | GraphRAG Agent (code search) |
| 🎨 | Final Reasoning Agent (synthesis) |
| 📝 | User input/query |
| 🎯 | Intent/goal |
| 🤖 | AI processing |
| ✅ | Success/completion |
| ⚠️ | Warning |
| ❌ | Error |
| 💡 | Reasoning/explanation |
| 📚 | Context/data |
| 🔎 | Search operation |

---

## 💡 Advanced: Log Analysis

### **Pattern Recognition:**

**Fast queries:**
```
Intent Agent: 100ms
Search Selector: 200ms
GraphRAG: 2000ms
Final Reasoning: 1500ms
Total: ~3.8s
```

**Slow queries:**
```
Intent Agent: 100ms
Search Selector: 200ms
GraphRAG: 5000ms  ← GLOBAL search takes longer
Final Reasoning: 2000ms
Total: ~7.3s
```

### **Context Size Analysis:**
```
Small context (LOCAL): ~500 chars → Fast synthesis
Medium context (COMMUNITY): ~1500 chars → Medium synthesis
Large context (GLOBAL): ~3000 chars → Slower synthesis
```

---

## 🎉 Summary

**What You Get:**
- 🔍 **Full visibility** into agent thinking
- 📊 **Real-time tracking** of decisions
- 🎯 **Clear understanding** of search method selection
- 📚 **Context awareness** of data sources
- ✅ **Easy debugging** when things go wrong

**The system is now fully transparent!** You can see exactly how it thinks and makes decisions! 🚀
