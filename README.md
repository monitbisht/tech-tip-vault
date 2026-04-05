# Tech-Tip Vault 🗄️

> An asynchronous AI-driven backend pipeline that ingests Instagram Reels, extracts technical knowledge using LLMs, and serves it as an on-demand, searchable developer study guide.

---

## 📖 Problem Statement

Developers constantly consume valuable technical content — interview questions, system design tips, best practices — across Instagram Reels. This knowledge is watched once and forgotten. **Tech-Tip Vault** solves this by automatically extracting, categorizing, and indexing that content into a structured, queryable knowledge base.

---

## 🏗️ Architecture

```
POST /tips/ingest (Instagram Reel URL)
          │
          ▼
  ┌───────────────────┐
  │  202 Accepted     │  ← Returns instantly (<10ms)
  │  (main thread)    │
  └───────────────────┘
          │
          ▼  Background Task
  ┌────────────────────────────────────────────┐
  │           INGESTION PIPELINE               │
  │                                            │
  │  1. instaloader → fetch caption + video    │
  │                                            │
  │  2. Content Source Decision:               │
  │     ┌──────────────┬───────────────────┐   │
  │     │ Caption has  │  Caption empty /  │   │
  │     │ real content │  music-only reel  │   │
  │     │     ↓        │        ↓          │   │
  │     │ Use caption  │  Groq Whisper     │   │
  │     │              │  (transcription)  │   │
  │     └──────────────┴───────────────────┘   │
  │                    ↓                       │
  │  3. Groq LLM (llama3-8b-8192)              │
  │     - Classify: tip or question            │
  │     - Assign subcategory (e.g. Java Core)  │
  │     - Summarize tips / extract questions   │
  │     - Generate tags                        │
  │                    ↓                       │
  │  4. MongoDB Atlas (insert document)        │
  └────────────────────────────────────────────┘
```

---

## 💻 Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10+ |
| Framework | FastAPI + Uvicorn |
| Database | MongoDB Atlas (PyMongo) |
| LLM | Groq API — `llama3-8b-8192` |
| Transcription | Groq Whisper — `whisper-large-v3` |
| Instagram Fetching | `instaloader` |
| Validation | Pydantic v2 |
| Docs | Swagger UI (auto-generated at `/docs`) |

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/tips/ingest` | Accepts Instagram Reel URL, returns `202 Accepted`, triggers background pipeline |
| `GET` | `/tips/` | Paginated vault of all processed tips and questions |
| `GET` | `/tips/search/?tag=` | Queries multikey index to return all content matching a tag |
| `GET` | `/tips/categories/` | Returns all types and subcategories (for dynamic menu building) |
| `GET` | `/study-guide/{tag}` | Aggregation pipeline: groups and flattens all content for a tag into a study guide |
| `GET` | `/study-guide/{tag}/subcategory/{subcategory}` | Drill-down: content filtered by both tag and subcategory |

---

## ⚙️ Key Technical Decisions

### 1. Non-Blocking Ingestion (BackgroundTasks)
LLM inference + video transcription can take 10–30 seconds. Running this synchronously would block the server. By offloading to FastAPI's `BackgroundTasks`, the endpoint returns `202 Accepted` in under **10ms** regardless of LLM latency.

### 2. Dynamic NoSQL Schema (MongoDB)
AI-generated subcategories are unpredictable. A rigid SQL schema would require migrations every time the LLM creates a new category. MongoDB's flexible document model stores dynamic tag arrays natively.

**Multikey Indexes** are created on startup on the `tags` array field, enabling sub-50ms queries across all AI-generated categories.

### 3. Content Source Detection
Not all reels have speech. The pipeline first checks the caption (stripping hashtags/mentions). If substantial content exists there, it's used directly. Otherwise, the video is transcribed via Groq Whisper — handling music-only reels correctly.

### 4. Strict JSON Prompting
The LLM is prompted with `temperature=0.2` and explicit JSON format instructions to ensure consistent, parseable outputs. Markdown fences are stripped defensively in case the model adds them.

---

## 🚀 Setup & Running

### Prerequisites
- Python 3.10+
- MongoDB Atlas account (free tier works)
- Groq API key — [Get one free at console.groq.com](https://console.groq.com)

### Installation

```bash
git clone https://github.com/yourusername/tech-tip-vault
cd tech-tip-vault

pip install -r requirements.txt
```

### Configuration

```bash
cp .env.example .env
# Edit .env with your actual keys:
# GROQ_API_KEY=gsk_...
# MONGO_URI=mongodb+srv://...
# DB_NAME=tech_tip_vault
```

### Run

```bash
uvicorn main:app --reload
```

Visit `http://localhost:8000/docs` for the interactive Swagger UI.

---

## 📦 Example Usage

### Ingest a Reel
```bash
curl -X POST http://localhost:8000/tips/ingest \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.instagram.com/reel/ABC123/"}'
```

**Response (instant):**
```json
{
  "status": "accepted",
  "message": "Reel received. Processing pipeline started in background.",
  "url": "https://www.instagram.com/reel/ABC123/"
}
```

### Search by Tag
```bash
curl "http://localhost:8000/tips/search/?tag=Java"
```

### Get Study Guide
```bash
curl "http://localhost:8000/study-guide/Spring Boot"
```

**Response:**
```json
{
  "tag": "Spring Boot",
  "total_items": 12,
  "sections": {
    "questions": {
      "count": 7,
      "items": [...]
    },
    "tips": {
      "count": 5,
      "items": [...]
    }
  }
}
```

---

## 📁 Project Structure

```
tech-tip-vault/
├── main.py                         # FastAPI app entry point
├── config.py                       # Environment variable loading
├── database.py                     # MongoDB connection + index setup
├── models.py                       # Pydantic request/response models
├── services/
│   ├── instagram_service.py        # instaloader: caption fetch + video download
│   ├── groq_service.py             # Whisper transcription + LLM processing
│   └── processing_service.py       # Full pipeline orchestration
├── routers/
│   ├── ingest.py                   # POST /tips/ingest
│   ├── tips.py                     # GET /tips/, /tips/search/, /tips/categories/
│   └── study_guide.py              # GET /study-guide/{tag}
├── requirements.txt
└── .env.example
```
