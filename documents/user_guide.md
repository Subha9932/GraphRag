# GitHub GraphRAG App Walkthrough

I have built a complete full-stack application for you to ingest GitHub repositories and interact with their knowledge graphs.

## App Structure
The project is located in `c:\Users\202317\.gemini\antigravity\scratch\GrapgRagMain\simple_rag_app`.

### Backend (`simple_rag_app/main.py`)
-   **Framework**: FastAPI.
-   **Features**:
    -   `POST /api/ingest`: Clones a repo and runs GraphRAG indexing.
    -   `POST /api/query`: Runs GraphRAG global search.
    -   `GET /api/graph`: Returns nodes and links from the generated knowledge graph (Parquet files).
-   **Dependencies**: `fastapi`, `uvicorn`, `pandas`, `pyarrow`.

### Frontend (`simple_rag_app/frontend/`)
-   **Framework**: React + Vite.
-   **Features**:
    -   **Glassmorphism UI**: Premium dark aesthetics.
    -   **Tabs**: Switch between "Chat" and "Graph" modes.
    -   **Graph Visualization**: Interactive 2D force-directed graph of the codebase knowledge.

## How to Run

### 1. Start the Backend
Open a terminal in the root workspace and run:
```powershell
uvicorn simple_rag_app.main:app --reload
```
*The backend runs on `http://localhost:8000`.*

### 2. Start the Frontend
Open a **new** terminal, navigate to the frontend directory, and start Vite:
```powershell
cd simple_rag_app/frontend
npm run dev
```
*The frontend typically runs on `http://localhost:5173`.*

## Usage Guide
1.  **Ingest**: Paste a GitHub URL (e.g., a small public repo) and click "Ingest & Index". Wait for the process to complete (check backend terminal for logs).
2.  **Chat**: Ask questions like "What is the main architecture?" or "How does the authentication work?".
3.  **Graph**: Switch to the **Graph** tab to visualize the entities and relationships extracted from the code.
