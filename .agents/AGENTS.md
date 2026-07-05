# Enterprise RAG Assistant - Agent Context & Guidelines

This workspace contains a full-stack RAG (Retrieval-Augmented Generation) application. This document serves as an optimization guide and project summary for agents to understand the repository structure, database schema, configuration, and developer guidelines quickly, saving reasoning and input/output tokens.

---

## 🏗️ Repository Structure

```
├── .agents/
│   └── AGENTS.md                 # This file (Agent Context & Guidelines)
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── api/routes/           # API endpoints (chat, documents, feedback, health, upload)
│       ├── config/settings.py    # Configuration schema (Pydantic Settings)
│       ├── core/                 # Rate limiting, shared tools
│       ├── models/db.py          # SQLAlchemy models (Document, ChatSession, ChatMessage, Feedback)
│       ├── rag/                  # RAG pipeline, chunker, prompt template, vector retriever (ChromaDB)
│       ├── services/             # Core business logic (chat, document DB, embedding, PDF extraction)
│       ├── utils/                # Logging setup
│       └── main.py               # FastAPI entry point, lifespan hooks
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   ├── tailwind.config.js
│   └── src/
│       ├── api/                  # API client code
│       ├── components/           # UI components (ChatWindow, Sidebar, UploadZone, MessageBubble, etc.)
│       ├── hooks/                # Custom React hooks (e.g. useChat, useDocuments)
│       ├── pages/App.tsx         # Main layout entry point
│       └── types/                # TypeScript interface definitions
├── docker-compose.yml            # Local development orchestration
└── README.md                     # General setup & onboarding instructions
```

---

## 🗄️ Database & Vector Schema

### SQLite Database (app.db) - [backend/app/models/db.py](file:///Users/jeet/Documents/Enterprice%20RAG%20Assistent/backend/app/models/db.py)
* **`documents`**: Tracks PDF uploads and processing status.
  * Columns: `id` (PK, UUID), `filename`, `file_path`, `file_hash`, `page_count`, `chunk_count`, `status` (uploaded, processing, completed, failed), `error_msg`, `file_size`, `uploaded_at`, `updated_at`.
* **`chat_sessions`**: Session metadata tracking.
  * Columns: `id` (PK, UUID), `document_ids` (JSON string list), `created_at`, `updated_at`.
* **`chat_messages`**: Chat history and citation references.
  * Columns: `id` (PK, UUID), `session_id`, `role` (`user` | `assistant`), `content`, `citations` (JSON list of page numbers and document names), `confidence` (`high`|`medium`|`low`|`not_found`), `trace_id`, `latency_ms`, `created_at`.
* **`feedback`**: Simple user rating table.
  * Columns: `id` (PK, UUID), `message_id`, `session_id`, `rating` (`good` | `bad`), `reason`, `created_at`.

### Vector Database (ChromaDB)
* **Persist Dir**: `./backend/chroma_db` (or custom configured via `CHROMA_PERSIST_DIR`)
* **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2` (Local via HuggingFace SentenceTransformers)
* **Metadata stored with chunks**: `document_id`, `page_number`, `text`

---

## ⚙️ Configuration & Environment Variables

All configurations are managed in [backend/app/config/settings.py](file:///Users/jeet/Documents/Enterprice%20RAG%20Assistent/backend/app/config/settings.py) via Pydantic:

| Variable | Default Value | Description |
|---|---|---|
| `GEMINI_API_KEY` | `""` | Gemini client API Key |
| `MODEL_NAME` | `gemini-2.5-flash` | Gemini model for generating responses |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | SentenceTransformer model path/ID |
| `CHUNK_SIZE` | `1000` | Size of chunks for PDF splitting (characters) |
| `CHUNK_OVERLAP` | `150` | Overlap size for PDF splitting (characters) |
| `TOP_K` | `5` | Number of document chunks to retrieve |
| `NO_ANSWER_THRESHOLD` | `0.55` | Max cosine distance threshold (refuses answer if distance exceeded) |
| `MAX_FILE_MB` | `50` | Maximum file upload size limit |
| `SESSION_MEMORY_K` | `10` | Number of recent messages to preserve in chat memory context |

---

## 🔄 Core Architectural Pipelines

### 1. Document Upload & Processing Pipeline
1. **Upload**: PDF uploaded via `POST /api/v1/upload`.
2. **Database entry**: Document is created in the DB with status `uploaded`.
3. **Background processing**: Handled via asynchronous process or background tasks:
   * **PDF Parsing**: `PDFService` extracts pages and text using PyMuPDF.
   * **Chunking**: `chunker.py` splits text by `CHUNK_SIZE` and `CHUNK_OVERLAP`.
   * **Vectorization & Storage**: Chunks embedded via `EmbeddingService` and written into ChromaDB by `Retriever`.
   * **Update DB**: Sets status to `completed` and stores chunk & page counts.

### 2. Chat & RAG Query Pipeline
1. **Request**: Incoming query and `session_id` via `POST /api/v1/chat`.
2. **Retrieve Context**: `Retriever` fetches top `TOP_K` document chunks from ChromaDB. Filtered based on cosine distance threshold (`NO_ANSWER_THRESHOLD`).
3. **Assemble Prompt**: Context chunks, chat session history (up to `SESSION_MEMORY_K`), and prompt instructions are formatted.
4. **LLM Generation**: Sent to Gemini model (`gemini-2.5-flash`).
5. **Citations & Confidence**: Response references are parsed to form structured citations containing document metadata, and confidence scores are calculated.
6. **Save to DB**: Saves user prompt and assistant response with latency/citations/confidence.

---

## 🛠️ Developer Commands & Scripts

### Run Full Stack with Docker
```bash
# Start backend, frontend, nginx, and setup database
docker compose up --build

# Run database/upload/vector volume resets
docker compose down -v
```

### Local Dev Run (Without Docker)
* **Backend**:
  ```bash
  cd backend
  python -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
  ```
* **Frontend**:
  ```bash
  cd frontend
  npm install
  npm run dev
  ```
