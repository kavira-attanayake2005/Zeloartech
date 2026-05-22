from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from typing import List
import logging

from schemas import HRRequest, HRResponse, AuditLogResponse, MemoryItemCreate, MemoryItemResponse
import orchestrator
import database
from memory import process_and_store_memory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="HR Automation Engine API")

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Graceful error handling to prevent exposing raw stack traces."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again later."}
    )

@app.get("/health")
def health_check():
    """Health monitoring endpoint."""
    return {"status": "healthy"}

@app.post("/api/request", response_model=HRResponse)
def handle_request(req: HRRequest):
    """
    Main endpoint for handling natural language requests.
    Routes to the orchestrator to manage the agent flow.
    """
    try:
        final_state = orchestrator.process_request(req.user_id, req.query)
        return HRResponse(
            user_id=req.user_id,
            response=final_state['response'],
            intent=final_state['intent'],
            confidence=final_state['confidence']
        )
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process HR request."
        )

@app.get("/api/audit", response_model=List[AuditLogResponse])
def get_audit_logs():
    """Retrieves all append-only audit logs."""
    try:
        logs = database.get_audit_logs()
        return logs
    except Exception as e:
        logger.error(f"Error retrieving audit logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve audit logs."
        )

@app.post("/api/memory", response_model=MemoryItemResponse)
def add_new_memory(memory_item: MemoryItemCreate):
    """Manages/Adds new memory for a user manually."""
    try:
        memory_id = database.add_memory(
            user_id=memory_item.user_id,
            tier=memory_item.tier,
            content=memory_item.content,
            significance_score=memory_item.significance_score
        )
        from datetime import datetime
        return {
            "id": memory_id,
            "user_id": memory_item.user_id,
            "tier": memory_item.tier,
            "content": memory_item.content,
            "significance_score": memory_item.significance_score,
            "created_at": datetime.utcnow()
        }
    except Exception as e:

        logger.error(f"Error adding memory: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add memory."
        )

@app.get("/api/memory/{user_id}", response_model=List[dict])
def get_user_memory(user_id: str):
    """Retrieves memory (STM/LTM) for a specific user."""
    try:
        memories = database.get_memories(user_id)
        return memories
    except Exception as e:
        logger.error(f"Error retrieving memory: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve memory."
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
