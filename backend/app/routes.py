import os
import shutil
import secrets
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from app.models import (
    ChatRequest, ChatResponse, UploadResponse,
    DocumentInfo, HealthResponse,
)
from app.rag import ingest_document, delete_document, get_documents, chat

router = APIRouter(prefix="/api", tags=["RAG Chatbot"])
security = HTTPBasic()

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def require_admin(credentials: HTTPBasicCredentials = Depends(security)) -> None:
    username_ok = secrets.compare_digest(credentials.username, "fairfarm")
    password_ok = secrets.compare_digest(credentials.password, "fairfarm")
    if not (username_ok and password_ok):
        raise HTTPException(
            status_code=401,
            detail="Invalid admin credentials",
            headers={"WWW-Authenticate": "Basic"},
        )


@router.get("/health", response_model=HealthResponse, summary="Health check")
async def health():
    docs = get_documents()
    return HealthResponse(status="ok", documents_count=len(docs))


@router.post("/chat", response_model=ChatResponse, summary="Send a chat message")
async def chat_endpoint(req: ChatRequest):
    """Send a message and receive a RAG-augmented response from the LLM."""
    try:
        response, conv_id = chat(req.message, req.conversation_id)
        return ChatResponse(
            response=response,
            conversation_id=conv_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/admin/upload",
    response_model=UploadResponse,
    summary="Upload a document (admin)",
)
async def upload_document(
    _: None = Depends(require_admin),
    file: UploadFile = File(...),
):
    """Upload a PDF or TXT file to be ingested into the RAG pipeline."""
    allowed = {".pdf", ".txt", ".md", ".csv"}
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(allowed)}",
        )

    filepath = os.path.join(UPLOAD_DIR, file.filename)
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        doc_id, chunks = ingest_document(filepath, file.filename)
    except ValueError as e:
        os.remove(filepath)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        os.remove(filepath)
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")

    return UploadResponse(
        document_id=doc_id,
        filename=file.filename,
        chunks=chunks,
        message=f"Successfully ingested '{file.filename}' into {chunks} chunks.",
    )


@router.get(
    "/admin/documents",
    response_model=list[DocumentInfo],
    summary="List documents (admin)",
)
async def list_documents(_: None = Depends(require_admin)):
    """List all ingested documents."""
    docs = get_documents()
    return [DocumentInfo(**d) for d in docs]


@router.delete("/admin/documents/{doc_id}", summary="Delete a document (admin)")
async def remove_document(doc_id: str, _: None = Depends(require_admin)):
    """Remove a document and its chunks from the vector store."""
    if not delete_document(doc_id):
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"message": "Document deleted successfully."}
