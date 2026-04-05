import instaloader
import os
import glob
import re

DOWNLOAD_DIR = "temp_videos"

def _extract_shortcode(url: str) -> str:
    """
    Extracts the shortcode from an Instagram reel URL.
    Handles formats like:
      - https://www.instagram.com/reel/ABC123/
      - https://instagram.com/reel/ABC123/?igsh=...
    """
    match = re.search(r"/reel/([A-Za-z0-9_-]+)", url)
    if not match:
        raise ValueError(f"Could not extract shortcode from URL: {url}")
    return match.group(1)


def fetch_reel_data(url: str) -> dict:
    """
    Fetches the Instagram reel's caption and downloads the video file.

    Returns a dict:
    {
        "caption": str or None,
        "video_path": str or None   <- local path to the downloaded .mp4
    }
    """
    shortcode = _extract_shortcode(url)
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    L = instaloader.Instaloader(
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False,
        quiet=True,
        dirname_pattern=DOWNLOAD_DIR
    )

    post = instaloader.Post.from_shortcode(L.context, shortcode)
    caption = post.caption  # Will be None if creator left it empty

    # Download the reel video
    L.download_post(post, target=DOWNLOAD_DIR)

    # Find the downloaded .mp4 file
    video_files = glob.glob(os.path.join(DOWNLOAD_DIR, "**", "*.mp4"), recursive=True)
    video_path = video_files[0] if video_files else None

    return {
        "caption": caption,
        "video_path": video_path
    }


def is_caption_substantial(caption: str | None) -> bool:
    """
    Decides if the caption holds the actual content.

    Logic:
    - If None or empty → not substantial
    - Strip all hashtags and mentions, then check remaining length
    - If remaining text is > 80 chars → substantial (creator wrote real content)
    - Otherwise → rely on transcript from video audio
    """
    if not caption:
        return False

    # Remove hashtags and mentions
    cleaned = re.sub(r"#\w+|@\w+", "", caption).strip()

    return len(cleaned) > 80


def cleanup_temp_files():
    """Removes all files in the temp_videos directory after processing."""
    import shutil
    if os.path.exists(DOWNLOAD_DIR):
        shutil.rmtree(DOWNLOAD_DIR)
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
