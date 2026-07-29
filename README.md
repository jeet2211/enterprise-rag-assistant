# Enterprise RAG Assistant

A full-stack RAG application for uploading PDF documents and asking grounded questions with citations.

## Stack

- Backend: FastAPI, Celery, Redis, SQLite, ChromaDB, PyMuPDF, Sentence Transformers, Gemini
- Frontend: React, Vite, TypeScript
- Runtime: Docker + Docker Compose

## Features

- Upload PDF documents and process them asynchronously with a Redis-backed Celery worker
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
- Optional background processing values such as `REDIS_URL`, `CELERY_BROKER_URL`, or `CELERY_RESULT_BACKEND`

## Start the app with Docker

1. Copy `.env.example` to `.env` and set `GEMINI_API_KEY`.
2. Start the stack from the repository root:

```bash
docker compose up --build
```

3. Wait for the API, worker, Redis, and frontend services to start, then open:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`

## What happens on startup

- The backend creates the SQLite database if it does not exist
- The backend creates upload and Chroma persistence folders
- Redis starts as the Celery broker/result backend
- The worker consumes document-processing tasks from Redis
- The frontend is built and served by nginx
- The frontend talks to the backend at `http://localhost:8000/api/v1`

## Useful URLs

- `http://localhost:5173` - UI
- `http://localhost:8000/api/v1/health` - health check
- `http://localhost:8000/api/v1/health/worker` - Redis/Celery worker health check
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

## Endpoints

- `POST /api/v1/upload` - upload a PDF
- `POST /api/v1/chat` - ask a question about uploaded documents
- `GET /api/v1/documents` - list uploaded documents
- `GET /api/v1/documents/{id}` - poll processing status or inspect a document
- `DELETE /api/v1/documents/{id}` - remove a document
- `GET /api/v1/health` - service health check
- `GET /api/v1/health/worker` - Redis/Celery worker health check

## MCP server

The backend includes an MCP server that exposes the RAG assistant to MCP-compatible clients such as Claude Desktop,
Cursor, or Codex. It runs over stdio and calls the existing FastAPI backend, so start the backend first.

Install dependencies and run it locally:

```bash
cd backend
pip install -r requirements.txt
MCP_RAG_API_BASE_URL=http://localhost:8000/api/v1 python -m app.mcp_server
```

Example MCP client config:

```json
{
  "mcpServers": {
    "enterprise-rag-assistant": {
      "command": "python",
      "args": ["-m", "app.mcp_server"],
      "cwd": "/Users/jeet/Documents/Enterprice RAG Assistent/backend",
      "env": {
        "MCP_RAG_API_BASE_URL": "http://localhost:8000/api/v1"
      }
    }
  }
}
```

Available MCP tools:

- `check_rag_health`
- `check_worker_health`
- `list_documents`
- `get_document`
- `get_document_status`
- `ask_rag`
- `upload_pdf`
- `delete_document`

## Background processing

Uploads are queued through Celery:

1. The API saves the PDF and creates a document row with status `uploaded`.
2. The API enqueues a small task in Redis.
3. The worker reads the task, extracts PDF text, chunks it, embeds it, indexes it in ChromaDB, and updates the
   document status.

The Docker worker starts with `--concurrency=1` to avoid SQLite and ChromaDB write contention. Increase this only
after load testing, or move the database to Postgres first.

## Troubleshooting

- If uploads fail, verify the file is a PDF and smaller than `MAX_FILE_MB`
- If answers are empty or generic, check that `GEMINI_API_KEY` is set
- If Docker fails to bind ports, make sure nothing else is already using `5173` or `8000`
- If document processing is stuck before `ready`, check worker logs with `docker compose logs worker`
- If uploads return a queueing error, check Redis with `docker compose logs redis`
- If `/api/v1/health/worker` is degraded, confirm the Redis and worker containers are running
