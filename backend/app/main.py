from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routes import router

settings = get_settings()

app = FastAPI(
    title="RAG Chatbot API",
    description="A production-level RAG chatbot API powered by OpenRouter. Upload documents and chat with them using AI.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/", tags=["Root"])
async def root():
    return {"message": "RAG Chatbot API is running. Visit /docs for Swagger UI."}
