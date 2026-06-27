import os
import sys

# Ensure the project root is importable so `backend.*` resolves even when this
# file is run directly from inside the backend/ directory (e.g. `python main.py`).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any

from backend.navigator import query_vectorless_rag
from backend.ingest import run_ingestion

app = FastAPI(title="Vectorless RAG Backend API", version="1.0.0")

# Enable CORS for the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify Next.js origin e.g. http://localhost:3000
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global in-memory status tracking
ingestion_status = {
    "status": "idle",  # idle, running, completed, failed
    "message": "No ingestion has been run yet."
}

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    path_taken: List[Dict[str, Any]]
    citations: List[Dict[str, Any]]

class IngestionResponse(BaseModel):
    status: str
    message: str

def bg_ingest_task(limit: int):
    global ingestion_status
    ingestion_status["status"] = "running"
    ingestion_status["message"] = "Fetching Kubernetes concepts docs and merging Markdown files..."
    try:
        run_ingestion(file_limit=limit)
        ingestion_status["status"] = "completed"
        ingestion_status["message"] = "Ingestion pipeline finished successfully. Index files uploaded to S3."
    except Exception as e:
        ingestion_status["status"] = "failed"
        ingestion_status["message"] = f"Ingestion failed with error: {str(e)}"
        print(f"Error in background ingestion: {e}")

@app.get("/api/health")
def health_check():
    return {"status": "ok", "backend": "FastAPI"}

@app.post("/api/query", response_model=QueryResponse)
def handle_query(request: QueryRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    try:
        result = query_vectorless_rag(request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@app.post("/api/ingest", response_model=IngestionResponse)
def trigger_ingest(background_tasks: BackgroundTasks, limit: int = 200):
    global ingestion_status
    if ingestion_status["status"] == "running":
        return {
            "status": "running",
            "message": "An ingestion task is already running in the background."
        }
    
    background_tasks.add_task(bg_ingest_task, limit)
    return {
        "status": "triggered",
        "message": "Ingestion task triggered in the background."
    }

@app.get("/api/status")
def get_status():
    global ingestion_status
    return ingestion_status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
