from datetime import datetime, timezone
from services.instagram_service import fetch_reel_data, is_caption_substantial, cleanup_temp_files
from services.groq_service import transcribe_video, process_with_llm
from database import tips_collection


def run_ingestion_pipeline(url: str):
    """
    The full async background pipeline:

    1. Fetch Instagram reel data (caption + download video)
    2. Decide content source: caption vs transcript
    3. Send raw content to Groq LLM
    4. Store structured result in MongoDB

    This runs entirely in the background after the API returns 202.
    """

    print(f"\n Starting ingestion pipeline for: {url}")
    source = None
    raw_content = None
    video_path = None

    try:
        # ── STEP 1: Fetch Instagram data ─────────────────────────────────────
        print(" Fetching Instagram reel data...")
        reel_data = fetch_reel_data(url)
        caption = reel_data["caption"]
        video_path = reel_data["video_path"]

        # ── STEP 2: Decide content source ─────────────────────────────────────
        if is_caption_substantial(caption):
            print("Caption is substantial. Using caption as content source.")
            raw_content = caption
            source = "caption"
        else:
            print("Caption is empty/minimal. Transcribing video audio via Groq Whisper...")
            if not video_path:
                raise Exception("No video downloaded and caption is not substantial. Cannot process.")
            raw_content = transcribe_video(video_path)
            source = "transcript"

        print(f"Raw content ({source}) ready. Length: {len(raw_content)} chars")

        # ── STEP 3: LLM Processing ────────────────────────────────────────────
        print("Sending to Groq LLM for classification and processing...")
        llm_result = process_with_llm(raw_content)

        print(f"LLM Result → type: {llm_result['type']} | subcategory: {llm_result['subcategory']}")

        # ── STEP 4: Store in MongoDB ───────────────────────────────────────────
        document = {
            "url": url,
            "type": llm_result["type"],
            "subcategory": llm_result["subcategory"],
            "content": llm_result["content"],
            "tags": llm_result["tags"],
            "source": source,
            "status": "processed",
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        tips_collection.insert_one(document)
        print(f"Saved to MongoDB → Collection: tips | Subcategory: {llm_result['subcategory']}\n")

    except Exception as e:
        # Store a failed record so we know what broke
        print(f"Pipeline failed for {url}: {str(e)}")
        tips_collection.insert_one({
            "url": url,
            "status": "failed",
            "error": str(e),
            "created_at": datetime.now(timezone.utc).isoformat()
        })

    finally:
        # Always clean up downloaded video files
        cleanup_temp_files()
        print("Temp files cleaned up.")
