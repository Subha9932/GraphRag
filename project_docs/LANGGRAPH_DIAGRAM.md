# LangGraph Diagram - Visual Explanation

## 🎯 What is a LangGraph Diagram?

A **LangGraph diagram** is a visual representation of how AI agents are connected and when they execute. Think of it like a **flowchart for AI agents**.

---

## 📊 Our LangGraph Structure

Based on `main_graph.py`, here's the exact diagram:

```
                    ┌─────────┐
                    │  START  │
                    └────┬────┘
                         │
                         ↓
              ┌──────────────────────┐
              │  intent_analyzer     │  ← Classifies user intent
              │  (GPT-4)             │
              └──────────┬───────────┘
                         │
         ┌───────────────┼───────────────┬───────────────┐
         │               │               │               │
         ↓               ↓               ↓               ↓
    ┌────────┐     ┌──────────┐    ┌─────────┐    ┌──────────┐
    │  rag   │     │ graphrag │    │  tool   │    │   risk   │
    │ agent  │     │  agent   │    │ agent   │    │  agent   │
    └────┬───┘     └────┬─────┘    └────┬────┘    └────┬─────┘
         │              │               │              │
         │              │               │              │
         └──────────────┼───────────────┼──────────────┘
                        │               │
                        ↓               ↓
                 ┌──────────────────────────┐
                 │  final_reasoner          │  ← GPT-4 synthesis
                 │  (Combines all results)  │
                 └──────────┬───────────────┘
                            │
                            ↓
                       ┌────────┐
                       │  END   │
                       └────────┘
```

---

## 🔍 Breaking Down Each Part

### **Nodes (Boxes)**
Each box is an **agent** that does a specific job:

```python
# From main_graph.py lines 17-26
workflow.add_node("intent_analyzer", create_intent_subgraph())
workflow.add_node("rag_agent", create_rag_subgraph())
workflow.add_node("graphrag_agent", create_graphrag_subgraph())
workflow.add_node("tool_agent", create_tool_subgraph())
workflow.add_node("risk_agent", create_risk_subgraph())
workflow.add_node("final_reasoner", final_reasoning)
```

| Node Name | What It Does |
|-----------|--------------|
| `intent_analyzer` | Understands what you're asking (explain? debug? refactor?) |
| `rag_agent` | Searches documentation (currently mocked) |
| `graphrag_agent` | Searches your actual code using GraphRAG |
| `tool_agent` | Runs commands on codebase (currently mocked) |
| `risk_agent` | Analyzes risks (currently mocked) |
| `final_reasoner` | Combines everything into nice answer |

### **Edges (Arrows)**
Arrows show **execution order** and **data flow**:

```python
# From main_graph.py lines 30-45

# Sequential edge (one after another)
workflow.add_edge(START, "intent_analyzer")

# Parallel edges (all at same time)
workflow.add_edge("intent_analyzer", "rag_agent")
workflow.add_edge("intent_analyzer", "graphrag_agent")
workflow.add_edge("intent_analyzer", "tool_agent")
workflow.add_edge("intent_analyzer", "risk_agent")

# Convergence edges (all lead to same place)
workflow.add_edge("rag_agent", "final_reasoner")
workflow.add_edge("graphrag_agent", "final_reasoner")
workflow.add_edge("tool_agent", "final_reasoner")
workflow.add_edge("risk_agent", "final_reasoner")

# Final edge
workflow.add_edge("final_reasoner", END)
```

---

## 🎬 Execution Flow (Animated)

Let me show you **when each agent runs**:

### **Time: 0ms - START**
```
┌─────────┐
│  START  │ ← User asks: "How does login work?"
└────┬────┘
     │
```

### **Time: 100ms - Intent Analysis**
```
     ↓
┌──────────────────────┐
│  intent_analyzer     │ ← GPT-4 classifies: "explain"
│  Status: RUNNING     │
└──────────────────────┘
```

### **Time: 1000ms - Parallel Execution Starts**
```
     ↓
┌────────┐  ┌──────────┐  ┌─────────┐  ┌──────────┐
│  rag   │  │ graphrag │  │  tool   │  │   risk   │
│RUNNING │  │ RUNNING  │  │ RUNNING │  │ RUNNING  │
└────────┘  └──────────┘  └─────────┘  └──────────┘

ALL FOUR RUN AT THE SAME TIME! ⚡
```

### **Time: 3000ms - Agents Finish**
```
┌────────┐  ┌──────────┐  ┌─────────┐  ┌──────────┐
│  rag   │  │ graphrag │  │  tool   │  │   risk   │
│  DONE  │  │   DONE   │  │  DONE   │  │   DONE   │
└────┬───┘  └────┬─────┘  └────┬────┘  └────┬─────┘
     │           │             │            │
     └───────────┼─────────────┼────────────┘
                 ↓
```

### **Time: 3500ms - Final Synthesis**
```
          ┌──────────────────────────┐
          │  final_reasoner          │
          │  GPT-4 combines results  │
          │  Status: RUNNING         │
          └──────────────────────────┘
```

### **Time: 5000ms - END**
```
          ┌──────────────────────────┐
          │  final_reasoner          │
          │  Status: DONE            │
          └──────────┬───────────────┘
                     ↓
                ┌────────┐
                │  END   │ ← Beautiful answer ready!
                └────────┘
```

---

## 🎨 Different Diagram Styles

### **Style 1: Hierarchical (Top to Bottom)**
```
                START
                  ↓
            Intent Analyzer
                  ↓
    ┌─────────────┼─────────────┐
    ↓             ↓             ↓
  RAG        GraphRAG        Tool/Risk
    ↓             ↓             ↓
    └─────────────┼─────────────┘
                  ↓
           Final Reasoner
                  ↓
                 END
```

### **Style 2: Left to Right (Pipeline)**
```
START → Intent → [RAG, GraphRAG, Tool, Risk] → Final → END
                      (Parallel)
```

### **Style 3: Detailed with Data Flow**
```
START
  │
  │ state = {user_query: "..."}
  ↓
Intent Analyzer
  │
  │ state.intent = "explain"
  ↓
  ├─→ RAG Agent ────────┐
  │   state.rag_context  │
  │                      │
  ├─→ GraphRAG Agent ────┤
  │   state.graphrag_ctx │
  │                      ├─→ Final Reasoner
  ├─→ Tool Agent ────────┤    state.final_answer
  │   state.tool_results │
  │                      │
  └─→ Risk Agent ────────┘
      state.risk_signals
                         ↓
                        END
```

---

## 🔑 Key Concepts

### **1. Parallel Execution**
```
Instead of:
  Agent 1 (1s) → Agent 2 (1s) → Agent 3 (1s) = 3 seconds total

LangGraph does:
  Agent 1 (1s) ┐
  Agent 2 (1s) ├─ All at same time = 1 second total
  Agent 3 (1s) ┘
```

### **2. State Management**
```
Each agent updates shared state:

Initial:  {user_query: "...", rag_context: []}
After RAG: {user_query: "...", rag_context: ["doc1", "doc2"]}
After All: {user_query: "...", rag_context: [...], graphrag_context: [...], ...}
```

### **3. Conditional Edges (Not Used Here)**
```
We could add conditions:

if intent == "debug":
    → Run debugging agents
elif intent == "explain":
    → Run explanation agents

(But we run all agents regardless for now)
```

---

## 💡 Why This Structure?

### **Benefits:**
1. ✅ **Fast**: Parallel execution (3-5x faster)
2. ✅ **Modular**: Easy to add/remove agents
3. ✅ **Clear**: Visual representation of workflow
4. ✅ **Scalable**: Can handle complex workflows

### **Example: Adding a New Agent**
```python
# Just add 2 lines!
workflow.add_node("security_agent", create_security_subgraph())
workflow.add_edge("intent_analyzer", "security_agent")
workflow.add_edge("security_agent", "final_reasoner")
```

New diagram automatically becomes:
```
                Intent
                  ↓
    ┌─────────────┼─────────────┬──────────┐
    ↓             ↓             ↓          ↓
  RAG        GraphRAG        Tool      Security ← NEW!
    ↓             ↓             ↓          ↓
    └─────────────┼─────────────┴──────────┘
                  ↓
           Final Reasoner
```

---

## 🎯 Summary

**LangGraph Diagram = Visual Workflow**

It shows:
- 📦 **What agents exist** (nodes/boxes)
- 🔗 **How they're connected** (edges/arrows)
- ⏱️ **When they run** (sequential vs parallel)
- 📊 **How data flows** (state updates)

**Think of it like a factory assembly line**, but for AI agents! 🏭
