from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class HRRequest(BaseModel):
    """
    Schema for incoming HR natural language requests.
    """
    user_id: str = Field(..., description="Unique identifier for the user.")
    query: str = Field(..., description="The natural language request.")

class HRResponse(BaseModel):
    """
    Schema for the response from the HR orchestration system.
    """
    user_id: str
    response: str
    intent: str
    confidence: float

class MemoryItemBase(BaseModel):
    """
    Base schema for a memory item.
    """
    user_id: str
    tier: str = Field(..., description="STM or LTM")
    content: str
    significance_score: float

class MemoryItemCreate(MemoryItemBase):
    pass

class MemoryItemResponse(MemoryItemBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class AuditLogResponse(BaseModel):
    """
    Schema for an audit log entry retrieval.
    """
    id: int
    timestamp: datetime
    user_id: str
    intent: str
    confidence: float
    routing_path: str
    status: str
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True
