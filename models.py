from pydantic import BaseModel
from typing import Optional

class IngestRequest(BaseModel):
    url: str

class IngestResponse(BaseModel):
    status: str
    message: str
    url: str

class TipDocument(BaseModel):
    url: str
    type: str              # "tip" or "question"
    subcategory: str       # AI-generated e.g. "Java Core", "Spring Boot"
    content: str           # summarized tip OR raw question(s)
    tags: list[str]        # AI-generated tags e.g. ["Java", "Interview"]
    source: str            # "caption" or "transcript"
    status: str            # "processed" or "failed"
    created_at: Optional[str] = None
