from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import os
import shutil
import sys
from pathlib import Path
from .utils import clone_repo, process_files

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev simplicity; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (Optional now, but good to keep if we build to static later)
# app.mount("/", StaticFiles(directory="simple_rag_app/static", html=True), name="static")

BASE_DIR = Path(os.getcwd())
RAG_TEST_DIR = BASE_DIR / "ragtest"
INPUT_DIR = RAG_TEST_DIR / "input"
TEMP_REPO_DIR = BASE_DIR / "temp_repo"

class IngestRequest(BaseModel):
    repo_url: str

class QueryRequest(BaseModel):
    query: str

@app.post("/api/ingest")
async def ingest_repo(request: IngestRequest):
    repo_url = request.repo_url
    try:
        # 1. Clone Repo
        print(f"Cloning {repo_url}...")
        repo_content_dir = clone_repo(repo_url, str(TEMP_REPO_DIR))
        
        # 2. Process Files
        print(f"Processing files from {repo_content_dir}...")
        count = process_files(str(repo_content_dir), str(INPUT_DIR))
        
        # 3. Run GraphRAG Indexing
        # Note: This is a blocking operation and can take time.
        # For a production app, use background tasks. Here we wait to report success.
        print("Running Indexing...")
        result = subprocess.run(
            [sys.executable, "-m", "graphrag", "index", "--root", "ragtest"],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            raise HTTPException(status_code=500, detail=f"Indexing failed. Return Code: {result.returncode}. Output: {result.stdout} \n Errors: {result.stderr}")
            
        return {"status": "success", "message": f"Successfully ingested {count} files and indexed the graph."}

    except FileNotFoundError as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"System command not found: {str(e)}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        error_msg = str(e)
        if "404" in error_msg or "Not Found" in error_msg:
             raise HTTPException(
                 status_code=400, 
                 detail="Repository not found or private. Please check the URL. If private, set GITHUB_TOKEN in your .env file."
             )
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {error_msg}")

@app.post("/api/reset")
async def reset_data():
    try:
        # Clear Input Directory
        if INPUT_DIR.exists():
            for file in INPUT_DIR.glob("*"):
                if file.is_file():
                    file.unlink()
        
        # Clear Output Directory
        output_dir = BASE_DIR / "ragtest" / "output"
        if output_dir.exists():
            shutil.rmtree(output_dir)
            
        return {"status": "success", "message": "All data cleared successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/query")
async def query_graph(request: QueryRequest):
    try:
        # Run Global Query
        print(f"Querying: {request.query}")
        result = subprocess.run(
            [sys.executable, "-m", "graphrag", "query", "--root", "ragtest", "--method", "global", "--query", request.query],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True
        ) 
        
        if result.returncode != 0:
             # Try local search if global fails or just return error
            raise HTTPException(status_code=500, detail=f"Query failed: {result.stderr}")

        # Extract the relevant part of the output
        output = result.stdout
        clean_output = "\n".join([line for line in output.splitlines() if not line.startswith("2025-")])
        
        return {"response": clean_output}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/graph")
async def get_graph():
    try:
        import pandas as pd
        
        output_dir = RAG_TEST_DIR / "output"
        # Find the timestamped folder or just use the latest artifacts if they are in root of output 
        # (GraphRAG default behavior might vary, but usually they are right in output/YYYYMMDD-HHMMSS/artifacts)
        # However, our previous run showed they were directly in output/ or a subdir. 
        # Let's check where the previous run put them.
        
        # Based on previous `list_dir` calls, artifacts seem to be directly in `ragtest/output` 
        # OR `ragtest/output/lancedb` etc.
        # Wait, the `list_dir` showed text_units.parquet etc in `ragtest/output`.
        
        entities_path = output_dir / "entities.parquet"
        relationships_path = output_dir / "relationships.parquet"
        
        if not entities_path.exists() or not relationships_path.exists():
             # Fallback check for subdirectory if needed, but for now assume root based on previous context
             # If strictly needed, we could scan for subdirs.
             raise HTTPException(status_code=404, detail="Graph artifacts not found. Has ingestion successfully completed?")

        # Read Entities
        df_entities = pd.read_parquet(entities_path)
        # Columns usually: id, title, type, description, ...
        # Take top nodes by degree or just first N to avoid overwhelming UI
        # For simplicity, let's take all or top 500.
        nodes = []
        for _, row in df_entities.iterrows():
            # CRITICAL FIX: Links use Entity Names (titles) as source/target, not UUIDs.
            # So we must use the title as the ID for the frontend graph to connect them.
            nodes.append({
                "id": str(row.get('title', 'Unknown')),  # Use Title as ID
                "name": row.get('title', 'Unknown'),
                "type": row.get('type', 'Unknown'),
                "description": row.get('description', '')
            })
            
        # Read Relationships
        df_rels = pd.read_parquet(relationships_path)
        # Columns: source, target, weight, description...
        links = []
        for _, row in df_rels.iterrows():
            # Get description for label, truncate if too long
            desc = str(row.get('description', ''))
            # Simple heuristic: first few words or truncated string
            label = (desc[:30] + '...') if len(desc) > 30 else desc
            
            links.append({
                "source": str(row.get('source', '')),
                "target": str(row.get('target', '')),
                "weight": float(row.get('weight', 1.0)),
                "label": label
            })
            
        return {"nodes": nodes, "links": links}

    except ImportError:
        raise HTTPException(status_code=500, detail="Pandas/Pyarrow not installed on backend.")
    except Exception as e:
        print(f"Graph Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
