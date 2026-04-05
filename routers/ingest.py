from fastapi import APIRouter, BackgroundTasks, HTTPException
from models import IngestRequest, IngestResponse
from services.processing_service import run_ingestion_pipeline
import re

router = APIRouter()

def _is_valid_instagram_reel(url: str) -> bool:
    pattern = r"https?://(www\.)?instagram\.com/reel/[A-Za-z0-9_-]+/?"
    return bool(re.match(pattern, url))


@router.post("/tips/ingest", status_code=202, response_model=IngestResponse)
async def ingest_tip(request: IngestRequest, background_tasks: BackgroundTasks):
    """
    Accepts an Instagram reel URL.
    Returns 202 Accepted immediately (<10ms).
    The full pipeline (fetch → transcribe → LLM → store) runs in the background.
    """
    if not _is_valid_instagram_reel(request.url):
        raise HTTPException(
            status_code=400,
            detail="Invalid URL. Only Instagram Reel URLs are supported (e.g. https://www.instagram.com/reel/ABC123/)."
        )

    background_tasks.add_task(run_ingestion_pipeline, request.url)

    return IngestResponse(
        status="accepted",
        message="Reel received. Processing pipeline started in background.",
        url=request.url
    )
