# Run All Servers

$exepath = ".\.venv\Scripts\python.exe"

# 1. Start FastAPI Backend (Simple RAG App + Agentic Copilot)
Write-Host "Starting Backend (FastAPI)..."
Start-Process -FilePath $exepath -ArgumentList "-m", "uvicorn", "simple_rag_app.main:app", "--host", "0.0.0.0", "--port", "8000"

# 2. Start React Frontend
Write-Host "Starting React Frontend..."
# Check if node_modules exists, if not install? (Optional, user might have done it)
# We assume user can run 'npm install' if needed, or we can add a check.
# For now, just launch dev server.
Set-Location "simple_rag_app/frontend"
Start-Process -FilePath "npm" -ArgumentList "run", "dev"
Set-Location "..\.."

Write-Host "Servers are starting. Backend: http://localhost:8000, Frontend: http://localhost:5173 (usually)"
