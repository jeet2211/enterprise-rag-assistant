# Enterprise RAG Assistant Developer Learning Guide

This guide is for a junior developer joining the Enterprise RAG Assistant codebase. It explains what the project does, where to start, how the pieces fit together, and how to make changes safely.

## 1. Project Overview

Enterprise RAG Assistant is a full-stack app for uploading PDF documents and asking questions about them. The assistant answers from uploaded document content and returns citations so users can verify where an answer came from.

The main problem it solves is grounded enterprise document Q&A: instead of asking a general chatbot and hoping it knows the answer, users upload PDFs and the app retrieves relevant chunks from those PDFs before asking Gemini to answer.

Target users are people who need to search, summarize, compare, or inspect business documents such as policies, contracts, procedures, technical docs, reports, or internal PDFs.

At a high level:

- The React frontend lets users upload PDFs, view processing status, select document filters, ask questions, and inspect citations.
- The FastAPI backend exposes upload, document, chat, health, and feedback APIs.
- Uploaded PDFs are saved to disk and tracked in SQLite through SQLAlchemy models.
- Celery and Redis process documents in the background.
- PyMuPDF extracts PDF text.
- A local Sentence Transformers model creates embeddings.
- ChromaDB stores vector-indexed document chunks.
- Chat requests retrieve relevant chunks from ChromaDB and use Gemini through LangChain to generate a grounded answer.

```text
User
  |
  v
React UI (frontend/src)
  |
  v
FastAPI routes (backend/app/api/routes)
  |
  +--> Upload path: save PDF -> DB row -> Celery task -> PDF text -> chunks -> embeddings -> ChromaDB
  |
  +--> Chat path: question -> retrieve ChromaDB chunks -> build grounded prompt -> Gemini -> answer + citations
  |
  v
SQLite metadata + uploaded files + ChromaDB vector store
```

## 2. Starting Point for a Junior Developer

Start with these files:

1. `README.md` for the product summary, Docker startup, endpoints, and environment setup.
2. `docker-compose.yml` to understand the running services: `redis`, `backend`, `worker`, and `frontend`.
3. `backend/app/main.py` to see how the API app is assembled.
4. `backend/app/services/factory.py` to see which services are created at startup.
5. `backend/app/api/routes/upload.py` and `backend/app/tasks/document_tasks.py` to understand document ingestion.
6. `backend/app/services/chat_service.py`, `backend/app/rag/retriever.py`, and `backend/app/rag/prompt.py` to understand RAG answering.
7. `frontend/src/pages/App.tsx`, `frontend/src/hooks/useDocuments.ts`, and `frontend/src/hooks/useChat.ts` to understand the UI state flow.

Best backend entry points:

- API app: `backend/app/main.py`
- Upload endpoint: `backend/app/api/routes/upload.py`
- Chat endpoints: `backend/app/api/routes/chat.py`
- Service wiring: `backend/app/services/factory.py`
- Background worker task: `backend/app/tasks/document_tasks.py`

Best frontend entry points:

- Browser entry: `frontend/src/main.tsx`
- Main app layout: `frontend/src/pages/App.tsx`
- Backend API wrapper: `frontend/src/api/client.ts`
- Document state hook: `frontend/src/hooks/useDocuments.ts`
- Chat state hook: `frontend/src/hooks/useChat.ts`

Ignore at first:

- `backend/alembic/` until you need database migrations.
- `scripts/run_rag_eval.py` and `evals/` until you need RAG quality evaluation.
- Dockerfile details until you need deployment or container debugging.
- Low-level styling in `frontend/src/index.css` and `frontend/tailwind.config.js` until you are changing UI design.

## 3. Project Structure

Repository root:

- `README.md`: setup instructions, feature summary, endpoint list, and troubleshooting.
- `.env.example`: sample configuration. Copy this to `.env`.
- `.env`: local secrets and runtime config. Do not commit real secrets.
- `docker-compose.yml`: defines Redis, backend API, Celery worker, and frontend nginx services.
- `docs/`: documentation. This guide lives here.
- `scripts/run_rag_eval.py`: command-line evaluator that sends a golden dataset to the running backend.
- `evals/golden_dataset.json`: sample RAG evaluation questions.

Backend:

- `backend/app/main.py`: creates the FastAPI app, configures CORS, rate limiting, logging, exception handling, startup lifespan, and routers.
- `backend/app/config/settings.py`: Pydantic settings loaded from environment variables and `.env`.
- `backend/app/api/deps.py`: small FastAPI dependency helpers that read services from `request.app.state`.
- `backend/app/api/routes/`: API route modules:
  - `upload.py`: validates, hashes, saves, deduplicates, records, and queues PDFs.
  - `documents.py`: lists, inspects, polls, and deletes documents.
  - `chat.py`: normal and streaming chat endpoints.
  - `health.py`: backend, ChromaDB, Gemini config, Redis, and Celery health endpoints.
  - `feedback.py`: records thumbs-up/thumbs-down feedback.
- `backend/app/models/`: data contracts and database models:
  - `db.py`: SQLAlchemy models and engine/session helpers.
  - `requests.py`: request Pydantic models.
  - `responses.py`: response Pydantic models.
- `backend/app/services/`: business services:
  - `factory.py`: builds database, embedding, retriever, document, PDF, memory, chat, and pipeline services.
  - `document_service.py`: CRUD operations for document metadata.
  - `pdf_service.py`: PDF text extraction and basic section title detection.
  - `embedding_service.py`: lazy-loads Sentence Transformers and embeds text/query strings.
  - `chat_service.py`: retrieval, prompt building, Gemini call, confidence, verifier, streaming, and DB persistence.
- `backend/app/rag/`: RAG-specific code:
  - `chunker.py`: turns page text into overlapping word chunks.
  - `retriever.py`: ChromaDB storage, vector search, metadata filters, and MMR reranking.
  - `pipeline.py`: document processing workflow.
  - `prompt.py`: system prompt, answer prompt, follow-up prompt, and verifier prompt.
- `backend/app/tasks/`: Celery configuration and document processing task.
- `backend/app/core/rate_limit.py`: SlowAPI limiter setup.
- `backend/app/utils/`: validators and JSON logging helpers.
- `backend/tests/`: pytest tests.
- `backend/alembic/`: database migration support.
- `backend/requirements.txt`: Python dependencies.
- `backend/pyproject.toml`: ruff, mypy, and pytest configuration.
- `backend/Dockerfile` and `backend/docker-entrypoint.sh`: backend/worker container setup.

Frontend:

- `frontend/src/main.tsx`: React bootstrap.
- `frontend/src/pages/App.tsx`: top-level layout and state composition.
- `frontend/src/api/client.ts`: all browser-to-backend API calls, including SSE parsing for streaming chat.
- `frontend/src/hooks/useDocuments.ts`: document list, upload, delete, selection, and polling state.
- `frontend/src/hooks/useChat.ts`: session ID, messages, streaming answer updates, and chat errors.
- `frontend/src/components/`: UI components:
  - `Sidebar.tsx`: document library, search, selection, delete, upload container.
  - `UploadZone.tsx`: drag/drop and file chooser.
  - `ChatWindow.tsx`: chat shell, input form, dashboard toggle, clear conversation.
  - `MessageBubble.tsx`: user/assistant bubbles, citations, feedback, trace display.
  - `CitationCard.tsx`: expandable source cards.
  - `ConfidenceBadge.tsx`: visual confidence labels.
  - `FollowUpChips.tsx`: follow-up question buttons.
  - `Dashboard.tsx`: health stats panel.
  - `ErrorToast.tsx`: shared error display.
  - `LoadingDots.tsx`: pending answer indicator.
- `frontend/src/types/index.ts`: TypeScript API and UI types.
- `frontend/src/index.css`: Tailwind base styles and utility CSS.
- `frontend/package.json`: frontend dependencies and commands.
- `frontend/vite.config.ts`: Vite dev server config.
- `frontend/tailwind.config.js`: Tailwind content paths and theme extensions.
- `frontend/nginx.conf` and `frontend/Dockerfile`: production static hosting.

## 4. How Everything Is Connected

Application startup:

1. `backend/app/main.py` calls `get_settings()` from `backend/app/config/settings.py`.
2. During FastAPI lifespan, `build_app_services(settings)` in `backend/app/services/factory.py` creates the upload directory, ChromaDB directory, SQLAlchemy engine, tables, session factory, embedding service, retriever, document service, PDF service, chat memory, chat service, and RAG pipeline.
3. These services are stored on `app.state`.
4. Route handlers read them from `request.app.state` or through dependency helpers in `backend/app/api/deps.py`.

Upload data flow:

```text
UploadZone.tsx
  -> useDocuments.upload()
  -> api/client.ts uploadDocument()
  -> POST /api/v1/upload
  -> validate_pdf_upload()
  -> SHA-256 hash deduplication
  -> save file in UPLOAD_DIR
  -> DocumentService.create_document()
  -> process_document_task.delay()
  -> Redis queue
  -> Celery worker
  -> RAGPipeline.process_document()
  -> PDFService.extract_pages()
  -> Chunker.chunk_pages()
  -> Retriever.add_chunks()
  -> EmbeddingService.embed_texts()
  -> ChromaDB upsert
  -> Document status ready
```

Chat data flow:

```text
ChatWindow.tsx
  -> useChat.sendMessage()
  -> api/client.ts sendChatStream()
  -> POST /api/v1/chat/stream
  -> ChatService.answer_stream()
  -> Retriever.search()
  -> EmbeddingService.embed_query()
  -> ChromaDB query
  -> MMR rerank
  -> build_prompt()
  -> Gemini via LangChain
  -> optional verifier prompt
  -> SSE token/final events
  -> frontend updates pending assistant message
  -> ChatMessage rows persisted
```

Configuration is loaded by `Settings` in `backend/app/config/settings.py`. Important env vars include `GEMINI_API_KEY`, `MODEL_NAME`, `EMBEDDING_MODEL`, `CHUNK_SIZE`, `CHUNK_OVERLAP`, `TOP_K`, `NO_ANSWER_THRESHOLD`, `UPLOAD_DIR`, `CHROMA_PERSIST_DIR`, `DATABASE_URL`, `REDIS_URL`, and Celery URLs.

External services and stores:

- Gemini: used by `ChatService._load_llm()` through `langchain_google_genai.ChatGoogleGenerativeAI`.
- Sentence Transformers: local embedding model in `EmbeddingService`.
- ChromaDB: persistent vector database in `Retriever`.
- Redis: Celery broker/result backend and worker health check.
- SQLite: default relational metadata store through SQLAlchemy. The code can accept other SQLAlchemy URLs, but Docker currently sets SQLite.

## 5. Core Concepts

FastAPI routes are thin. They validate input, call services, and shape responses. Most business logic belongs in services or RAG modules, not route handlers.

SQLAlchemy models in `backend/app/models/db.py` define persistent tables:

- `Document`: uploaded file metadata and processing status.
- `ChatSession`: chat session metadata.
- `ChatMessage`: persisted user and assistant messages.
- `Feedback`: thumbs-up/down feedback.

RAG means retrieval-augmented generation. In this app:

1. Documents are split into chunks.
2. Chunks are embedded into vectors.
3. A user question is embedded into a vector.
4. ChromaDB finds similar chunks.
5. The selected chunks become the prompt context.
6. Gemini answers using only that context.

Chunking matters because LLMs and vector search work better with smaller pieces than whole PDFs. `Chunker` uses approximate word tokens, `CHUNK_SIZE`, and `CHUNK_OVERLAP`.

Embeddings are numeric representations of text meaning. `EmbeddingService` uses `sentence-transformers/all-MiniLM-L6-v2` by default and normalizes embeddings.

Vector retrieval happens in `Retriever.search()`. It asks ChromaDB for more candidates than needed, then applies MMR reranking to balance relevance and diversity. It can filter by selected document IDs.

Confidence is based on ChromaDB cosine distance in `ChatService._compute_confidence()`. If the best distance is above `NO_ANSWER_THRESHOLD`, the app refuses to answer without calling Gemini.

Grounding is enforced mainly by prompt rules in `backend/app/rag/prompt.py`, retrieval confidence checks, and optional verifier behavior in `ChatService._verify_answer()`.

Streaming chat uses server-sent events. The backend emits `trace`, `token`, optional `replace`, `final`, and `error` events. The frontend parses them in `frontend/src/api/client.ts`.

Celery is used so upload requests return quickly while heavy PDF extraction and embedding work happen in the background. The worker command in `docker-compose.yml` uses `--concurrency=1` to reduce SQLite and ChromaDB write contention.

## 6. Development Workflow

Docker setup from the repository root:

```bash
cp .env.example .env
# edit .env and set GEMINI_API_KEY
docker compose up --build
```

Useful URLs:

- Frontend: `http://localhost:5173`
- Backend root: `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/api/v1/health`
- Worker health: `http://localhost:8000/api/v1/health/worker`

Stop the stack:

```bash
docker compose down
```

Reset local Docker volumes:

```bash
docker compose down -v
```

Backend local setup:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend local setup:

```bash
cd frontend
npm install
VITE_API_BASE_URL=http://localhost:8000/api/v1 npm run dev
```

Run a worker locally if you are not using Docker:

```bash
cd backend
celery -A app.tasks.celery_app.celery_app worker --loglevel=INFO --concurrency=1 --prefetch-multiplier=1
```

For local non-Docker development, Redis must be reachable at the configured `REDIS_URL`. The default `.env.example` points to `redis://redis:6379/0`, which works inside Docker Compose. On the host machine, use something like:

```env
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

Common debugging commands:

```bash
docker compose logs backend
docker compose logs worker
docker compose logs redis
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/health/worker
```

Common issues:

- Upload is stuck: check `docker compose logs worker` and `/api/v1/health/worker`.
- Chat says Gemini is not configured: set `GEMINI_API_KEY`.
- Frontend cannot reach backend: check `VITE_API_BASE_URL` and CORS origins.
- Duplicate upload is not processed: this is expected if SHA-256 hash matches an existing non-failed document.
- Scanned/image-only PDFs fail: `PDFService` requires extractable text and does not perform OCR.

## 7. Testing Guide

The backend uses pytest. Configuration is in `backend/pyproject.toml` under `[tool.pytest.ini_options]`.

Tests live in `backend/tests/`:

- `conftest.py`: creates test settings and a FastAPI `TestClient`.
- `test_routes.py`: checks root, health, empty documents list, and feedback.
- `test_upload_queue.py`: checks upload queueing and duplicate upload behavior.
- `test_document_tasks.py`: checks Celery task edge cases such as missing documents, ready documents, and missing files.

Run backend tests:

```bash
cd backend
pytest
```

Run one test file:

```bash
cd backend
pytest tests/test_upload_queue.py
```

Run one test:

```bash
cd backend
pytest tests/test_document_tasks.py::test_document_task_marks_missing_file_failed
```

Frontend currently has no test script in `frontend/package.json`. It has `dev`, `build`, and `preview`, but no unit or e2e testing setup.

How to write a new backend test:

1. Put it in `backend/tests/test_<area>.py`.
2. Use the `client` fixture for API tests.
3. Use `monkeypatch` to replace expensive services, Celery queueing, Gemini calls, ChromaDB calls, or file-system behavior when the unit under test does not need the real dependency.
4. Assert response status codes and meaningful fields, not every response detail.

Current coverage strengths:

- Basic API route smoke tests.
- Upload queueing and duplicate detection.
- Celery task control flow.

Coverage gaps:

- `ChatService` retrieval, refusal, verifier, persistence, and streaming behavior.
- `Retriever` MMR reranking and document filter behavior.
- `RAGPipeline` status transitions and error paths.
- Frontend hooks and UI behavior.
- End-to-end upload-to-chat flow.
- RAG evaluation is script-based, not a pytest suite.

## 8. Important Code Paths

### Flow 1: Upload And Index A PDF

1. User picks or drops a PDF in `frontend/src/components/UploadZone.tsx`.
2. `UploadZone` validates that the file looks like a PDF and calls `onUpload`.
3. `frontend/src/pages/App.tsx` maps `onUpload` to `documents.upload`.
4. `frontend/src/hooks/useDocuments.ts` calls `uploadDocument()` and tracks upload progress.
5. `frontend/src/api/client.ts` sends `POST /api/v1/upload` with `XMLHttpRequest` so progress events work.
6. `backend/app/api/routes/upload.py` validates size/type using `validate_pdf_upload()`.
7. The route computes a SHA-256 file hash and checks `DocumentService.get_by_hash()`.
8. If it is a duplicate and the previous document has not failed, the route returns `deduplicated: true`.
9. Otherwise it saves the file under `UPLOAD_DIR`, creates a `Document` row, and queues `process_document_task.delay()`.
10. `backend/app/tasks/document_tasks.py` runs in the Celery worker.
11. The task builds services with `include_chat=False`, skips missing/ready documents, and calls `RAGPipeline.process_document()`.
12. `backend/app/rag/pipeline.py` updates status through `extracting_text`, `chunking`, `embedding`, `indexing`, and `ready`.
13. `PDFService.extract_pages()` extracts text with PyMuPDF.
14. `Chunker.chunk_pages()` creates overlapping chunks.
15. `Retriever.add_chunks()` embeds and upserts chunks into ChromaDB with metadata.
16. `useDocuments` polls while documents are in in-progress statuses, so the UI updates when status becomes `ready` or `failed`.

### Flow 2: Ask A Grounded Question

1. User submits a question in `frontend/src/components/ChatWindow.tsx`.
2. `frontend/src/pages/App.tsx` calls `chat.sendMessage(question, selectedDocumentIds)`.
3. `frontend/src/hooks/useChat.ts` adds a user message and a pending assistant message.
4. `frontend/src/api/client.ts` sends `POST /api/v1/chat/stream`.
5. `backend/app/api/routes/chat.py` calls `ChatService.answer_stream()`.
6. `ChatService._retrieve()` calls `Retriever.search()`.
7. `Retriever.search()` embeds the question, queries ChromaDB, applies selected document filters, and reranks with MMR.
8. `ChatService` converts matches to citations and computes confidence from distances.
9. If confidence is `not_found`, it refuses without a Gemini call.
10. Otherwise it renders chat history from `SessionMemoryStore`, formats context, and builds a prompt with `build_prompt()`.
11. Gemini streams answer chunks through LangChain.
12. If verifier settings require it, `ChatService._verify_answer()` may replace the answer with the standard no-answer response.
13. The backend emits SSE events.
14. The frontend appends `token` text to the pending message, handles `replace`, stores trace/confidence from `trace`, and uses `final` to attach citations and metadata.
15. `ChatService._persist_messages()` stores user and assistant messages in SQLite.

## 9. Configuration And Environment

Main configuration files:

- `.env.example`: sample runtime settings.
- `backend/app/config/settings.py`: authoritative backend settings schema.
- `docker-compose.yml`: container-time overrides for paths and service URLs.
- `backend/pyproject.toml`: ruff, mypy, and pytest config.
- `frontend/package.json`: frontend npm scripts and dependencies.
- `frontend/vite.config.ts`: local Vite server config.
- `frontend/tailwind.config.js`: Tailwind scanning and theme extensions.
- `frontend/nginx.conf`: static frontend fallback routing.
- `backend/alembic.ini` and `backend/alembic/`: migration configuration.

Important environment variables:

- `GEMINI_API_KEY`: required for generated answers.
- `MODEL_NAME`: Gemini model name, default `gemini-2.5-flash`.
- `EMBEDDING_MODEL`: Sentence Transformers model.
- `CHUNK_SIZE` and `CHUNK_OVERLAP`: ingestion chunking behavior.
- `TOP_K`: default retrieval count.
- `NO_ANSWER_THRESHOLD`: distance threshold for refusing weak matches.
- `SESSION_MEMORY_K`: chat memory window size.
- `CHAT_CONTEXT_TOP_K`: max chunks passed into chat context.
- `CHAT_CONTEXT_CHUNK_CHARS`: max characters per retrieved chunk in prompt context.
- `CHAT_SYNC_FOLLOWUPS`: whether normal chat calls generate follow-up questions.
- `CHAT_LLM_VERIFIER_MIN_CONFIDENCE`: controls when verifier runs.
- `WARM_EMBEDDING_MODEL_ON_STARTUP`: loads embedding model during startup when true.
- `MAX_FILE_MB`: upload size limit.
- `UPLOAD_DIR`: uploaded file directory.
- `CHROMA_PERSIST_DIR`: ChromaDB persistence directory.
- `DATABASE_URL`: SQLAlchemy DB URL.
- `REDIS_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`: Redis/Celery connectivity.
- `CELERY_TASK_ALWAYS_EAGER`: useful for tests or synchronous task behavior.
- `CORS_ORIGINS`: allowed frontend origins.
- `RATE_LIMIT_CHAT`: SlowAPI limit for chat routes.

Build, lint, format, and test:

- Backend tests: `cd backend && pytest`
- Backend lint config exists for ruff in `backend/pyproject.toml`, but `ruff` is not listed in `backend/requirements.txt`.
- Backend type config exists for mypy, but `mypy` is not listed in `backend/requirements.txt`.
- Frontend build: `cd frontend && npm run build`
- Frontend has no configured test, lint, or format script.

## 10. Common Tasks For A Junior Developer

Add a new backend endpoint:

1. Add request/response models in `backend/app/models/requests.py` or `backend/app/models/responses.py`.
2. Add a route function in the right file under `backend/app/api/routes/`, or create a new route module.
3. Keep route logic thin; put business logic in `backend/app/services/`.
4. Include the router in `backend/app/main.py` if it is a new module.
5. Add tests in `backend/tests/`.

Update upload behavior:

1. Start with `backend/app/api/routes/upload.py`.
2. For validation changes, check `backend/app/utils/validators.py`.
3. For processing changes, update `backend/app/rag/pipeline.py`, `backend/app/services/pdf_service.py`, `backend/app/rag/chunker.py`, or `backend/app/rag/retriever.py`.
4. Add tests around queueing, task behavior, or pipeline behavior.

Update chat behavior:

1. Start with `backend/app/services/chat_service.py`.
2. Prompt wording lives in `backend/app/rag/prompt.py`.
3. Retrieval behavior lives in `backend/app/rag/retriever.py`.
4. Response schema lives in `backend/app/models/responses.py`.
5. Frontend rendering lives in `frontend/src/components/MessageBubble.tsx`, `CitationCard.tsx`, and `ConfidenceBadge.tsx`.

Update UI behavior:

1. Start in `frontend/src/pages/App.tsx` to see the state wiring.
2. Use `frontend/src/hooks/useDocuments.ts` for document state.
3. Use `frontend/src/hooks/useChat.ts` for chat state.
4. Use `frontend/src/api/client.ts` if the backend API contract changes.
5. Keep shared TypeScript shapes in `frontend/src/types/index.ts`.

Add tests:

- For route behavior, use the `client` fixture.
- For Celery task behavior, call `process_document_task.run()` as existing tests do.
- For expensive RAG behavior, mock embeddings, ChromaDB, and Gemini unless you are writing an explicit integration test.

Safely refactor:

- Preserve API response shapes unless you also update `frontend/src/types/index.ts` and affected components.
- Preserve document status strings unless you update backend responses and frontend status lists/config.
- Preserve the no-answer phrase if tests, evaluations, or users rely on it.
- Make one behavior change at a time and add a focused test.

Trace where behavior is implemented:

- Find backend endpoint: search route path under `backend/app/api/routes`.
- Find UI API call: search endpoint path in `frontend/src/api/client.ts`.
- Find document status behavior: search for status strings like `extracting_text` or `ready`.
- Find chat output behavior: search for response fields such as `confidence`, `evidence_status`, or `trace_id`.

## 11. Risks, Gotchas, And Conventions

Project conventions:

- Backend route files are thin and service methods hold business logic.
- Shared services are stored on `app.state` during FastAPI lifespan.
- Pydantic models define API contracts.
- SQLAlchemy models define persistence.
- Document processing statuses are explicit strings: `uploaded`, `extracting_text`, `chunking`, `embedding`, `indexing`, `ready`, `failed`.
- Logs use JSON formatting through `backend/app/utils/logger.py`.
- Chat requests include a `trace_id` for debugging.

Error-handling patterns:

- `backend/app/main.py` has a global exception handler returning a generic 500 plus trace ID.
- Upload queue failures mark the document as `failed` and return HTTP 503.
- PDF extraction raises `ValueError` for invalid, protected, empty, or no-text PDFs.
- Celery retries unexpected errors but treats `FileNotFoundError` and `ValueError` as non-retryable.
- Chat persistence failures are logged as warnings and do not fail the user response.
- Feedback failures return HTTP 500.

Security concerns:

- Uploaded document text is untrusted. The prompt explicitly says not to follow instructions inside documents.
- Real `GEMINI_API_KEY` values belong in `.env`, not source control.
- File names are sanitized with `Path(file.filename).name`, but uploads still write to local storage.
- Only PDFs are accepted, but MIME checks are not a full content-security boundary.
- CORS is configurable through `CORS_ORIGINS`.
- Chat has rate limiting through SlowAPI.

Performance concerns:

- The embedding model is loaded lazily and can be warmed on startup.
- PDF processing and embeddings are CPU-heavy, so they run in Celery.
- Docker worker concurrency is `1` to avoid SQLite and ChromaDB write contention.
- ChromaDB queries fetch extra candidates and rerank, capped at 50 candidates.
- Large chunk sizes increase prompt size and latency.
- `CHAT_CONTEXT_CHUNK_CHARS` limits prompt context per chunk.

Gotchas:

- README mentions SQLite and ChromaDB, which matches Docker, but Alembic exists and the DB layer can use any SQLAlchemy URL.
- `.env.example` uses Docker Redis host `redis`; for host-local development use `localhost`.
- The frontend defaults `VITE_API_BASE_URL` to `http://localhost:8000/api/v1`.
- Streaming chat falls back to normal chat only when the HTTP response is not OK or has no body.
- `MessageBubble` sends feedback using the frontend-generated message ID, while backend persistence generates separate `ChatMessage` IDs. That means feedback is recorded, but not necessarily linked to the persisted assistant row ID.
- Scanned PDFs are not supported because there is no OCR path.
- Tests may initialize real app lifespan services, so expensive model loading can surprise you if fixtures are not patched.

## 12. Suggested 1-Week Learning Path

Day 1: Run the app and map the surface area.

- Read `README.md`, `.env.example`, and `docker-compose.yml`.
- Start the stack with `docker compose up --build`.
- Upload a small text-based PDF.
- Watch document statuses in the UI and worker logs.
- Visit `/docs`, `/api/v1/health`, and `/api/v1/health/worker`.

Day 2: Learn backend startup and routing.

- Read `backend/app/main.py`, `backend/app/config/settings.py`, and `backend/app/services/factory.py`.
- Follow one API route from request model to response model.
- Starter task: add a harmless field to the health response, such as a config-derived boolean, with a test.

Day 3: Learn document ingestion.

- Read `backend/app/api/routes/upload.py`, `backend/app/tasks/document_tasks.py`, `backend/app/rag/pipeline.py`, `backend/app/services/pdf_service.py`, and `backend/app/rag/chunker.py`.
- Starter task: improve or test a PDF validation error message.

Day 4: Learn retrieval and chat.

- Read `backend/app/rag/retriever.py`, `backend/app/services/chat_service.py`, and `backend/app/rag/prompt.py`.
- Ask questions with and without selected documents.
- Starter task: add a test for confidence/refusal behavior with a fake retriever.

Day 5: Learn the frontend state flow.

- Read `frontend/src/pages/App.tsx`, `frontend/src/hooks/useDocuments.ts`, `frontend/src/hooks/useChat.ts`, and `frontend/src/api/client.ts`.
- Starter task: display a clearer failed-document error by fetching document detail or exposing `error_msg` in the list response.

Day 6: Learn quality and evaluation.

- Read `scripts/run_rag_eval.py` and `evals/golden_dataset.json`.
- Run the evaluator against a local backend after uploading documents that match the dataset.
- Starter task: add a project-specific golden question.

Day 7: Make a small end-to-end change.

- Pick a narrow feature such as adding a document status tooltip, exposing chunk count in a new place, or adding an API test for document deletion.
- Update backend/frontend contracts carefully if needed.
- Run backend tests and frontend build.
- Write a short note in docs or README about what you learned.

## 13. Missing Documentation And Recommended Improvements

Missing or thin documentation:

- No architecture diagram in the README.
- No explicit local Redis instructions for non-Docker backend/worker development.
- No dedicated API contract documentation beyond Swagger.
- No document status lifecycle docs except a comment in `backend/app/rag/pipeline.py`.
- No frontend architecture docs.
- No testing strategy docs.
- No RAG quality tuning guide for `TOP_K`, `NO_ANSWER_THRESHOLD`, MMR settings, chunk size, and context limits.
- No OCR/scanned-PDF limitation note in the main README troubleshooting section.
- No explanation of feedback linkage and current limitations.

Recommended README/docs additions:

- Add a "How the RAG pipeline works" diagram.
- Add a "Local development without Docker, including Redis and worker" section.
- Add a "Document processing statuses" table.
- Add a "Configuration reference" table generated from `Settings`.
- Add a "Testing and evaluation" section with `pytest`, frontend build, and `scripts/run_rag_eval.py`.
- Add examples of upload and chat API requests with `curl`.
- Add a note that scanned PDFs need OCR before this app can answer from them.
- Add frontend documentation showing how `App.tsx`, hooks, API client, and components fit together.

## Quick Reference

Most useful commands:

```bash
cp .env.example .env
docker compose up --build
docker compose logs worker
docker compose down
docker compose down -v

cd backend && pytest
cd frontend && npm install && npm run build
python scripts/run_rag_eval.py --backend-url http://localhost:8000/api/v1
```

Most important files:

```text
backend/app/main.py
backend/app/services/factory.py
backend/app/api/routes/upload.py
backend/app/tasks/document_tasks.py
backend/app/rag/pipeline.py
backend/app/rag/retriever.py
backend/app/services/chat_service.py
backend/app/rag/prompt.py
frontend/src/pages/App.tsx
frontend/src/api/client.ts
frontend/src/hooks/useDocuments.ts
frontend/src/hooks/useChat.ts
```
