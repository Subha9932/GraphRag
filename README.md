# Agentic Engineering Knowledge Copilot (AEKC)

A multi-agent system powered by LangGraph that intelligently analyzes codebases using GraphRAG and provides formatted, context-aware responses.

## 🎯 Overview

AEKC combines multiple AI agents to provide comprehensive code analysis:
- **Intent Classification**: Understands what you're asking
- **GraphRAG Integration**: Queries indexed code knowledge graphs
- **Multi-Agent Orchestration**: Parallel execution for faster responses
- **GPT-4 Synthesis**: Generates clean, markdown-formatted answers

## 🏗️ Architecture

```
┌─────────────┐
│   User UI   │ (React + Markdown Rendering)
└──────┬──────┘
       │
┌──────▼──────┐
│  FastAPI    │ (Backend Server)
└──────┬──────┘
       │
┌──────▼──────────┐
│ LangGraph       │ (Multi-Agent Orchestrator)
│ Main Graph      │
└──────┬──────────┘
       │
   ┌───┴────┬────────┬─────────┬──────────┐
   ▼        ▼        ▼         ▼          ▼
┌──────┐ ┌────┐ ┌────────┐ ┌──────┐ ┌──────┐
│Intent│ │RAG │ │GraphRAG│ │Tools │ │Risk  │
│Agent │ │    │ │ Agent  │ │Agent │ │Agent │
└──┬───┘ └─┬──┘ └───┬────┘ └──┬───┘ └──┬───┘
   │       │        │         │        │
   └───────┴────────┴─────────┴────────┘
                    │
            ┌───────▼────────┐
            │ GPT-4 Synthesis│
            │ (Final Answer) │
            └────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- OpenAI API Key

### Installation

1. **Clone and Setup**
```bash
cd "c:\Users\202317\Graph Knowledge\GraphRag"
```

2. **Install Python Dependencies**
```bash
pip install -r requirements.txt
```

3. **Install Frontend Dependencies**
```bash
cd simple_rag_app/frontend
npm install
cd ../..
```

4. **Configure Environment**
Create `.env` file:
```env
OPENAI_API_KEY=your-key-here
GRAPHRAG_API_KEY=your-key-here
```

### Running the System

**Automated (Recommended):**
```powershell
.\run_servers.ps1
```

**Manual:**
```bash
# Terminal 1 - Backend
python -m uvicorn simple_rag_app.main:app --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd simple_rag_app/frontend
npm run dev
```

Access at: **http://localhost:5173**

## 📖 Usage

### 1. Ingest a Repository
- Enter GitHub URL: `https://github.com/username/repo`
- Click "Ingest & Index"
- Wait for completion (may take several minutes)

### 2. Query the Codebase
**Example Queries:**
- "How does the authentication system work?"
- "Explain the main architecture"
- "What are the key components?"
- "Debug the login flow"

### 3. View Knowledge Graph
Switch to Graph tab to visualize code relationships.

## 🔧 System Components

### Backend (`simple_rag_app/`)
- **main.py**: FastAPI server with LangGraph integration
- **utils.py**: Repository cloning and file processing

### Agentic System (`agentic_copilot/`)

#### Graphs
- **main_graph.py**: Orchestrates all agents
- **intent_subgraph.py**: Classifies user intent
- **graphrag_subgraph.py**: Queries code knowledge graph
- **rag_subgraph.py**: Document retrieval (mocked)
- **tool_subgraph.py**: Tool execution (mocked)
- **risk_subgraph.py**: Risk analysis (mocked)

#### Agents
- **reasoning_agent.py**: GPT-4 synthesis of all agent outputs

#### Schemas
- **state.py**: Global state management with reducers

#### Reducers
- **reducers.py**: State merging strategies

### Frontend (`simple_rag_app/frontend/`)
- **App.jsx**: Main UI with markdown rendering
- **GraphView.jsx**: Interactive graph visualization

## 🎨 Key Features

### Multi-Agent Parallelism
Agents run simultaneously using LangGraph's parallel execution:
```python
workflow.add_edge("intent_analyzer", "rag_agent")
workflow.add_edge("intent_analyzer", "graphrag_agent")
workflow.add_edge("intent_analyzer", "tool_agent")
workflow.add_edge("intent_analyzer", "risk_agent")
```

### State Management
LangGraph reducers handle concurrent updates:
```python
class GlobalState(TypedDict):
    user_query: Annotated[str, _keep_first]  # Immutable
    rag_context: Annotated[List[str], operator.add]  # Accumulates
    graphrag_context: Annotated[List[str], operator.add]
```

### GPT-4 Synthesis
Clean, formatted responses:
```python
llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
response = llm.synthesize(query, intent, context)
```

### Markdown Rendering
Rich text display in React:
```jsx
<ReactMarkdown remarkPlugins={[remarkGfm]}>
  {response}
</ReactMarkdown>
```

## 📊 Advantages Over Previous Implementation

| Feature | Old | New |
|---------|-----|-----|
| **Execution** | Sequential | Parallel (3-5x faster) |
| **Response Quality** | Raw dumps | GPT-4 formatted |
| **Error Handling** | Raw tracebacks | Filtered, graceful |
| **Extensibility** | Hard-coded | Modular agents |
| **State Management** | None | LangGraph reducers |
| **UI** | Plain text | Markdown rendering |

## 🛠️ Development

### Adding a New Agent

1. Create subgraph in `agentic_copilot/graphs/`:
```python
def my_agent(state: GlobalState):
    # Your logic here
    return {"my_context": [result]}

def create_my_subgraph():
    workflow = StateGraph(GlobalState)
    workflow.add_node("my_agent", my_agent)
    workflow.set_entry_point("my_agent")
    workflow.add_edge("my_agent", END)
    return workflow.compile()
```

2. Add to main graph:
```python
from .my_subgraph import create_my_subgraph

workflow.add_node("my_agent", create_my_subgraph())
workflow.add_edge("intent_analyzer", "my_agent")
workflow.add_edge("my_agent", "final_reasoner")
```

3. Update state schema:
```python
class GlobalState(TypedDict):
    # ... existing fields
    my_context: Annotated[List[str], operator.add]
```

## 🐛 Troubleshooting

**Backend won't start:**
- Check `.env` has valid `OPENAI_API_KEY`
- Run: `pip install -r requirements.txt`

**Frontend errors:**
- Run: `npm install` in `simple_rag_app/frontend`
- Clear browser cache

**GraphRAG errors:**
- Ensure repository ingested first
- Check `ragtest/output` exists

**Empty responses:**
- Verify ingestion completed
- Check backend logs for errors

## 📝 API Endpoints

### POST `/api/ingest`
Ingest a GitHub repository
```json
{
  "repo_url": "https://github.com/username/repo"
}
```

### POST `/api/query`
Query the codebase
```json
{
  "query": "How does authentication work?"
}
```

### GET `/api/graph`
Get knowledge graph visualization data

### POST `/api/reset`
Clear all ingested data

## 🔐 Security Notes

- API keys stored in `.env` (gitignored)
- CORS enabled for development (restrict in production)
- No authentication (add for production use)

## 📚 Dependencies

### Python
- fastapi
- uvicorn
- langchain-openai
- langgraph
- graphrag
- pandas
- python-dotenv

### Node.js
- react
- vite
- lucide-react
- react-markdown
- remark-gfm
- react-force-graph-2d

## 🎯 Future Enhancements

- [ ] Streaming responses
- [ ] Conversation memory
- [ ] More specialized agents (security, performance)
- [ ] Cloud deployment
- [ ] Authentication & multi-user support
- [ ] Real-time collaboration

## 📄 License

[Your License Here]

## 🤝 Contributing

Contributions welcome! Please follow the existing code structure and add tests for new features.

## 📞 Support

For issues and questions, please check the troubleshooting section or create an issue in the repository.

---

**Built with ❤️ using LangGraph, FastAPI, and React**
