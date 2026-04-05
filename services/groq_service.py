from groq import Groq
from config import GROQ_API_KEY
import json

client = Groq(api_key=GROQ_API_KEY)

WHISPER_MODEL = "whisper-large-v3"
LLM_MODEL = "llama-3.1-8b-instant"


def transcribe_video(video_path: str) -> str:
    """
    Sends the video file to Groq's Whisper API and returns the transcript.
    Groq Whisper accepts .mp4 files directly.
    """
    with open(video_path, "rb") as video_file:
        transcription = client.audio.transcriptions.create(
            file=(video_path, video_file.read()),
            model=WHISPER_MODEL,
            response_format="text"
        )
    return transcription


def process_with_llm(raw_content: str) -> dict:
    """
    Sends raw content (caption or transcript) to Groq LLM.

    The LLM is prompted to:
    1. Decide if this is a "tip" or "question"
    2. Assign a subcategory (e.g. "Java Core", "Spring Boot", "System Design")
    3. If TIP   → summarize, strip fillers, extract core insight
    4. If QUESTION → extract the question(s) cleanly, NO summarization
    5. Generate relevant tags

    Returns a strictly structured JSON dict.
    """

    prompt = f"""
You are an expert technical content classifier for a developer study guide app.

Analyze the following raw content from an Instagram reel (it could be a caption or a video transcript).

Your job:
1. Classify it as either "tip" or "question".
   - "question": content contains interview questions, quiz questions, or "what is X", "explain Y", "difference between X and Y" type content.
   - "tip": content contains advice, best practices, how-to guides, performance tricks, or general knowledge.

2. Assign ONE subcategory string. Be specific. Examples: "Java Core", "Spring Boot", "System Design", "DSA", "Python", "Databases", "Microservices", "Android", "REST APIs", "Docker", "Git", "OS Concepts", "Networking".

3. Process the content:
   - If "question": Extract ALL questions clearly and cleanly. Do NOT summarize. Do NOT add your own words. Just list the questions exactly as found.
   - If "tip": Remove ALL filler content (intros like "hey guys", outros like "follow for more", hashtag spam, emojis used as decoration). Extract and rewrite ONLY the core technical insight in clean, concise English.

4. Generate 2-5 relevant tags as a JSON array of strings. Tags should be specific technologies or concepts.

Respond ONLY with a valid JSON object. No explanation, no markdown, no extra text. Just the JSON.

JSON format:
{{
  "type": "tip" or "question",
  "subcategory": "subcategory string",
  "content": "processed content string",
  "tags": ["tag1", "tag2", "tag3"]
}}

Raw content to analyze:
\"\"\"
{raw_content}
\"\"\"
"""

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,   # low temperature = consistent, structured output
        max_tokens=1000
    )

    raw_json_str = response.choices[0].message.content.strip()

    # Strip markdown code fences if LLM adds them despite instructions
    if raw_json_str.startswith("```"):
        raw_json_str = raw_json_str.split("```")[1]
        if raw_json_str.startswith("json"):
            raw_json_str = raw_json_str[4:]
        raw_json_str = raw_json_str.strip()

    raw_json_str = "".join(ch for ch in raw_json_str if ord(ch) >= 32)

    return json.loads(raw_json_str)
