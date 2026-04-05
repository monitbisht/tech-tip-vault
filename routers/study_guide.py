from fastapi import APIRouter, HTTPException
from database import tips_collection

router = APIRouter()


@router.get("/study-guide/{tag}")
def get_study_guide(tag: str):
    """
    Aggregation endpoint for generating an on-demand study guide for a given tag.

    Pipeline:
    1. Match all processed documents containing the tag (case-insensitive)
    2. Group by type (tip vs question)
    3. Flatten and return content as a clean, structured study guide
    """

    pipeline = [
        # Stage 1: Filter by tag (case-insensitive) and status
        {
            "$match": {
                "status": "processed",
                "tags": {"$regex": f"^{tag}$", "$options": "i"}
            }
        },
        # Stage 2: Project only the fields we need
        {
            "$project": {
                "_id": 0,
                "type": 1,
                "subcategory": 1,
                "content": 1,
                "source": 1
            }
        },
        # Stage 3: Group by type, push all content into arrays
        {
            "$group": {
                "_id": "$type",
                "items": {
                    "$push": {
                        "subcategory": "$subcategory",
                        "content": "$content",
                        "source": "$source"
                    }
                },
                "count": {"$sum": 1}
            }
        },
        # Stage 4: Sort so questions come before tips
        {"$sort": {"_id": 1}}
    ]

    raw = list(tips_collection.aggregate(pipeline))

    if not raw:
        raise HTTPException(
            status_code=404,
            detail=f"No content found for tag: '{tag}'. Try a different tag."
        )

    # Restructure into a clean study guide format
    study_guide = {
        "tag": tag,
        "total_items": sum(group["count"] for group in raw),
        "sections": {}
    }

    for group in raw:
        content_type = group["_id"]   # "tip" or "question"
        study_guide["sections"][content_type + "s"] = {
            "count": group["count"],
            "items": group["items"]
        }

    return study_guide


@router.get("/study-guide/{tag}/subcategory/{subcategory}")
def get_study_guide_by_subcategory(tag: str, subcategory: str):
    """
    Drill-down endpoint: returns only content for a specific tag + subcategory combo.
    Example: GET /study-guide/Java/subcategory/Java Core
    Flattens all questions/tips into a single clean list.
    """

    pipeline = [
        {
            "$match": {
                "status": "processed",
                "tags": {"$regex": f"^{tag}$", "$options": "i"},
                "subcategory": {"$regex": f"^{subcategory}$", "$options": "i"}
            }
        },
        {
            "$project": {
                "_id": 0,
                "type": 1,
                "content": 1,
                "source": 1,
                "created_at": 1
            }
        }
    ]

    results = list(tips_collection.aggregate(pipeline))

    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"No content found for tag '{tag}' in subcategory '{subcategory}'."
        )

    return {
        "tag": tag,
        "subcategory": subcategory,
        "count": len(results),
        "items": results
    }
