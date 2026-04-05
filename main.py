from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import setup_indexes
from routers import ingest, tips, study_guide

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_indexes()
    yield

app = FastAPI(
    title="Tech-Tip Vault",
    description=(
        "An asynchronous AI pipeline that ingests Instagram Reels, "
        "extracts technical knowledge using LLMs, and serves it as "
        "an on-demand, searchable study guide for developers."
    ),
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(ingest.router, tags=["Ingestion"])
app.include_router(tips.router, tags=["Vault"])
app.include_router(study_guide.router, tags=["Study Guide"])

@app.get("/", tags=["Health"])
def root():
    return {
        "status": "running",
        "message": "Tech-Tip Vault API is live.",
        "docs": "/docs"
    }