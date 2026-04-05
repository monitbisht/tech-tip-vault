from fastapi import APIRouter, Query, HTTPException
from database import tips_collection

router = APIRouter()


def _serialize(doc) -> dict:
    """Converts MongoDB document to JSON-serializable dict."""
    doc["_id"] = str(doc["_id"])
    return doc


# ─────────────────────────────────────────────
#  QUESTIONS ENDPOINTS
# ─────────────────────────────────────────────

@router.get("/questions/")
def get_all_questions():
    """
    Returns all subcategories available under Questions.
    e.g. { "subcategories": ["Java Core", "Spring Boot", "DSA"] }
    """
    pipeline = [
        {"$match": {"status": "processed", "type": "question"}},
        {"$group": {"_id": "$subcategory", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    raw = list(tips_collection.aggregate(pipeline))
    return {
        "subcategories": [{"name": r["_id"], "count": r["count"]} for r in raw]
    }


@router.get("/questions/{subcategory}")
def get_questions_by_subcategory(subcategory: str):
    """
    Returns all questions under a specific subcategory.
    e.g. GET /questions/Java Core
    """
    cursor = tips_collection.find(
        {
            "status": "processed",
            "type": "question",
            "subcategory": {"$regex": f"^{subcategory}$", "$options": "i"}
        },
        {"_id": 1, "content": 1, "tags": 1, "source": 1, "url": 1}
    )
    results = [_serialize(doc) for doc in cursor]

    if not results:
        raise HTTPException(status_code=404, detail=f"No questions found for subcategory: '{subcategory}'")

    return {
        "subcategory": subcategory,
        "count": len(results),
        "questions": results
    }


# ─────────────────────────────────────────────
#  TIPS ENDPOINTS
# ─────────────────────────────────────────────

@router.get("/tips/")
def get_all_tips():
    """
    Returns all subcategories available under Tips.
    e.g. { "subcategories": ["Spring Boot", "System Design", "Performance"] }
    """
    pipeline = [
        {"$match": {"status": "processed", "type": "tip"}},
        {"$group": {"_id": "$subcategory", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    raw = list(tips_collection.aggregate(pipeline))
    return {
        "subcategories": [{"name": r["_id"], "count": r["count"]} for r in raw]
    }


@router.get("/tips/{subcategory}")
def get_tips_by_subcategory(subcategory: str):
    """
    Returns all tips under a specific subcategory.
    e.g. GET /tips/Spring Boot
    """
    cursor = tips_collection.find(
        {
            "status": "processed",
            "type": "tip",
            "subcategory": {"$regex": f"^{subcategory}$", "$options": "i"}
        },
        {"_id": 1, "content": 1, "tags": 1, "source": 1, "url": 1}
    )
    results = [_serialize(doc) for doc in cursor]

    if not results:
        raise HTTPException(status_code=404, detail=f"No tips found for subcategory: '{subcategory}'")

    return {
        "subcategory": subcategory,
        "count": len(results),
        "tips": results
    }


# ─────────────────────────────────────────────
#  SEARCH (across both)
# ─────────────────────────────────────────────

@router.get("/search/")
def search_by_tag(tag: str = Query(..., description="Tag to search for e.g. 'Java', 'Spring Boot'")):
    """Queries the multikey index to return all content matching a tag."""
    if not tag.strip():
        raise HTTPException(status_code=400, detail="Tag cannot be empty.")

    cursor = tips_collection.find(
        {
            "status": "processed",
            "tags": {"$regex": f"^{tag}$", "$options": "i"}
        },
        {"_id": 1, "type": 1, "subcategory": 1, "content": 1, "tags": 1}
    )
    results = [_serialize(doc) for doc in cursor]
    return {"tag": tag, "count": len(results), "results": results}
