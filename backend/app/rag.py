import os
import uuid
import hashlib
from datetime import datetime
from typing import Optional

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import OpenAI
from pypdf import PdfReader

from app.config import get_settings

settings = get_settings()

# --- OpenRouter LLM client ---
_llm_client = OpenAI(
    api_key=settings.openrouter_api_key,
    base_url=settings.openrouter_base_url,
)

# --- Text splitter ---
_splitter = RecursiveCharacterTextSplitter(
    chunk_size=settings.chunk_size,
    chunk_overlap=settings.chunk_overlap,
    separators=["\n\n", "\n", ". ", " ", ""],
)

# --- In-memory document & chunk store ---
_documents: dict[str, dict] = {}
_chunks: list[dict] = []  # Each: {"doc_id", "filename", "text", "chunk_index"}
_vectorizer: TfidfVectorizer | None = None
_tfidf_matrix = None


def _rebuild_tfidf():
    """Rebuild TF-IDF matrix from all stored chunks."""
    global _vectorizer, _tfidf_matrix
    if not _chunks:
        _vectorizer = None
        _tfidf_matrix = None
        return
    _vectorizer = TfidfVectorizer(stop_words="english", max_features=10000)
    texts = [c["text"] for c in _chunks]
    _tfidf_matrix = _vectorizer.fit_transform(texts)


def _extract_text(filepath: str, filename: str) -> str:
    """Extract text from PDF or plain text files."""
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".pdf":
        reader = PdfReader(filepath)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    else:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()


def ingest_document(filepath: str, filename: str) -> tuple[str, int]:
    """Ingest a document: extract text, chunk, and store in memory."""
    text = _extract_text(filepath, filename)
    if not text.strip():
        raise ValueError("Could not extract any text from the document.")

    chunks = _splitter.split_text(text)
    doc_id = hashlib.md5(filename.encode()).hexdigest()[:12]

    # Remove old chunks for this document if re-uploading
    global _chunks
    _chunks = [c for c in _chunks if c["doc_id"] != doc_id]

    # Add new chunks
    for i, chunk_text in enumerate(chunks):
        _chunks.append({
            "doc_id": doc_id,
            "filename": filename,
            "text": chunk_text,
            "chunk_index": i,
        })

    _documents[doc_id] = {
        "document_id": doc_id,
        "filename": filename,
        "uploaded_at": datetime.now().isoformat(),
        "chunk_count": len(chunks),
    }

    _rebuild_tfidf()
    return doc_id, len(chunks)


def delete_document(doc_id: str) -> bool:
    """Delete a document and its chunks."""
    global _chunks
    if doc_id not in _documents:
        return False
    _chunks = [c for c in _chunks if c["doc_id"] != doc_id]
    del _documents[doc_id]
    _rebuild_tfidf()
    return True


def get_documents() -> list[dict]:
    """List all ingested documents."""
    return list(_documents.values())


def _retrieve_context(query: str, top_k: int = 5) -> list[dict]:
    """Retrieve the most relevant chunks using TF-IDF cosine similarity."""
    if not _chunks or _vectorizer is None or _tfidf_matrix is None:
        return []

    query_vec = _vectorizer.transform([query])
    scores = cosine_similarity(query_vec, _tfidf_matrix).flatten()

    top_indices = scores.argsort()[::-1][:top_k]
    contexts = []
    for idx in top_indices:
        if scores[idx] > 0.0:
            contexts.append({
                "text": _chunks[idx]["text"],
                "filename": _chunks[idx]["filename"],
                "score": float(scores[idx]),
            })
    return contexts


# --- Conversation history (in-memory) ---
_conversations: dict[str, list[dict]] = {}

SYSTEM_PROMPT = """You are a helpful assistant that answers questions based on the provided context documents. 
Follow these rules:
- Answer ONLY using information from the provided context.
- If the context doesn't contain enough information, say so clearly.
- Cite the source filename when referencing information.
- Be concise and accurate.
- Use markdown formatting for readability."""


def chat(message: str, conversation_id: Optional[str] = None) -> tuple[str, str]:
    """Process a chat message with RAG retrieval and return response."""
    if not conversation_id:
        conversation_id = uuid.uuid4().hex[:16]

    if conversation_id not in _conversations:
        _conversations[conversation_id] = []

    # Retrieve relevant context
    contexts = _retrieve_context(message)

    # Build context string
    if contexts:
        context_str = "\n\n---\n\n".join(
            f"[Source: {c['filename']}]\n{c['text']}" for c in contexts
        )
        user_content = f"Context:\n{context_str}\n\n---\n\nQuestion: {message}"
    else:
        user_content = (
            f"No documents have been uploaded yet. The user asked: {message}\n\n"
            "Please let them know they should upload documents first to get contextual answers."
        )

    # Build message history
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(_conversations[conversation_id][-6:])
    messages.append({"role": "user", "content": user_content})

    # Call LLM via OpenRouter
    response = _llm_client.chat.completions.create(
        model=settings.llm_model,
        messages=messages,
        temperature=0.3,
        max_tokens=2048,
    )

    assistant_message = response.choices[0].message.content

    # Store in conversation history
    _conversations[conversation_id].append({"role": "user", "content": message})
    _conversations[conversation_id].append({"role": "assistant", "content": assistant_message})

    # Trim history
    if len(_conversations[conversation_id]) > 20:
        _conversations[conversation_id] = _conversations[conversation_id][-20:]

    return assistant_message, conversation_id
