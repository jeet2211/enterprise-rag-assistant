# Redis, Celery, Streaming, And Latency Changes

This document explains the implementation changes made to the Enterprise RAG Assistant around background processing,
Docker runtime behavior, Redis/Celery, answer quality, streaming responses, and query latency. It is intentionally
detailed so a future engineer can understand the current behavior at the function and code-path level.

## Executive Summary

The app originally processed uploaded PDFs with FastAPI `BackgroundTasks` inside the API process. Chat responses were
returned only after the backend completed retrieval, answer generation, follow-up generation, verification, and database
persistence. This created two important problems:

- Document processing was coupled to the web server process.
- Chat latency was high because several model calls ran sequentially before the UI received anything.

The updated system now uses:

- Redis as the Celery broker/result backend.
- A separate Celery worker container for PDF processing.
- A Docker entrypoint that repairs named-volume permissions before dropping to a non-root user.
- A streaming chat endpoint for token-by-token UI updates.
- Per-trace latency instrumentation.
- Gated answer verification and disabled synchronous follow-up generation by default.
- Smaller prompt context for lower model latency.
- Startup embedding warmup.

Measured query-time improvement for an already-indexed `Agentic-Design-Patterns (1).pdf` question:

- Before: roughly `15430ms` to `23587ms`.
- After: roughly `7163ms` backend latency.
- Timing breakdown from trace `5343baa2-6d41-4ff9-977c-abe3c9da639c`:
  - `retrieval_ms`: `67.6`
  - `prompt_ms`: `0.0`
  - `llm_answer_ms`: `6808.3`
  - `persist_ms`: `21.5`

This proves the dominant remaining latency is the main Gemini generation call, not Chroma, SQLite, Redis, or retrieval.

## Configuration Changes

### `backend/app/config/settings.py`

New background-processing settings:

- `redis_url`
  - Env alias: `REDIS_URL`
  - Default: `redis://redis:6379/0`
  - Used by Redis health checks and as the fallback broker/backend URL for Celery.

- `celery_broker_url`
  - Env alias: `CELERY_BROKER_URL`
  - Default: `None`
  - If unset, `resolved_celery_broker_url` returns `redis_url`.

- `celery_result_backend`
  - Env alias: `CELERY_RESULT_BACKEND`
  - Default: `None`
  - If unset, `resolved_celery_result_backend` returns `redis_url`.

- `celery_task_always_eager`
  - Env alias: `CELERY_TASK_ALWAYS_EAGER`
  - Default: `False`
  - Intended for tests/local fallback where tasks should run synchronously.

New chat latency settings:

- `chat_context_top_k`
  - Env alias: `CHAT_CONTEXT_TOP_K`
  - Default: `5`
  - Hard cap for how many retrieved chunks are passed into the LLM prompt.

- `chat_context_chunk_chars`
  - Env alias: `CHAT_CONTEXT_CHUNK_CHARS`
  - Default: `1200`
  - Max character count per retrieved chunk in the prompt context.

- `chat_sync_followups`
  - Env alias: `CHAT_SYNC_FOLLOWUPS`
  - Default: `False`
  - When `False`, follow-up questions are not generated during the blocking chat request.

- `chat_llm_verifier_min_confidence`
  - Env alias: `CHAT_LLM_VERIFIER_MIN_CONFIDENCE`
  - Default: `low`
  - Controls when the expensive LLM verifier runs. With `low`, verifier runs only for `low` or `not_found` style cases.

- `warm_embedding_model_on_startup`
  - Env alias: `WARM_EMBEDDING_MODEL_ON_STARTUP`
  - Default: `True`
  - Preloads the sentence-transformer model during API startup.

### `.env.example`

The example env file now documents all Redis/Celery and latency-related settings so local Docker runs have clear defaults.

## Docker And Runtime Changes

### `docker-compose.yml`

Added a `redis` service:

- Image: `redis:7.4-alpine`
- Command: `redis-server --appendonly yes`
- Port: `6379:6379`
- Volume: `redis_data:/data`
- Health check: `redis-cli ping`

Updated the `backend` service:

- Depends on healthy Redis.
- Exposes Redis/Celery environment variables.
- Uses the same named volumes for uploads, Chroma, and SQLite.
- Uses `cap_add: CHOWN` so the entrypoint can repair volume ownership.

Added a `worker` service:

- Uses the same backend image.
- Command:

```yaml
celery -A app.tasks.celery_app.celery_app worker --loglevel=INFO --concurrency=1 --prefetch-multiplier=1
```

- Shares the same volumes:
  - `backend_uploads`
  - `backend_chroma`
  - `backend_sqlite`
- Starts with `--concurrency=1` to reduce SQLite and Chroma write contention.

### `backend/Dockerfile`

Added `gosu`:

- Used by the entrypoint to start as root briefly, repair volume permissions, then run the actual app as `appuser`.

Added:

```dockerfile
ENV ANONYMIZED_TELEMETRY=False
```

This is intended to reduce Chroma telemetry noise on future image builds.

Removed final `USER appuser` and replaced it with:

```dockerfile
ENTRYPOINT ["/app/backend/docker-entrypoint.sh"]
```

The process still runs as `appuser`; the privilege drop now happens inside the entrypoint after volume ownership repair.

### `backend/docker-entrypoint.sh`

Responsibilities:

1. Ensure runtime directories exist:

```sh
mkdir -p /app/backend/uploads /app/backend/chroma_db /app/backend/data
```

2. Repair ownership of mounted Docker named volumes:

```sh
chown -R appuser:appgroup /app/backend/uploads /app/backend/chroma_db /app/backend/data
```

3. Drop privileges and run the requested command:

```sh
exec gosu appuser "$@"
```

This fixed the SQLite error:

```text
sqlite3.OperationalError: attempt to write a readonly database
```

The root cause was that Docker named volumes are mounted over image-created directories. Even though the Dockerfile
`chown`s those directories at build time, the mounted volume can still be root-owned at runtime.

## Service Factory

### `backend/app/services/factory.py`

This module centralizes backend service construction so both the API process and the Celery worker build dependencies
the same way.

#### `AppServices`

Dataclass bundling:

- `engine`
- `session_factory`
- `embedding_service`
- `retriever`
- `document_service`
- `pdf_service`
- `memory_store`
- `chat_service`
- `pipeline`

#### `migrate_sqlite_schema(engine)`

Backfills old SQLite volumes with missing columns/indexes.

Current backfills:

- Adds `documents.file_hash` if missing.
- Adds `documents.chunk_count` if missing.
- Creates `ix_documents_file_hash`.

This logic used to live in `main.py`; moving it into the factory lets the worker perform the same DB initialization.

#### `build_app_services(settings, include_chat=True)`

Builds all runtime services:

1. Creates upload and Chroma directories.
2. Builds SQLAlchemy engine.
3. Creates DB tables.
4. Runs SQLite backfills.
5. Builds DB session factory.
6. Creates:
   - `EmbeddingService`
   - `Retriever`
   - `DocumentService`
   - `PDFService`
   - `SessionMemoryStore`
   - `ChatService`, unless `include_chat=False`
   - `RAGPipeline`

The Celery worker calls this with `include_chat=False` because document processing does not need chat memory or LLM chat.

## Celery Task Queue

### `backend/app/tasks/celery_app.py`

Defines the shared Celery app:

```python
celery_app = Celery(
    "enterprise_rag_assistant",
    broker=settings.resolved_celery_broker_url,
    backend=settings.resolved_celery_result_backend,
    include=["app.tasks.document_tasks"],
)
```

Important Celery settings:

- `task_always_eager`
  - Controlled by `CELERY_TASK_ALWAYS_EAGER`.

- `task_acks_late=True`
  - Worker acknowledges after task execution, not before.

- `task_reject_on_worker_lost=True`
  - If worker dies mid-task, the broker can redeliver.

- `worker_prefetch_multiplier=1`
  - Prevents one worker from reserving many PDF jobs.

- `broker_connection_retry_on_startup=True`
  - Preserves retry-on-startup behavior for Celery 6 compatibility.

- JSON serializers only:
  - `task_serializer="json"`
  - `accept_content=["json"]`
  - `result_serializer="json"`

### `backend/app/tasks/document_tasks.py`

#### `_is_non_retryable(exc)`

Returns `True` for errors that should not be retried:

- `FileNotFoundError`
- `ValueError`

Rationale:

- Missing files, invalid PDFs, password-protected PDFs, empty PDFs, and no-text PDFs are not transient.
- Retrying them wastes worker time.

#### `process_document_task(self, document_id, file_path, filename)`

Celery task name: `documents.process`

Flow:

1. Load settings and configure logging.
2. Build worker services with `build_app_services(settings, include_chat=False)`.
3. Look up the document row.
4. Skip if document is missing:

```python
return {"status": "skipped", "reason": "missing_document"}
```

5. Skip if document is already `ready`:

```python
return {"status": "skipped", "reason": "already_ready"}
```

6. If the PDF file is missing:
   - mark document `failed`
   - set `error_msg="Uploaded file is missing."`
   - return a failed result without retry

7. Run:

```python
services.pipeline.process_document(document_id, file_path, filename)
```

8. If an exception is non-retryable, return failed without retry.
9. Otherwise call:

```python
raise self.retry(exc=exc)
```

10. On success:

```python
return {"status": "ready", "document_id": document_id}
```

## Upload Route Changes

### `backend/app/api/routes/upload.py`

FastAPI `BackgroundTasks` was removed.

#### `_compute_hash(file)`

Still computes SHA-256 by streaming file chunks.

Used for deduplication.

#### `_save_upload(file, destination)`

Still writes upload to disk in 1 MB chunks.

#### `upload_document(request, file)`

New behavior:

1. Validate uploaded PDF.
2. Compute SHA-256 hash.
3. Check for existing document by hash.
4. If existing document exists and is not `failed`, return it without queueing duplicate work.

This improves deduplication from only skipping `ready` files to also skipping:

- `uploaded`
- `extracting_text`
- `chunking`
- `embedding`
- `indexing`

5. Save file to uploads volume.
6. Create DB row with status `uploaded`.
7. Enqueue Celery task:

```python
process_document_task.delay(document_id, str(destination), original_name)
```

8. If enqueue fails:
   - mark document `failed`
   - return HTTP `503`

The route still returns HTTP `202 Accepted`.

## RAG Pipeline Changes

### `backend/app/rag/pipeline.py`

#### `_ensure_document_exists(document_id)`

Returns whether the document row still exists.

Used to avoid continuing processing after a user deletes a document while the worker is mid-task.

#### `process_document(document_id, file_path, filename)`

Still performs:

1. `extracting_text`
2. `chunking`
3. `embedding`
4. `indexing`
5. `ready`

New behavior:

- Calls `_ensure_document_exists()` before and after major stages.
- If the document has been deleted, returns early.
- Restored the contract with `Chunker.chunk_pages()` by passing:

```python
(page.page_number, page.text, page.section_title)
```

- Restored `section_title` into chunk payloads passed to Chroma metadata.
- On exception, marks failed only if the document still exists.

This prevents a delete/worker race from recreating or updating deleted document state.

## SQLite Test Support

### `backend/app/models/db.py`

#### `build_engine(db_url)`

For in-memory SQLite URLs:

```python
sqlite:///:memory:
sqlite://
```

the engine now uses `StaticPool`.

Why:

- Without `StaticPool`, each new DB connection can see a different empty in-memory database.
- Tests that create tables on one connection and query on another can fail unpredictably.

## Health Checks

### `backend/app/models/responses.py`

Added:

```python
class WorkerHealthResponse(BaseModel):
    status: str
    redis: str
    celery: str
    worker_count: int = 0
```

### `backend/app/api/routes/health.py`

#### `health(request)`

Existing endpoint remains backward-compatible:

```text
GET /api/v1/health
```

Still reports:

- app status
- Chroma health
- Gemini configured/degraded status
- document counts
- total chunks

#### `worker_health(request)`

New endpoint:

```text
GET /api/v1/health/worker
```

Checks:

1. Redis:

```python
Redis.from_url(settings.redis_url).ping()
```

2. Celery workers:

```python
celery_app.control.inspect(timeout=1).ping()
```

Returns:

- `healthy` only if Redis responds and at least one Celery worker responds.
- `degraded` otherwise.

Important operational note:

- During testing, Redis and worker exited with code `137`, likely due to Docker resource pressure.
- Restarting with `docker compose up -d redis worker` restored worker health.

## Prompt And Answer Quality Changes

### `backend/app/rag/prompt.py`

The system prompt now instructs the LLM to:

- Answer the user's actual intent directly.
- Avoid merely restating retrieved chunks.
- For broad design questions, start with a recommendation.
- Then provide 3-6 concrete bullets or numbered steps.
- Cite each substantive claim inline.
- State when support is partial.

This addressed an observed answer-quality problem where the app produced a citation-heavy but shallow paragraph for:

```text
what is best way to create agents
```

## Chat Service Latency Changes

### `backend/app/services/chat_service.py`

This file received the most important query-time changes.

#### `SessionMemoryStore`

Unchanged conceptually:

- In-memory sliding window.
- Stores `(role, content)` pairs per `session_id`.
- Used only for current API process lifetime.

#### `_compute_confidence(distances, no_answer_threshold)`

Unchanged behavior:

- No distances -> `not_found`
- Best distance over threshold -> `not_found`
- `< 0.20` -> `high`
- `< 0.38` -> `medium`
- Otherwise `low`

#### `_should_run_verifier(confidence, min_confidence)`

New deterministic gate for the expensive LLM verifier.

Confidence order:

```python
{"not_found": 0, "low": 1, "medium": 2, "high": 3}
```

If `chat_llm_verifier_min_confidence="low"`, verifier runs only for:

- `not_found`
- `low`

It does not run for:

- `medium`
- `high`

This removes one full LLM call from most successful answers.

#### `_route_question(question)`

Expanded routing for broad design/strategy questions.

Now routes to `explanation` if the question includes terms such as:

- `architecture`
- `best`
- `build`
- `create`
- `design`
- `implement`
- `pattern`
- `plan`
- `strategy`

This makes broad questions retrieve with the explanation-oriented retrieval settings.

#### `_trim_text(text, limit)`

New helper that trims chunk text before it is inserted into the LLM prompt.

Behavior:

- If text length is under limit, returns unchanged.
- If over limit, truncates near the last space before the limit and appends `...`.

Purpose:

- Reduce prompt size.
- Reduce Gemini input latency.
- Avoid feeding huge chunks when only part of the chunk is needed.

#### `_format_context(matches)`

Changed from static method to instance method so it can read settings.

Now applies:

```python
self._trim_text(str(match["text"]), self.settings.chat_context_chunk_chars)
```

Each context item is still formatted like:

```text
[DocumentName p.PageNumber] Section: ... | chunk text
```

#### `_build_citations(matches)`

New helper to isolate citation construction.

Builds `Citation` objects from retrieved matches:

- `document_name`
- `page_number`
- `chunk_preview`
- `token_count`
- `doc_id`
- `distance`
- `section_title`

This removes duplicated citation code between non-streaming and streaming answer paths.

#### `_record_timing(timings, name, start)`

New helper for stage-level latency logging.

Stores elapsed milliseconds:

```python
timings[name] = round((time.perf_counter() - start) * 1000, 1)
```

#### `_retrieve(question, top_k, document_ids, timings)`

New shared retrieval helper for both `/chat` and `/chat/stream`.

Responsibilities:

1. Determine `requested_top_k`.
2. Cap it with:

```python
self.settings.chat_context_top_k
```

3. Route the question via `_route_question`.
4. Select retrieval knobs:
   - parameter questions:
     - higher candidate multiplier
     - lower MMR lambda
   - explanation questions:
     - candidate multiplier at least `4`
     - MMR lambda no more than `0.65`
   - general questions:
     - default settings

5. Call `self.retriever.search(...)`.
6. Record `retrieval_ms`.
7. Build citations.
8. Compute confidence.

Returns:

```python
(matches, citations, confidence)
```

#### `answer(...)`

Existing non-streaming chat path remains compatible with the old API response.

Major changes:

1. Uses `_retrieve(...)`.
2. Records timings for:
   - `retrieval_ms`
   - `prompt_ms`
   - `llm_answer_ms`
   - `followups_ms`, only if enabled
   - `verifier_ms`, only if gated on
   - `persist_ms`

3. Does not generate follow-up questions unless:

```python
self.settings.chat_sync_followups
```

is true.

4. Runs LLM verifier only when:

```python
_should_run_verifier(confidence, self.settings.chat_llm_verifier_min_confidence)
```

5. If verifier is skipped:

```python
evidence_status = "exact" if confidence == "high" else "partial"
```

6. Logs two structured messages:

```json
{"event":"chat_request", ...}
{"event":"chat_timing", "timings": {...}}
```

#### `answer_stream(...)`

New streaming answer generator used by `/api/v1/chat/stream`.

Flow:

1. Generate a `trace_id`.
2. Run `_retrieve(...)`.
3. Yield initial trace event:

```python
{"event": "trace", "data": {"trace_id": trace_id, "confidence": confidence}}
```

4. If confidence is `not_found`, stream the refusal text.
5. Otherwise:
   - build prompt
   - load LLM
   - call `llm.stream(prompt)`
   - yield each token/chunk as:

```python
{"event": "token", "data": {"text": text}}
```

6. If streaming fails before any token is sent, fallback to `llm.invoke(prompt)`.
7. If verifier runs and rejects the streamed answer, yield:

```python
{"event": "replace", "data": {"text": "I could not find this information in the uploaded documents."}}
```

8. Persist the final answer.
9. Log `chat_request` and `chat_timing`.
10. Yield final metadata:

```python
{
  "event": "final",
  "data": {
    "answer": answer_text,
    "citations": [...],
    "session_id": session_id,
    "sources_used": len(citations),
    "confidence": confidence,
    "evidence_status": evidence_status,
    "answer_style": answer_style,
    "trace_id": trace_id,
    "follow_up_questions": [],
    "latency_ms": latency_ms
  }
}
```

This improves perceived latency because the browser can display text before the full metadata response is ready.

## Chat API Changes

### `backend/app/api/routes/chat.py`

#### `chat(request, payload, chat_service)`

Existing route:

```text
POST /api/v1/chat
```

Still returns `ChatResponse`.

Uses `chat_service.answer(...)`.

#### `_sse(event, data)`

New helper that formats Server-Sent Event blocks:

```text
event: token
data: {"text": "..."}
```

#### `chat_stream(request, payload, chat_service)`

New route:

```text
POST /api/v1/chat/stream
```

Returns:

```python
StreamingResponse(events(), media_type="text/event-stream")
```

The route converts `chat_service.answer_stream(...)` generator items into SSE events.

If an exception escapes the generator, it sends an SSE `error` event:

```json
{"detail": "..."}
```

## Startup Warmup

### `backend/app/main.py`

During FastAPI lifespan startup:

```python
if settings.warm_embedding_model_on_startup:
    services.embedding_service.embed_query("warmup")
    services.retriever.healthcheck()
```

Purpose:

- Load sentence-transformer model before the first user query.
- Touch Chroma collection before first request.
- Move cold-start cost from first chat request to app startup.

Tradeoff:

- Backend startup becomes slower.
- First query after startup becomes faster.

## Frontend Streaming Changes

### `frontend/src/api/client.ts`

#### `sendChat(payload)`

Unchanged fallback function.

Still calls:

```text
POST /api/v1/chat
```

#### `ChatStreamHandlers`

New callback interface:

```ts
interface ChatStreamHandlers {
  onToken: (text: string) => void
  onReplace?: (text: string) => void
  onTrace?: (data: Partial<ChatResponse>) => void
}
```

#### `parseSseBlock(block)`

Parses a single SSE block into:

```ts
{ event: string; data: unknown }
```

Supported SSE fields:

- `event:`
- `data:`

The function JSON-parses joined `data:` lines.

#### `sendChatStream(payload, handlers)`

New streaming client.

Flow:

1. Calls:

```text
POST /api/v1/chat/stream
```

with:

```http
Accept: text/event-stream
```

2. If response is not OK or has no body, falls back to `sendChat(payload)`.
3. Reads `response.body.getReader()`.
4. Decodes chunks using `TextDecoder`.
5. Splits stream into SSE blocks by `\n\n`.
6. Handles events:
   - `token`: calls `handlers.onToken(text)`
   - `replace`: calls `handlers.onReplace(text)`
   - `trace`: calls `handlers.onTrace(data)`
   - `final`: saves final `ChatResponse`
   - `error`: throws an error

7. If stream ends without `final`, throws:

```text
Streaming chat ended without a final response
```

### `frontend/src/hooks/useChat.ts`

#### `sendMessage(question, documentIds)`

Changed from:

```ts
const response = await sendChat(...)
```

to:

```ts
const response = await sendChatStream(..., handlers)
```

Streaming handlers:

- `onToken`
  - Appends token text to the pending assistant message.

- `onReplace`
  - Replaces the pending assistant content, used if backend verifier rejects after streaming.

- `onTrace`
  - Sets early metadata such as `trace_id` and `confidence`.

After the stream completes, the hook replaces the pending message with the final response:

- final answer text
- citations
- confidence
- evidence status
- answer style
- trace ID
- follow-up questions
- latency
- `isPending=false`

This preserves the existing UI model while making the content appear earlier.

## Retriever Behavior

### `backend/app/rag/retriever.py`

No major structural changes were made here during the latency work.

Important current behavior:

- Embeds the user query with `EmbeddingService.embed_query`.
- Queries Chroma with optional metadata filter:

```python
where={"doc_id": {"$eq": document_ids[0]}}
```

or:

```python
where={"doc_id": {"$in": document_ids}}
```

- Fetches more candidates than final `top_k`.
- Applies MMR reranking in `_mmr_rerank`.

Latency observation:

- For the tested query, retrieval took only about `67.6ms`.
- Retrieval is not the current bottleneck.

## Embedding Service Behavior

### `backend/app/services/embedding_service.py`

No structural change during latency work, but startup warmup now calls it.

Important functions:

- `_load()`
  - Lazily loads `SentenceTransformer`.
  - Protected by a thread lock.

- `embed_texts(texts)`
  - Encodes normalized embeddings.
  - Returns `float32` lists.

- `embed_query(text)`
  - Embeds a single query using `embed_texts([text])[0]`.

Cold-start impact:

- First call loads the transformer model.
- Startup warmup moves that cost to application startup.

## Tests Added Or Updated

### `backend/tests/test_upload_queue.py`

#### `test_upload_enqueues_document_processing_task`

Verifies:

- Upload returns `202`.
- Document starts as `uploaded`.
- Celery `.delay(...)` is called once.
- Enqueued args include document ID and filename.

#### `test_duplicate_processing_upload_is_not_queued_twice`

Verifies:

- Same file uploaded twice returns deduplicated response.
- Second upload does not enqueue another Celery job.

### `backend/tests/test_document_tasks.py`

#### `test_document_task_skips_missing_document`

Verifies task exits cleanly when DB row is gone.

#### `test_document_task_skips_ready_document`

Verifies duplicate task for already-ready document does not reprocess.

#### `test_document_task_processes_existing_document`

Verifies existing uploaded document calls pipeline.

#### `test_document_task_marks_missing_file_failed`

Verifies missing PDF file marks document failed and does not call pipeline.

### `backend/tests/conftest.py`

Updated to make app tests use test settings during lifespan startup.

### `backend/tests/test_routes.py`

Adjusted feedback endpoint expectations to match actual `201 Created` response.

## Operational Commands

### Start stack

```bash
cd "/Users/jeet/Documents/Enterprice RAG Assistent"
docker compose up -d
```

### Rebuild frontend after frontend code changes

```bash
docker compose build frontend
docker compose up -d --no-deps frontend
```

### Rebuild backend after backend source changes

```bash
docker compose build backend
docker compose up -d backend worker
```

Note: backend rebuild is slow because the ML dependencies are heavy.

### Check API health

```bash
curl -fsS http://localhost:8000/api/v1/health
```

### Check Redis/Celery worker health

```bash
curl -fsS http://localhost:8000/api/v1/health/worker
```

### Restart Redis and worker if they exited

```bash
docker compose up -d redis worker
```

### Inspect Redis

```bash
docker compose exec redis redis-cli
```

Useful commands inside Redis:

```redis
PING
KEYS *
DBSIZE
LLEN celery
MONITOR
```

### Inspect SQLite contents

```bash
docker compose exec -T backend python - <<'PY'
from app.config.settings import get_settings
from app.models.db import build_engine
from sqlalchemy import text

engine = build_engine(get_settings().db_url)

with engine.connect() as conn:
    for table in ["documents", "chat_sessions", "chat_messages", "feedback"]:
        print(f"\n--- {table} ---")
        rows = conn.execute(text(f"SELECT * FROM {table} LIMIT 20")).mappings().all()
        for row in rows:
            print(dict(row))
PY
```

### Inspect Chroma chunks

```bash
docker compose exec -T backend python - <<'PY'
from app.config.settings import get_settings
from app.services.embedding_service import EmbeddingService
from app.rag.retriever import Retriever

settings = get_settings()
retriever = Retriever(settings.chroma_persist_dir, EmbeddingService(settings.embedding_model))

sample = retriever.collection.peek(limit=5)
for i, doc in enumerate(sample.get("documents", []), start=1):
    print(f"\n--- Chunk {i} ---")
    print(doc[:1000])
    print("metadata:", sample.get("metadatas", [])[i - 1])
PY
```

## Verification Performed

Backend syntax:

```bash
python -m compileall app tests
```

Frontend build:

```bash
npm run build
```

Docker Compose validation:

```bash
docker compose config --quiet
```

SQLite write probe:

```text
sqlite write ok
```

Worker health:

```json
{"status":"healthy","redis":"healthy","celery":"healthy","worker_count":1}
```

Streaming smoke test result:

```json
{
  "first_token_ms": 6044.5,
  "total_client_ms": 7197.4,
  "backend_latency_ms": 7163.3,
  "chars": 1769,
  "sources": 5
}
```

Trace timing:

```json
{
  "llm_answer_ms": 6808.3,
  "persist_ms": 21.5,
  "prompt_ms": 0.0,
  "retrieval_ms": 67.6
}
```

## Known Remaining Issues And Follow-Ups

### Main Gemini call is still the bottleneck

After removing extra synchronous LLM calls, the dominant cost is now `llm_answer_ms`.

Possible future improvements:

- Use a faster Gemini model for chat.
- Reduce max output length.
- Add answer caching for repeated questions.
- Add semantic query cache keyed by document IDs and normalized question.
- Improve prompt compactness further.

### Chroma telemetry log noise

Logs still showed:

```text
Failed to send telemetry event ... capture() takes 1 positional argument but 3 were given
```

The Dockerfile and Compose env now include `ANONYMIZED_TELEMETRY=False`, but a full backend image rebuild may be needed
for the Dockerfile-level env to apply everywhere. Compose-level env applies on container recreation.

### Redis and worker exited with code `137`

Observed once during local testing.

Likely cause:

- Docker resource pressure, especially with backend, worker, sentence-transformers, Chroma, and frontend running together.

Mitigations:

- Increase Docker Desktop memory.
- Keep worker concurrency at `1`.
- Consider Postgres and external vector DB for heavier workloads.

### SQLite is still not ideal for multi-process production

The API and worker both write to SQLite.

Current mitigations:

- Worker concurrency is `1`.
- SQLite volume permissions are repaired at startup.

Recommended next production step:

- Move to Postgres.

### Follow-up questions are currently empty in streaming mode

By design, synchronous follow-up generation is disabled to reduce latency.

Future options:

- Generate follow-ups asynchronously.
- Add a separate `/chat/{trace_id}/followups` endpoint.
- Store follow-ups later and let the UI update when available.

## High-Level Request Flow After Changes

### Upload flow

```text
Browser
  -> POST /api/v1/upload
  -> API validates + saves file + creates document row
  -> API enqueues Celery task in Redis
  -> Worker consumes task
  -> Worker runs RAGPipeline
  -> Worker updates SQLite + Chroma
```

### Streaming chat flow

```text
Browser
  -> POST /api/v1/chat/stream
  -> API retrieves Chroma chunks
  -> API builds trimmed prompt context
  -> API streams Gemini chunks as SSE token events
  -> Browser appends tokens to pending assistant message
  -> API persists final answer
  -> API sends final SSE metadata event
  -> Browser attaches citations/confidence/latency
```

