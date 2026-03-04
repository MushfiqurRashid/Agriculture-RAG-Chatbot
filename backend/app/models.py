from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    conversation_id: str


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    chunks: int
    message: str


class DocumentInfo(BaseModel):
    document_id: str
    filename: str
    uploaded_at: str
    chunk_count: int


class HealthResponse(BaseModel):
    status: str
    documents_count: int
