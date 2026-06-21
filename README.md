# Enterprise RAG Assistant

A full-stack RAG application for uploading PDF documents and asking grounded questions with citations.

## Stack

- Backend: FastAPI, SQLite, ChromaDB, PyMuPDF, Sentence Transformers, Gemini
- Frontend: React, Vite, TypeScript
- Runtime: Docker + Docker Compose

## Features

- Upload PDF documents and process them in the background
- Ask questions grounded in the uploaded documents
- See citations with document name and page number
- Delete documents and clear chat sessions
- Run the full stack with Docker Compose

## Requirements

- Docker and Docker Compose
- A Gemini API key
- Optional for local development without Docker:
  - Python 3.11+
  - Node.js 20+

## Configuration

1. Copy the example environment file:

```bash
cp .env.example .env
```

2. Open `.env` and set:

- `GEMINI_API_KEY`
- Any optional tuning values you want to change, such as `CHUNK_SIZE`, `TOP_K`, or `MAX_FILE_MB`

## Start the app with Docker

1. Copy `.env.example` to `.env` and set `GEMINI_API_KEY`.
2. Start the stack from the repository root:

```bash
docker compose up --build
```

3. Wait for both services to start, then open:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`

## What happens on startup

- The backend creates the SQLite database if it does not exist
- The backend creates upload and Chroma persistence folders
- The frontend is built and served by nginx
- The frontend talks to the backend at `http://localhost:8000/api/v1`

## Useful URLs

- `http://localhost:5173` - UI
- `http://localhost:8000/api/v1/health` - health check
- `http://localhost:8000/docs` - Swagger UI
- `http://localhost:8000/redoc` - ReDoc

## Stop the app

```bash
docker compose down
```

## Reset local data

Use this if you want to remove the database, uploads, and vector store volumes:

```bash
docker compose down -v
```

## Local development without Docker

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

If you run the frontend locally, make sure `VITE_API_BASE_URL` points to the backend API, for example:

```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## Testing

Backend test setup:

```bash
cd backend
pip install -r requirements-dev.txt
pytest
```

Frontend test setup:

```bash
cd frontend
npm install
npm run test
```

Coverage reports:

```bash
cd backend
pytest --cov=app --cov-report=term-missing
```

```bash
cd frontend
npm run test:coverage
```

The backend suite covers:

- Settings parsing and validation
- PDF upload validation
- Chunking, retrieval, embedding, and PDF wrappers
- Document CRUD and pipeline behavior
- Health, upload, chat, and document API routes

The frontend suite covers:

- API client wrappers
- `useChat` and `useDocuments` state flows
- The chat composer UI

## Endpoints

- `POST /api/v1/upload` - upload a PDF
- `POST /api/v1/chat` - ask a question about uploaded documents
- `GET /api/v1/documents` - list uploaded documents
- `GET /api/v1/documents/{id}` - poll processing status or inspect a document
- `DELETE /api/v1/documents/{id}` - remove a document
- `GET /api/v1/health` - service health check

## Troubleshooting

- If uploads fail, verify the file is a PDF and smaller than `MAX_FILE_MB`
- If answers are empty or generic, check that `GEMINI_API_KEY` is set
- If Docker fails to bind ports, make sure nothing else is already using `5173` or `8000`
- If document processing is stuck on `processing`, check backend logs for PDF parsing or embedding errors
