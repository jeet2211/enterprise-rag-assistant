# Enterprise RAG Assistant

A full-stack RAG application for uploading PDF documents and asking grounded questions with citations.

## Stack

- Backend: FastAPI, SQLite, ChromaDB, PyMuPDF, Sentence Transformers, Gemini
- Frontend: React, Vite, TypeScript
- Runtime: Docker + Docker Compose

## Quick start

1. Copy `.env.example` to `.env` and set `GEMINI_API_KEY`.
2. Start the stack:

```bash
docker compose up --build
```

3. Open:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`

