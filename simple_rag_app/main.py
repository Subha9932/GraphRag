from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import os
import shutil
import sys
from pathlib import Path
from .utils import clone_repo, process_files

# Add project root to path to import agentic_copilot
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv
env_path = Path(__file__).resolve().parent.parent / '.env'
print(f"Loading .env from: {env_path}, Exists: {env_path.exists()}")
load_dotenv(dotenv_path=env_path, override=True)
key_status = "FOUND" if os.environ.get("OPENAI_API_KEY") else "MISSING"
print(f"DEBUG: OPENAI_API_KEY status: {key_status}")


from agentic_copilot.graphs.main_graph import create_main_graph

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev simplicity; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(os.getcwd())
RAG_TEST_DIR = BASE_DIR / "ragtest"
INPUT_DIR = RAG_TEST_DIR / "input"
TEMP_REPO_DIR = BASE_DIR / "temp_repo"


@app.post("/api/ingest/upload")
async def ingest_files(files: list[UploadFile] = File(...)):
    try:
        # 1. Clear Input Directory (Start Fresh)
        if INPUT_DIR.exists():
            print(f"🧹 Clearing existing data in {INPUT_DIR}...")
            for item in INPUT_DIR.iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
        else:
            INPUT_DIR.mkdir(parents=True, exist_ok=True)
            
        # Define filters (Hardcoded for Salesforce & General Code)
        ALLOWED_EXTENSIONS = {
            # Salesforce
            '.cls', '.trigger', '.cmp', '.page', '.component', '.xml', 
            # Web / JS
            '.js', '.jsx', '.ts', '.tsx', '.html', '.css', '.json', '.yaml', '.yml',
            # Backend / General
            '.py', '.java', '.cpp', '.c', '.h', '.cs', '.go', '.rs', 
            '.php', '.rb', '.swift', '.kt', '.md', '.txt'
        }
        
        IGNORED_PATTERNS = {
            '__pycache__', '.git', 'node_modules', 'dist', 'build', 
            'bin', 'obj', '.idea', '.vscode', 'venv', '.venv', 'coverage',
            '.DS_Store'
        }

        print(f"🎯 using Hardcoded Filters | Allowed: {len(ALLOWED_EXTENSIONS)} types, Ignored: {len(IGNORED_PATTERNS)} patterns")

        count = 0
        skipped_count = 0
        
        for file in files:
            filename = file.filename
            file_path = Path(filename)
            
            # 2. Check Ignored Patterns (Directory or Filename substring)
            is_ignored = False
            for pattern in IGNORED_PATTERNS:
                if pattern in file_path.parts or filename.startswith(pattern):
                    is_ignored = True
                    break
            
            if is_ignored:
                print(f"Skipping ignored pattern: {filename}")
                skipped_count += 1
                continue
                
            # 3. Check Extension Whitelist
            if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
                print(f"Skipping unsupported extension: {filename}")
                skipped_count += 1
                continue

            # Save file
            target_path = INPUT_DIR / file_path.name
            
            content = await file.read()
            # Basic textual check
            try:
                text_content = content.decode("utf-8")
                with open(target_path, "w", encoding="utf-8") as f:
                    f.write(text_content)
                count += 1
            except UnicodeDecodeError:
                print(f"Skipping binary file: {filename}")
                skipped_count += 1
                continue

        if count == 0:
             raise HTTPException(status_code=400, detail=f"No valid code files found! Checked {len(files)} files.")

        print(f"Uploaded {count} valid files to {INPUT_DIR} (Skipped {skipped_count})")
        
        # 3. Run GraphRAG Indexing
        print("Running Indexing...")
        result = subprocess.run(
            [sys.executable, "-m", "graphrag", "index", "--root", "ragtest"],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            # Relaxed Check: GraphRAG sometimes emits RuntimeWarnings at exit but finishes work
            if "Pipeline complete" in result.stdout:
                print(f"⚠️ Indexing generated warnings but completed successfully.\nWarnings: {result.stderr[:200]}...")
            else:
                print(f"❌ Indexing Failed with return code {result.returncode}")
                print(f"STDOUT:\n{result.stdout}")
                print(f"STDERR:\n{result.stderr}")
                raise HTTPException(status_code=500, detail=f"Indexing failed. Check server logs for details. Stderr: {result.stderr[:500]}...")
            
        success_msg = f"Successfully uploaded {count} files (Skipped {skipped_count} noise files)."
        return {"status": "success", "message": success_msg}


    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

from typing import Optional

class IngestRequest(BaseModel):
    repo_url: Optional[str] = None
    local_path: Optional[str] = None

class QueryRequest(BaseModel):
    query: str

@app.post("/api/ingest")
async def ingest_repo(request: IngestRequest):
    repo_url = request.repo_url
    local_path = request.local_path
    
    # Validation: Ensure at least one is provided
    if not repo_url and not local_path:
        raise HTTPException(status_code=400, detail="Either 'repo_url' or 'local_path' must be provided.")
        
    try:
        source_dir = ""
        
        # 1. Determine Source
        if local_path:
            # Handle Local Path
            print(f"Ingesting from local path: {local_path}...")
            p = Path(local_path)
            if not p.exists() or not p.is_dir():
                raise HTTPException(status_code=400, detail=f"Local path does not exist or is not a directory: {local_path}")
            source_dir = str(p)
        else:
            # Handle GitHub URL
            print(f"Cloning {repo_url}...")
            source_dir = str(clone_repo(repo_url, str(TEMP_REPO_DIR)))
        
        # 2. Process Files
        print(f"Processing files from {source_dir}...")
        count = process_files(source_dir, str(INPUT_DIR))
        
        # 3. Run GraphRAG Indexing
        # Note: This is a blocking operation and can take time.
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

    except HTTPException as he:
        raise he
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
        print(f"Agentic Query: {request.query}")
        
        # Initialize the LangGraph Application
        # We create it per request or cache it globally. Creating per request is safer for thread isolation in this prototype.
        graph_app = create_main_graph()
        
        # Initial State
        initial_state = {
            "user_query": request.query,
            "rag_context": [],
            "graphrag_context": [],
            "tool_results": [],
            "risk_signals": [],
            "merged_insights": []
        }
        
        # Execute Graph
        # We use .invoke() for a blocking call suitable for a standard HTTP request
        result = graph_app.invoke(initial_state)
        
        final_answer = result.get("final_answer", "No answer generated by agents.")
        
        # We can also return the detailed trace if the frontend supports it, 
        # but for "same React UI" compatibility, we primarily return 'response'.
        # We append the details to the response or a separate field.
        
        return {
            "response": final_answer,
            "details": result # Extra data for potential future UI upgrades
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
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
             # Return empty graph instead of error to allow UI to load gracefully
             return {"nodes": [], "links": []}

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
