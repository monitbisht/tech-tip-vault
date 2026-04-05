# Tech-Tip Vault 🗄️

![Platform](https://img.shields.io/badge/Platform-Backend_API-009688?logo=fastapi&logoColor=white)
![Language](https://img.shields.io/badge/Language-Python-3776AB?logo=python&logoColor=white)

## Description

**Tech-Tip Vault** is an asynchronous AI-powered backend API that solves a problem every developer faces — valuable technical knowledge consumed across Instagram Reels gets watched once and forgotten.

The application provides a centralized pipeline to ingest Instagram Reels, automatically detect whether the core content lives in the caption or the spoken audio, extract and categorize it using an LLM, and index it into a searchable knowledge base organized by topic. The result is an on-demand, queryable study guide for interview preparation and technical learning — built entirely from content you already consume.

## Table of Contents
* [Key Features](#key-features)
* [Tech Stack](#tech-stack)
* [API Endpoints](#api-endpoints)
* [Installation](#installation)
* [Usage](#usage)
* [Project Structure](#project-structure)
* [Contact](#contact)

## Key Features

* **Smart Content Source Detection:** Automatically decides whether to use the reel's caption or transcribe the video audio via Groq Whisper, correctly handling both spoken-content reels and music-only reels where all the value is in the caption.
* **AI Classification and Extraction:** Uses a Groq LLM to classify each piece of content as a tip or an interview question, assign it a subcategory (e.g. Java Core, Spring Boot, System Design), and either summarize it or extract questions cleanly depending on the type.
* **Dynamic NoSQL Schema:** MongoDB's flexible document model stores AI-generated tags and subcategories without requiring schema migrations as new categories emerge.
* **On-Demand Study Guides:** Aggregation pipeline endpoints filter and flatten stored content by topic into clean, focused study guides ready for interview preparation.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10+ |
| Framework | FastAPI + Uvicorn |
| Database | MongoDB Atlas (PyMongo) |
| LLM | Groq API — `llama-3.1-8b-instant` |
| Transcription | Groq Whisper — `whisper-large-v3` |
| Instagram Fetching | `instaloader` |
| Validation | Pydantic v2 |
| Docs | Swagger UI (auto-generated at `/docs`) |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/tips/ingest` | Accepts an Instagram Reel URL, returns `202 Accepted`, triggers the background pipeline |
| `GET` | `/questions/` | Returns all available question subcategories |
| `GET` | `/questions/{subcategory}` | Returns all questions under a specific subcategory |
| `GET` | `/tips/` | Returns all available tip subcategories |
| `GET` | `/tips/{subcategory}` | Returns all tips under a specific subcategory |
| `GET` | `/search/?tag=` | Searches across all content by tag |
| `GET` | `/study-guide/{tag}` | Aggregates and flattens all content for a tag into a study guide |

## Installation

### Prerequisites
- Python 3.10+
- MongoDB Atlas account (free tier works)
- Groq API key — [Get one free at console.groq.com](https://console.groq.com)

### Steps

1. **Clone the repository**
    ```bash
    git clone https://github.com/monitbisht/tech-tip-vault.git
    cd tech-tip-vault
    ```

2. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3. **Configure environment**
    ```bash
    # Create a .env file in the root directory with the following keys:
    # GROQ_API_KEY=gsk_...
    # MONGO_URI=mongodb+srv://...
    # DB_NAME=tech_tip_vault
    ```

4. **Run the server**
    ```bash
    uvicorn main:app --reload
    ```

Visit `http://localhost:8000/docs` for the interactive Swagger UI.

## Usage

**Ingest a Reel**
```bash
curl -X POST http://localhost:8000/tips/ingest \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.instagram.com/reel/ABC123/"}'
```

**Browse Questions by Subcategory**
```bash
curl http://localhost:8000/questions/Java Core
```

**Get a Study Guide**
```bash
curl http://localhost:8000/study-guide/Spring Boot
```

## Project Structure

```
tech-tip-vault/
├── main.py                         # FastAPI app entry point
├── config.py                       # Environment variable loading
├── database.py                     # MongoDB connection and index setup
├── models.py                       # Pydantic request/response models
├── services/
│   ├── instagram_service.py        # Caption fetching and video download
│   ├── groq_service.py             # Whisper transcription and LLM processing
│   └── processing_service.py       # Full pipeline orchestration
├── routers/
│   ├── ingest.py                   # POST /tips/ingest
│   ├── tips.py                     # Questions and Tips endpoints
│   └── study_guide.py              # Study guide aggregation endpoints
├── requirements.txt
└── .env.example
```

## Contact

Created by **Monit Bisht** — Aspiring Backend Developer.

* [GitHub Profile](https://github.com/monitbisht)
* **Email:** monitbisht15@gmail.com
