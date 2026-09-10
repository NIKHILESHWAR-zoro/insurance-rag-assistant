from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import upload, query, compare

app = FastAPI(
    title="Insurance Policy Comparator & Claim Helper API",
    description="RAG-based API for querying and comparing insurance policy documents.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(query.router)
app.include_router(compare.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "insurance-rag-assistant-api"}


@app.get("/health")
def health():
    return {"status": "healthy"}
