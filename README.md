# GraphRAG - Codebase Analysis Tool 🚀

A powerful GraphRAG-based application optimized for analyzing and understanding codebases through knowledge graph visualization.

## 🎯 Features

- **Codebase Ingestion**: Automatically clone and process GitHub repositories
- **AI-Powered Analysis**: Extract entities (Classes, Functions, Files, Variables) and relationships
- **Interactive Graph Visualization**: Explore code dependencies and structure visually
- **Intelligent Querying**: Ask questions about your codebase using natural language
- **Private Repository Support**: Authenticate with GitHub tokens

## 🏗️ Architecture

```
GitHub Repository
    ↓
Download & Process (utils.py)
    ↓
GraphRAG Indexing (AI Extraction)
    ↓
Graph Storage (Parquet Files)
    ↓
FastAPI Backend
    ↓
React Frontend (Graph Visualization)
```

## 📋 Prerequisites

- Python 3.10-3.12
- Node.js 16+
- OpenAI API Key

## 🚀 Quick Start

### 1. Install Dependencies

**Backend:**
```bash
pip install -r requirements.txt
```

**Frontend:**
```bash
cd simple_rag_app/frontend
npm install
```

### 2. Configure Environment

Create `ragtest/.env`:
```env
GRAPHRAG_API_KEY=your_openai_api_key_here
```

Optional - For private repositories:
```env
GITHUB_TOKEN=your_github_token_here
```

### 3. Start the Application

**Terminal 1 - Backend:**
```bash
uvicorn simple_rag_app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd simple_rag_app/frontend
npm run dev
```

### 4. Access the Application

- Frontend: `http://localhost:5173`
- Backend API: `http://127.0.0.1:8000`
- API Docs: `http://127.0.0.1:8000/docs`

## 📖 Usage

1. **Ingest a Repository**: Enter a GitHub URL (e.g., `https://github.com/user/repo`)
2. **Wait for Processing**: The system will download, chunk, and analyze the code
3. **Explore the Graph**: View entities and relationships visually
4. **Ask Questions**: Use natural language to query your codebase

## 🔧 Configuration

### Entity Types
Configured in [`ragtest/settings.yaml`](ragtest/settings.yaml#L82):
```yaml
entity_types: [class, function, module, variable, file, api_endpoint]
```

### Chunking Strategy
```yaml
chunks:
  size: 1200        # Characters per chunk
  overlap: 100      # Overlap between chunks
```

### Concurrent Processing
```yaml
concurrent_requests: 25  # Process up to 25 chunks in parallel
```

## 📚 Documentation

Detailed documentation available in the [`docs/`](docs/) folder:

- **[Simple Flow Guide](docs/simple_flow_guide.md)** - Easy visual walkthrough
- **[Technical Walkthrough](docs/walkthrough.md)** - Comprehensive technical details
- **[Implementation Plan](docs/implementation_plan.md)** - Development roadmap

## 🛠️ Key Components

### Backend (`simple_rag_app/`)
- **`main.py`**: FastAPI server with ingestion and query endpoints
- **`utils.py`**: Repository cloning and file processing utilities

### Frontend (`simple_rag_app/frontend/`)
- **`GraphView.jsx`**: Interactive graph visualization using `react-force-graph-2d`

### GraphRAG Configuration (`ragtest/`)
- **`settings.yaml`**: Main configuration file
- **`prompts/`**: Custom prompts for entity extraction and querying
- **`output/`**: Generated graph data (entities.parquet, relationships.parquet)

## 🔍 How It Works

1. **Ingestion**: Code files are downloaded and preprocessed with metadata headers
2. **Chunking**: Files are split into 1200-character chunks with 100-character overlap
3. **Parallel Processing**: Up to 25 chunks processed simultaneously by AI
4. **Entity Extraction**: AI identifies code entities (classes, functions, etc.)
5. **Relationship Mapping**: AI determines connections (imports, calls, defines)
6. **Graph Storage**: Results saved in Parquet format for efficient querying
7. **Visualization**: Frontend renders interactive graph from backend API

## 🎨 Custom Prompts

The system uses custom prompts optimized for code analysis:

- **Extract Graph**: Identifies code entities with safe naming conventions
- **Global Search Map**: Analyzes code structure and patterns
- **Global Search Reduce**: Synthesizes technical reports

## 🐛 Troubleshooting

### Issue: 500 Error on Ingestion
**Solution**: Check `ragtest/logs/indexing-engine.log` for detailed errors

### Issue: Graph shows no connections
**Solution**: Verify `entities.parquet` and `relationships.parquet` exist in `ragtest/output/`

### Issue: Private repository access denied
**Solution**: Set `GITHUB_TOKEN` in your environment or `.env` file

## 📊 Data Storage

- **Entities**: `ragtest/output/entities.parquet` (nodes)
- **Relationships**: `ragtest/output/relationships.parquet` (edges)
- **Format**: Apache Parquet (columnar, compressed)

## 🤝 Contributing

Contributions welcome! Please ensure:
- Code follows existing patterns
- Documentation is updated
- Tests pass (if applicable)

## 📝 License

[Add your license here]

## 🙏 Acknowledgments

- Built with [Microsoft GraphRAG](https://github.com/microsoft/graphrag)
- Visualization powered by [react-force-graph](https://github.com/vasturiano/react-force-graph)

---

**Made with ❤️ for better codebase understanding**
