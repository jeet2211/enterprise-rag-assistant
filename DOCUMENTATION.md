# Enterprise RAG Assistant — Complete Documentation

> **Last Updated:** June 2026
>
> This document is the single, authoritative reference for the Enterprise RAG Assistant project. It is written for beginners — every concept is explained from first principles. If you are an experienced developer, feel free to skip to the sections you need using the Table of Contents.

---

## Table of Contents

- [1. Project Overview](#1-project-overview)
  - [1.1 What Is This Project?](#11-what-is-this-project)
  - [1.2 What Is RAG? (Explained Simply)](#12-what-is-rag-explained-simply)
  - [1.3 What Problem Does It Solve?](#13-what-problem-does-it-solve)
  - [1.4 Technology Stack](#14-technology-stack)
- [2. Core Concepts for Beginners](#2-core-concepts-for-beginners)
  - [2.1 API & REST API](#21-api--rest-api)
  - [2.2 HTTP Methods](#22-http-methods)
  - [2.3 JSON](#23-json)
  - [2.4 Pydantic](#24-pydantic)
  - [2.5 SQLAlchemy & ORM](#25-sqlalchemy--orm)
  - [2.6 Vector Database](#26-vector-database)
  - [2.7 Embeddings](#27-embeddings)
  - [2.8 Cosine Similarity](#28-cosine-similarity)
  - [2.9 Large Language Model (LLM)](#29-large-language-model-llm)
  - [2.10 Retrieval-Augmented Generation (RAG)](#210-retrieval-augmented-generation-rag)
  - [2.11 Chunking](#211-chunking)
  - [2.12 Tokens](#212-tokens)
  - [2.13 Middleware](#213-middleware)
  - [2.14 Dependency Injection](#214-dependency-injection)
  - [2.15 Docker & Docker Compose](#215-docker--docker-compose)
  - [2.16 Docker Volumes](#216-docker-volumes)
  - [2.17 React](#217-react)
  - [2.18 Hooks](#218-hooks)
  - [2.19 Components & Props](#219-components--props)
  - [2.20 State](#220-state)
  - [2.21 TypeScript](#221-typescript)
  - [2.22 Tailwind CSS](#222-tailwind-css)
  - [2.23 Vite](#223-vite)
- [3. Architecture Overview](#3-architecture-overview)
  - [3.1 High-Level Architecture Diagram](#31-high-level-architecture-diagram)
  - [3.2 Backend Structure](#32-backend-structure)
  - [3.3 Frontend Structure](#33-frontend-structure)
  - [3.4 How Frontend and Backend Communicate](#34-how-frontend-and-backend-communicate)
  - [3.5 Persistence Layer](#35-persistence-layer)
- [4. System Data Flow](#4-system-data-flow)
  - [4.1 Document Upload Flow](#41-document-upload-flow)
  - [4.2 Document Processing Flow](#42-document-processing-flow)
  - [4.3 Chat Query Flow](#43-chat-query-flow)
  - [4.4 Document Deletion Flow](#44-document-deletion-flow)
- [5. The RAG Pipeline — End to End](#5-the-rag-pipeline--end-to-end)
  - [5.1 Upload & Validation](#51-upload--validation)
  - [5.2 File Storage](#52-file-storage)
  - [5.3 PDF Parsing](#53-pdf-parsing)
  - [5.4 Text Chunking](#54-text-chunking)
  - [5.5 Embedding Generation](#55-embedding-generation)
  - [5.6 Vector Storage (Indexing)](#56-vector-storage-indexing)
  - [5.7 Retrieval (Semantic Search)](#57-retrieval-semantic-search)
  - [5.8 Prompt Construction](#58-prompt-construction)
  - [5.9 Answer Generation (LLM Call)](#59-answer-generation-llm-call)
  - [5.10 Citation Generation & Deduplication](#510-citation-generation--deduplication)
  - [5.11 Document Deletion & Cleanup](#511-document-deletion--cleanup)
  - [5.12 Fallback Behavior](#512-fallback-behavior)
- [6. Module-by-Module Explanation](#6-module-by-module-explanation)
  - [6.1 API Layer](#61-api-layer)
  - [6.2 Configuration](#62-configuration)
  - [6.3 Database Layer](#63-database-layer)
  - [6.4 RAG Engine](#64-rag-engine)
  - [6.5 Services](#65-services)
  - [6.6 Utilities](#66-utilities)
  - [6.7 Frontend API Client](#67-frontend-api-client)
  - [6.8 Frontend Hooks](#68-frontend-hooks)
  - [6.9 Frontend Components](#69-frontend-components)
  - [6.10 Frontend Types](#610-frontend-types)
- [7. File-by-File Documentation](#7-file-by-file-documentation)
  - [7.1 Root Configuration Files](#71-root-configuration-files)
  - [7.2 Backend Files](#72-backend-files)
  - [7.3 Frontend Files](#73-frontend-files)
- [8. Frontend Deep Dive](#8-frontend-deep-dive)
  - [8.1 Application State Flow](#81-application-state-flow)
  - [8.2 API Calls](#82-api-calls)
  - [8.3 Hooks and Responsibilities](#83-hooks-and-responsibilities)
  - [8.4 Component Tree](#84-component-tree)
  - [8.5 Upload Workflow](#85-upload-workflow)
  - [8.6 Chat Workflow](#86-chat-workflow)
  - [8.7 Document Management Workflow](#87-document-management-workflow)
  - [8.8 How UI State Maps to Backend State](#88-how-ui-state-maps-to-backend-state)
- [9. Backend Deep Dive](#9-backend-deep-dive)
  - [9.1 Application Startup (Lifespan)](#91-application-startup-lifespan)
  - [9.2 Configuration System](#92-configuration-system)
  - [9.3 Database Model](#93-database-model)
  - [9.4 API Routes](#94-api-routes)
  - [9.5 Services Layer](#95-services-layer)
  - [9.6 Rate Limiting](#96-rate-limiting)
  - [9.7 Structured Logging](#97-structured-logging)
  - [9.8 Request / Response Schemas](#98-request--response-schemas)
- [10. Feature Deep Dives](#10-feature-deep-dives)
  - [10.1 Document Upload & Background Processing](#101-document-upload--background-processing)
  - [10.2 PDF Text Extraction](#102-pdf-text-extraction)
  - [10.3 Text Chunking](#103-text-chunking)
  - [10.4 Vector Embedding & Storage](#104-vector-embedding--storage)
  - [10.5 Semantic Search & Retrieval](#105-semantic-search--retrieval)
  - [10.6 Prompt Engineering](#106-prompt-engineering)
  - [10.7 LLM Integration](#107-llm-integration)
  - [10.8 Citation Generation & Deduplication](#108-citation-generation--deduplication)
  - [10.9 Conversational Memory](#109-conversational-memory)
  - [10.10 Rate Limiting](#1010-rate-limiting)
  - [10.11 Health Monitoring](#1011-health-monitoring)
  - [10.12 Error Handling](#1012-error-handling)
  - [10.13 Drag-and-Drop Upload UI](#1013-drag-and-drop-upload-ui)
  - [10.14 Real-time Processing Status Polling](#1014-real-time-processing-status-polling)
- [11. Test Suite Explanation](#11-test-suite-explanation)
  - [11.1 conftest.py — Shared Test Infrastructure](#111-conftestpy--shared-test-infrastructure)
  - [11.2 test_chat_service.py](#112-test_chat_servicepy)
  - [11.3 test_chunker.py](#113-test_chunkerpy)
  - [11.4 test_deps_and_logger.py](#114-test_deps_and_loggerpy)
  - [11.5 test_document_service.py](#115-test_document_servicepy)
  - [11.6 test_embedding_service.py](#116-test_embedding_servicepy)
  - [11.7 test_main.py](#117-test_mainpy)
  - [11.8 test_pdf_service.py](#118-test_pdf_servicepy)
  - [11.9 test_pipeline.py](#119-test_pipelinepy)
  - [11.10 test_retriever.py](#1110-test_retrieverpy)
  - [11.11 test_routes.py](#1111-test_routespy)
  - [11.12 test_settings.py](#1112-test_settingspy)
  - [11.13 test_validators.py](#1113-test_validatorspy)
  - [11.14 Frontend Tests](#1114-frontend-tests)
- [12. Deployment Guide](#12-deployment-guide)
  - [12.1 Prerequisites](#121-prerequisites)
  - [12.2 Environment Variables](#122-environment-variables)
  - [12.3 Running with Docker Compose](#123-running-with-docker-compose)
  - [12.4 Running Locally (Without Docker)](#124-running-locally-without-docker)
  - [12.5 Production Considerations](#125-production-considerations)
- [13. Extension Guide](#13-extension-guide)
  - [13.1 Swap the Embedding Model](#131-swap-the-embedding-model)
  - [13.2 Add Authentication](#132-add-authentication)
  - [13.3 Add New Document Types](#133-add-new-document-types)
  - [13.4 Add Streaming Responses](#134-add-streaming-responses)
  - [13.5 Switch to PostgreSQL](#135-switch-to-postgresql)
  - [13.6 Add a Reranker](#136-add-a-reranker)
  - [13.7 Add Hybrid Search](#137-add-hybrid-search)
- [14. Troubleshooting Guide](#14-troubleshooting-guide)
  - [14.1 Pydantic Namespace Conflict](#141-pydantic-namespace-conflict)
  - [14.2 SlowAPI Decorator Issues](#142-slowapi-decorator-issues)
  - [14.3 ChromaDB Connection Issues](#143-chromadb-connection-issues)
  - [14.4 Model Loading Issues](#144-model-loading-issues)
  - [14.5 Common Docker Issues](#145-common-docker-issues)
  - [14.6 Frontend Build Issues](#146-frontend-build-issues)
- [15. Future Improvement Ideas](#15-future-improvement-ideas)
- [16. Glossary](#16-glossary)

---

## 1. Project Overview

### 1.1 What Is This Project?

The **Enterprise RAG Assistant** is a full-stack web application that lets you:

1. **Upload PDF documents** (company reports, manuals, research papers — anything).
2. **Ask questions in natural language** about the content of those documents.
3. **Receive accurate answers with citations** pointing back to the exact pages and paragraphs the answer came from.

Think of it as "ChatGPT, but it only talks about *your* documents." No hallucinated facts from the internet — every answer is grounded in the material you uploaded.

The project consists of three layers:

| Layer | Technology | What It Does |
|-------|-----------|--------------|
| **Frontend** | React + TypeScript + Tailwind CSS | A chat-style web UI where you upload PDFs and ask questions |
| **Backend** | Python + FastAPI | An API server that handles uploads, processes documents, and generates answers |
| **Storage** | SQLite + ChromaDB + File System | Stores document metadata, vector embeddings, and raw PDF files |

### 1.2 What Is RAG? (Explained Simply)

**RAG** stands for **Retrieval-Augmented Generation**. Let us break that down with an analogy.

Imagine you are taking an open-book exam:

1. **The Exam Question** = the user's question ("What was our company's revenue in Q3?")
2. **Your Textbooks** = the uploaded PDF documents
3. **Finding the Right Pages** = *Retrieval* — you flip through your books to find the pages that are most relevant to the question
4. **Writing Your Answer** = *Generation* — you read those pages and write an answer in your own words, citing which pages you used

A **Large Language Model** (like Google's Gemini) is very good at step 4 — writing coherent answers. But on its own, it does not have access to your company's private documents. It would have to guess, and it might guess wrong (this is called a *hallucination*).

**RAG fixes this** by adding step 3 first. Before asking the LLM to answer, we *retrieve* the most relevant chunks of your documents and hand them to the LLM as context. Now the LLM has the actual facts right in front of it, and it can write an accurate answer.

Here is the analogy as a picture:

```
Without RAG:
  Student (LLM) gets question → Guesses the answer → Often wrong ❌

With RAG:
  Student (LLM) gets question → Opens textbook (Retrieval) → Reads relevant pages → Writes accurate answer ✅
```

### 1.3 What Problem Does It Solve?

| Problem | How RAG Solves It |
|---------|-------------------|
| LLMs don't know your private data | We feed your documents directly as context |
| LLMs hallucinate (make things up) | Answers are grounded in retrieved text |
| You can't search PDFs semantically | Vector search finds meaning, not just keywords |
| No traceability | Citations tell you exactly where the answer came from |
| Too many documents to read | The system reads them for you and finds the relevant parts |

### 1.4 Technology Stack

Here is every technology used, with an explanation of *why* it was chosen:

| Technology | Role | Why This Choice |
|-----------|------|-----------------|
| **Python 3.11** | Backend language | Most popular language for AI/ML; rich ecosystem of libraries |
| **FastAPI** | Backend web framework | Modern, fast, automatic API documentation, async support, type-safe |
| **Pydantic** | Data validation | Validates incoming request data and serializes responses; used natively by FastAPI |
| **SQLAlchemy** | Database ORM | Industry-standard Python ORM for SQL databases |
| **SQLite** | Relational database | Lightweight, serverless, zero-configuration; perfect for single-server deployments |
| **ChromaDB** | Vector database | Open-source, embeddable, purpose-built for storing and searching embeddings |
| **SentenceTransformers** | Embedding model | Converts text into numerical vectors for semantic search |
| **Google Gemini** | Large Language Model | Generates natural-language answers from retrieved context |
| **LangChain** | LLM integration | Provides a clean interface to call Gemini (and other LLMs) |
| **PyMuPDF (fitz)** | PDF parser | Fast, reliable PDF text extraction |
| **React 18** | Frontend UI library | Component-based, widely adopted, excellent developer tooling |
| **TypeScript** | Frontend language | Adds type safety to JavaScript, catches bugs at compile time |
| **Tailwind CSS** | CSS utility framework | Rapid UI styling without writing custom CSS files |
| **Vite** | Frontend build tool | Extremely fast development server and build tool |
| **Docker** | Containerization | Packages the app so it runs identically on any machine |
| **Docker Compose** | Multi-container orchestration | Starts backend + frontend + volumes with a single command |
| **SlowAPI** | Rate limiting | Protects the API from abuse by limiting request frequency |
| **aiofiles** | Async file I/O | Non-blocking file writes in the async FastAPI environment |
| **pytest** | Testing framework | The de-facto Python testing framework |

---

## 2. Core Concepts for Beginners

This section explains every technical concept you will encounter in the codebase. If you are already familiar with a concept, skip to the next one.

### 2.1 API & REST API

**API** stands for **Application Programming Interface**. It is a set of rules that says: "If you send me a message in *this* format, I will do *this* thing and send you back a response in *this* format."

Think of it like a restaurant menu:
- The **menu** is the API — it lists what you can order and what you will get back.
- The **waiter** is the API server — it takes your order and brings your food.
- **You** are the client (the frontend, or any other program that calls the API).

A **REST API** is a specific style of API that uses standard web addresses (URLs) and HTTP methods. In this project, the backend exposes a REST API with endpoints like:

| Endpoint | What It Does |
|----------|-------------|
| `GET /api/v1/health` | Check if the system is running |
| `POST /api/v1/upload` | Upload a PDF document |
| `POST /api/v1/chat` | Send a question and get an answer |
| `GET /api/v1/documents` | List all uploaded documents |
| `DELETE /api/v1/documents/{id}` | Delete a specific document |

### 2.2 HTTP Methods

HTTP (HyperText Transfer Protocol) is the language web browsers and servers speak. It defines several **methods** (also called verbs) that indicate what you want to do:

| Method | Meaning | Analogy |
|--------|---------|---------|
| **GET** | "Give me data" | Reading a book from the library |
| **POST** | "Here is new data; process it" | Handing in a homework assignment |
| **PUT** | "Replace this data with what I'm giving you" | Rewriting an entire chapter |
| **PATCH** | "Update part of this data" | Fixing a typo on one page |
| **DELETE** | "Remove this data" | Removing a book from the shelf |

This project uses **GET** (health, list/get documents), **POST** (upload, chat), and **DELETE** (remove document).

### 2.3 JSON

**JSON** (JavaScript Object Notation) is a text format for representing structured data. It looks like this:

```json
{
  "question": "What was the revenue?",
  "session_id": "abc-123-def",
  "top_k": 5
}
```

Key rules:
- Data is in **key-value pairs** (`"key": "value"`)
- Text values are in double quotes
- Numbers have no quotes
- Lists use square brackets: `[1, 2, 3]`
- Nested objects use curly braces: `{"a": {"b": 1}}`

The frontend and backend in this project communicate by sending JSON back and forth over HTTP.

### 2.4 Pydantic

**Pydantic** is a Python library that validates data. When someone sends a request to our API, we need to make sure the data is correct — for example, the `question` field must be a string between 1 and 4,000 characters.

Pydantic lets you define a **model** (a Python class) that describes what valid data looks like:

```python
class ChatRequest(BaseModel):
    question: str           # Must be a string
    session_id: str         # Must be a string
    top_k: Optional[int]    # Optional integer
```

If someone sends `{"question": 123}`, Pydantic will reject it because `123` is not a string. This prevents bugs and security issues.

Pydantic is also used for **response models** — ensuring the data the server sends back is always in the correct format.

### 2.5 SQLAlchemy & ORM

**SQLAlchemy** is a Python library for talking to databases. An **ORM** (Object-Relational Mapper) lets you interact with database tables using Python objects instead of writing raw SQL queries.

Without an ORM:
```sql
INSERT INTO documents (id, filename, status) VALUES ('abc', 'report.pdf', 'processing');
```

With SQLAlchemy ORM:
```python
doc = Document(id='abc', filename='report.pdf', status='processing')
session.add(doc)
session.commit()
```

Both do the same thing, but the ORM version is Python code — easier to write, test, and refactor.

In this project, SQLAlchemy manages a **SQLite** database that stores metadata about uploaded documents (filename, status, page count, timestamps).

### 2.6 Vector Database

A **vector database** is a special database designed to store and search **vectors** (lists of numbers). Regular databases are great at exact lookups ("find the row where `id = 5`"), but vector databases are great at **similarity lookups** ("find the rows that are *most similar* to this vector").

This project uses **ChromaDB** as its vector database. When you upload a PDF, each chunk of text is converted into a vector (a list of ~384 numbers) and stored in ChromaDB. When you ask a question, the question is also converted into a vector, and ChromaDB finds the chunks whose vectors are closest to the question's vector.

### 2.7 Embeddings

An **embedding** is a way to represent text (or images, audio, etc.) as a list of numbers — a **vector**. The key property is that **similar text produces similar vectors**.

Example:
- "The cat sat on the mat" → `[0.12, -0.34, 0.56, ...]` (384 numbers)
- "A kitten was sitting on the rug" → `[0.11, -0.33, 0.55, ...]` (very similar numbers!)
- "Stock prices rose sharply" → `[0.89, 0.12, -0.67, ...]` (very different numbers)

The model used in this project is `all-MiniLM-L6-v2` from the **SentenceTransformers** library. It produces 384-dimensional vectors. "384-dimensional" just means each piece of text is represented by a list of 384 numbers.

### 2.8 Cosine Similarity

**Cosine similarity** is a mathematical way to measure how similar two vectors are. It returns a value between -1 and 1:

| Value | Meaning |
|-------|---------|
| 1.0 | Identical direction (extremely similar) |
| 0.5 | Somewhat similar |
| 0.0 | Unrelated |
| -1.0 | Opposite meaning |

Imagine two arrows pointing from the center of a clock. If both point to 12, the angle between them is 0° and the cosine is 1 (identical). If one points to 12 and the other to 3, the angle is 90° and the cosine is 0 (unrelated).

ChromaDB uses cosine distance (which is `1 - cosine similarity`) to find the most similar chunks when you ask a question.

### 2.9 Large Language Model (LLM)

A **Large Language Model** is an AI model trained on massive amounts of text. Given a prompt (input text), it generates a continuation — a coherent, human-like response.

This project uses **Google Gemini** (`gemini-2.5-flash` by default). The LLM receives:
1. A system prompt ("You are an enterprise assistant…")
2. Conversation history (previous questions and answers)
3. Context (retrieved chunks from documents)
4. The user's question

And it returns a natural-language answer.

**Important:** The LLM is optional in this project. If no Gemini API key is configured, the system returns a fallback message explaining that no LLM is available. This makes the system usable for testing even without an API key.

### 2.10 Retrieval-Augmented Generation (RAG)

We covered this in [Section 1.2](#12-what-is-rag-explained-simply), but here is the formal definition:

**RAG** is a technique where:
1. **Retrieval**: Given a user query, relevant documents (or document chunks) are retrieved from a knowledge base.
2. **Augmented**: The retrieved text is added to the LLM's prompt as context.
3. **Generation**: The LLM generates an answer based on both the query and the retrieved context.

This gives the LLM access to information it was not trained on, and grounds its answers in factual source material.

### 2.11 Chunking

**Chunking** is the process of splitting a long document into smaller pieces called **chunks**.

Why not send the entire document to the LLM? Two reasons:
1. **LLMs have input limits** (called "context windows"). A 200-page PDF might exceed the limit.
2. **Retrieval works better with small chunks.** If you search for "Q3 revenue," you want to find the specific paragraph about Q3 revenue — not the entire 200-page document.

This project uses a **sliding window** chunking strategy:
- Each chunk is up to 1,000 characters (configurable via `chunk_size`).
- Consecutive chunks overlap by 200 characters (configurable via `chunk_overlap`).

The overlap ensures that if an important sentence spans the boundary between two chunks, it will appear in at least one of them.

### 2.12 Tokens

A **token** is the smallest unit of text that an LLM processes. Tokens are not the same as words:
- "Hello" = 1 token
- "unbelievable" = 3 tokens (un + believ + able)
- A space or punctuation mark can be its own token

LLMs have a maximum number of tokens they can process in one request (the "context window"). This is why chunking is important — we need to make sure the total prompt (system prompt + history + context + question) fits within the limit.

### 2.13 Middleware

**Middleware** is code that runs *between* receiving a request and sending a response. Think of it as a series of checkpoints at an airport:

```
Request → [CORS Check] → [Rate Limit Check] → [Your Route Handler] → [Response]
```

Each middleware can:
- Inspect or modify the request before it reaches your code
- Inspect or modify the response before it goes back to the client
- Reject the request entirely (e.g., rate limit exceeded)

This project uses two middlewares:
1. **CORS Middleware** — allows the frontend (on a different port) to call the backend API
2. **SlowAPI Middleware** — enforces rate limits on API endpoints

### 2.14 Dependency Injection

**Dependency Injection** (DI) is a design pattern where, instead of a function creating the objects it needs, those objects are *passed in* (injected) from the outside.

Without DI:
```python
def handle_chat():
    service = ChatService()  # Creates its own dependency
    return service.answer(question)
```

With DI (as used in this project):
```python
def handle_chat(chat_service = Depends(get_chat_service)):
    return chat_service.answer(question)  # Dependency is injected by FastAPI
```

Benefits:
- **Testability**: In tests, you can inject a fake/mock service instead of the real one.
- **Flexibility**: You can swap implementations without changing the route handler.
- **Single Responsibility**: Route handlers only handle HTTP logic; services handle business logic.

In this project, services are created once during app startup and stored on `app.state`. The `deps.py` file contains helper functions that extract these services from `app.state`, and FastAPI's `Depends()` mechanism injects them into route handlers.

### 2.15 Docker & Docker Compose

**Docker** is a tool that packages your application and all its dependencies into a **container** — a lightweight, isolated environment that runs the same way on any machine.

Think of it as a shipping container: your code, Python interpreter, libraries, and system tools are all packed together. Whether the container runs on your laptop, a colleague's laptop, or a cloud server, it behaves identically.

A **Dockerfile** is a recipe that tells Docker how to build the container:
1. Start from a base image (e.g., `python:3.11-slim`)
2. Copy files
3. Install dependencies
4. Set the command to run

**Docker Compose** orchestrates multiple containers. This project has two:
- A **backend** container (Python + FastAPI)
- A **frontend** container (Vite build served by nginx)

Docker Compose lets you start both with a single command: `docker-compose up`.

### 2.16 Docker Volumes

**Docker Volumes** are persistent storage for containers. Without volumes, any data a container writes is lost when the container stops (because containers are ephemeral by design).

This project uses three named volumes:
| Volume | Purpose |
|--------|---------|
| `backend_uploads` | Stores uploaded PDF files |
| `backend_chroma` | Stores ChromaDB vector embeddings |
| `backend_sqlite` | Stores the SQLite database file |

This means your uploaded documents and their embeddings survive container restarts.

### 2.17 React

**React** is a JavaScript library (created by Facebook) for building user interfaces. Instead of manipulating HTML directly, you describe what the UI should look like using **components**, and React efficiently updates the actual HTML when data changes.

Key ideas:
- **Declarative**: You say *what* to render, not *how* to update the DOM.
- **Component-based**: The UI is built from small, reusable pieces (components).
- **Virtual DOM**: React keeps a lightweight copy of the DOM in memory and only updates the parts that actually changed.

### 2.18 Hooks

**Hooks** are special functions in React (starting with `use`) that let you add features like state management and side effects to function components.

Common hooks used in this project:
| Hook | Purpose |
|------|---------|
| `useState` | Store and update a value (e.g., the list of messages) |
| `useEffect` | Run code when something changes (e.g., poll for document status) |
| `useCallback` | Memoize a function so it does not change on every render |
| `useRef` | Hold a reference to a DOM element or a mutable value |

This project also defines **custom hooks** (`useChat`, `useDocuments`) that encapsulate complex state logic and API calls.

### 2.19 Components & Props

A **component** is a reusable piece of UI. In this project, components are TypeScript functions that return JSX (HTML-like syntax):

```tsx
function MessageBubble({ message }) {
    return <div className="bubble">{message.text}</div>;
}
```

**Props** (short for "properties") are the inputs to a component — like function arguments. The parent component passes data down to child components through props:

```tsx
<MessageBubble message={myMessage} />
```

### 2.20 State

**State** is data that can change over time and causes the UI to re-render when it does. For example, the list of chat messages is state — when a new message arrives, the UI needs to update.

In React, state is managed using the `useState` hook:

```tsx
const [messages, setMessages] = useState([]);
// Later...
setMessages([...messages, newMessage]);  // This triggers a re-render
```

In this project, state is organized into two custom hooks:
- `useChat` manages: messages, sessionId, sending status, error
- `useDocuments` manages: documents, loading, uploading, uploadProgress, error

### 2.21 TypeScript

**TypeScript** is a superset of JavaScript that adds **static types**. This means you declare the type of each variable, function parameter, and return value:

```typescript
function add(a: number, b: number): number {
    return a + b;
}

add(1, "hello");  // ← TypeScript ERROR: "hello" is not a number
```

TypeScript catches bugs *before* you run the code (at compile time), which is especially valuable in large projects. In this project, types are defined in `types/index.ts` and used throughout the frontend.

### 2.22 Tailwind CSS

**Tailwind CSS** is a utility-first CSS framework. Instead of writing CSS classes with custom names and styles, you apply small, pre-built utility classes directly in your HTML:

```html
<!-- Traditional CSS -->
<div class="card">...</div>
<!-- card { padding: 16px; border-radius: 8px; background: white; } -->

<!-- Tailwind CSS -->
<div class="p-4 rounded-lg bg-white">...</div>
```

Each class does one thing: `p-4` = padding of 1rem, `rounded-lg` = border-radius of 0.5rem, `bg-white` = white background.

Benefits:
- No context-switching between HTML and CSS files
- Consistent spacing and color scales
- Easy responsive design with prefixes like `md:` and `lg:`
- Built-in dark mode support

### 2.23 Vite

**Vite** (French for "fast") is a modern build tool for web projects. It does two things:

1. **Development server**: Serves your files with instant hot-reload (changes appear in the browser without refreshing).
2. **Production build**: Bundles, minifies, and optimizes your code for deployment.

Vite is significantly faster than older tools like Webpack because it uses native ES modules and only processes the files you actually import.

---

## 3. Architecture Overview

### 3.1 High-Level Architecture Diagram

```mermaid
graph TB
    subgraph "User's Browser"
        FE["React Frontend<br/>(TypeScript + Tailwind)"]
    end

    subgraph "Backend Server"
        API["FastAPI Application"]
        subgraph "Services"
            CS["ChatService"]
            DS["DocumentService"]
            PS["PDFService"]
            ES["EmbeddingService"]
        end
        subgraph "RAG Engine"
            PL["RAGPipeline"]
            CH["Chunker"]
            RT["Retriever"]
            PR["PromptBuilder"]
        end
    end

    subgraph "Storage"
        SQL["SQLite<br/>(Document Metadata)"]
        CHROMA["ChromaDB<br/>(Vector Embeddings)"]
        FS["File System<br/>(PDF Files)"]
    end

    subgraph "External"
        GEMINI["Google Gemini API<br/>(LLM)"]
    end

    FE -->|"HTTP/JSON"| API
    API --> CS
    API --> DS
    API --> PL
    CS --> RT
    CS --> PR
    CS --> GEMINI
    PL --> PS
    PL --> CH
    PL --> ES
    PL --> RT
    PL --> DS
    RT --> ES
    RT --> CHROMA
    DS --> SQL
    PL --> FS
```

### 3.2 Backend Structure

The backend follows a **layered architecture**:

```
┌──────────────────────────────────┐
│          API Layer               │  ← HTTP routes (chat, upload, documents, health)
│     (app/api/routes/*.py)        │
├──────────────────────────────────┤
│        Service Layer             │  ← Business logic (ChatService, DocumentService, etc.)
│     (app/services/*.py)          │
├──────────────────────────────────┤
│         RAG Engine               │  ← Domain-specific logic (chunking, retrieval, prompts)
│      (app/rag/*.py)              │
├──────────────────────────────────┤
│         Data Layer               │  ← Database models, configuration
│   (app/models/*.py, config/)     │
├──────────────────────────────────┤
│       Infrastructure             │  ← Logging, validation, rate limiting
│   (app/utils/*.py, core/*.py)    │
└──────────────────────────────────┘
```

Data flows **downward**: routes call services, services call the RAG engine and data layer, the RAG engine calls storage. No layer reaches "up" — a service never directly handles HTTP, and the data layer never calls a service.

### 3.3 Frontend Structure

The frontend follows a **component hierarchy** pattern:

```
┌──────────────────────────────────┐
│          Pages (App.tsx)         │  ← Root layout and state wiring
├──────────────────────────────────┤
│       Components                 │  ← UI building blocks
│  (Sidebar, ChatWindow, etc.)     │
├──────────────────────────────────┤
│          Hooks                   │  ← State management and side effects
│   (useChat, useDocuments)        │
├──────────────────────────────────┤
│        API Client                │  ← HTTP communication with backend
│     (api/client.ts)              │
├──────────────────────────────────┤
│          Types                   │  ← TypeScript type definitions
│     (types/index.ts)             │
└──────────────────────────────────┘
```

### 3.4 How Frontend and Backend Communicate

The frontend and backend are completely separate applications that communicate over HTTP:

1. The frontend runs in the browser (port 5173 in development).
2. The backend runs as an API server (port 8000).
3. The frontend makes `fetch()` or `XMLHttpRequest` calls to the backend's API endpoints.
4. All communication uses JSON format.
5. **CORS** (Cross-Origin Resource Sharing) middleware on the backend allows these cross-origin requests.

```mermaid
sequenceDiagram
    participant Browser as React Frontend (port 5173)
    participant Server as FastAPI Backend (port 8000)

    Browser->>Server: POST /api/v1/upload (PDF file)
    Server-->>Browser: 202 Accepted {document_id, status}

    Browser->>Server: GET /api/v1/documents
    Server-->>Browser: 200 OK [{id, filename, status}, ...]

    Browser->>Server: POST /api/v1/chat {question, session_id}
    Server-->>Browser: 200 OK {answer, citations, session_id}
```

### 3.5 Persistence Layer

The project uses three types of storage:

| Storage | Technology | What It Stores | Location |
|---------|-----------|---------------|----------|
| **Relational DB** | SQLite | Document metadata (id, filename, status, page_count, timestamps) | `data/rag.db` |
| **Vector DB** | ChromaDB | Text chunk embeddings + metadata (document_id, page_number, text) | `chroma/` directory |
| **File System** | OS filesystem | Raw PDF files | `uploads/` directory |

**Why three stores?** Each is optimized for a different purpose:
- SQLite is great for structured queries ("list all documents sorted by date").
- ChromaDB is great for similarity search ("find chunks most similar to this question").
- The file system is the most efficient way to store large binary files (PDFs).

---

## 4. System Data Flow

This section shows exactly what happens during each major operation, step by step.

### 4.1 Document Upload Flow

```mermaid
sequenceDiagram
    participant User as User (Browser)
    participant FE as React Frontend
    participant API as FastAPI /upload
    participant Val as Validator
    participant FS as File System
    participant DB as SQLite
    participant BG as Background Task

    User->>FE: Drops PDF file onto UploadZone
    FE->>FE: Client-side validation (is it a PDF?)
    FE->>API: POST /api/v1/upload (multipart file)
    API->>Val: validate_pdf_upload(file, max_bytes)
    Val-->>API: Validation passes
    API->>API: Generate UUID for document_id
    API->>FS: Save file to uploads/{uuid}_{filename}
    API->>DB: Create Document record (status="processing")
    API->>BG: Schedule background processing task
    API-->>FE: 202 Accepted {document_id, filename, status="processing"}
    FE-->>User: Shows document in sidebar with "Processing" badge
```

Key points:
- The upload returns **immediately** with status 202 (Accepted). The actual processing (PDF parsing, chunking, embedding) happens in the background.
- The document status starts as `"processing"` and will change to `"ready"` or `"failed"` after background processing completes.

### 4.2 Document Processing Flow

```mermaid
sequenceDiagram
    participant BG as Background Task
    participant PDF as PDFService
    participant CK as Chunker
    participant EMB as EmbeddingService
    participant VDB as ChromaDB
    participant DB as SQLite

    BG->>PDF: extract_pages(file_path)
    PDF-->>BG: List of PageText (page_number + text)
    BG->>CK: chunk_pages(pages)
    CK-->>BG: List of Chunk (text + page + index)
    BG->>VDB: add_chunks(document_id, filename, chunks)
    VDB->>EMB: embed_texts([chunk.text for chunk in chunks])
    EMB-->>VDB: List of vectors (384 dimensions each)
    VDB->>VDB: Upsert chunks + embeddings + metadata
    BG->>DB: update_document(status="ready", page_count=N)

    Note over BG,DB: If any step fails:
    BG->>DB: update_document(status="failed", error_msg="...")
```

### 4.3 Chat Query Flow

```mermaid
sequenceDiagram
    participant User as User
    participant FE as Frontend
    participant API as POST /chat
    participant CS as ChatService
    participant RT as Retriever
    participant EMB as EmbeddingService
    participant VDB as ChromaDB
    participant MEM as SessionMemory
    participant LLM as Google Gemini

    User->>FE: Types question and clicks Send
    FE->>FE: Shows user message + loading dots
    FE->>API: POST /api/v1/chat {question, session_id, top_k}
    API->>CS: answer(question, session_id, top_k)
    CS->>RT: search(question, top_k)
    RT->>EMB: embed_query(question)
    EMB-->>RT: Question vector
    RT->>VDB: query(vector, n_results=top_k)
    VDB-->>RT: Matching chunks + metadata + distances
    RT-->>CS: Search results
    CS->>CS: Deduplicate citations by (doc_name, page)
    CS->>MEM: render(session_id) → conversation history
    CS->>CS: build_prompt(history, context, question)
    CS->>LLM: Generate answer from prompt
    LLM-->>CS: Answer text
    CS->>MEM: add_turn(session_id, question, answer)
    CS-->>API: {answer, citations}
    API-->>FE: ChatResponse {answer, citations, session_id}
    FE->>FE: Replace loading dots with answer + citations
    FE-->>User: Displays answer with expandable citation cards
```

### 4.4 Document Deletion Flow

```mermaid
sequenceDiagram
    participant User as User
    participant FE as Frontend
    participant API as DELETE /documents/{id}
    participant PL as RAGPipeline
    participant RT as Retriever
    participant VDB as ChromaDB
    participant FS as File System
    participant DB as SQLite

    User->>FE: Clicks delete button on document card
    FE->>API: DELETE /api/v1/documents/{document_id}
    API->>PL: delete_document(document_id, file_path)
    PL->>RT: delete_document(document_id)
    RT->>VDB: Delete all chunks where doc_id = document_id
    PL->>FS: Unlink (delete) PDF file
    API->>DB: delete_document(document_id)
    API-->>FE: DeleteResponse {document_id, status="deleted"}
    FE->>FE: Refresh document list
    FE-->>User: Document disappears from sidebar
```

---

## 5. The RAG Pipeline — End to End

This is the most important section of the documentation. It walks through the entire RAG process from start to finish, explaining every step in detail.

### 5.1 Upload & Validation

**What happens:** When a user drags a PDF onto the upload zone, the file goes through two layers of validation.

**Client-side validation** (in `UploadZone.tsx`):
- Checks that the file has a `.pdf` extension
- Prevents the upload from even starting if it is not a PDF

**Server-side validation** (in `validators.py`):
- Checks the `content_type` header is `application/pdf`
- Checks the file extension is `.pdf`
- Reads the file in chunks and verifies the total size does not exceed `max_file_mb` (default 50 MB)
- If validation fails, raises an `HTTPException` with a descriptive error message
- **Crucially**: after reading the file to check size, it rewinds the file pointer back to the beginning (`await file.seek(0)`) so the file can be read again for saving

**Why validate on both sides?** Client-side validation gives instant feedback to the user. Server-side validation is the security layer — you cannot trust the client because anyone could send a request directly to the API using a tool like `curl`, bypassing the frontend entirely.

**Code reference:** `backend/app/utils/validators.py`, `frontend/src/components/UploadZone.tsx`

### 5.2 File Storage

**What happens:** After validation, the PDF is saved to the server's file system.

The upload route (`upload.py`) does the following:
1. Generates a UUID (e.g., `a3f1e2d4-...`) as the `document_id`
2. Constructs the file path: `uploads/{uuid}_{original_filename}`
3. Uses `aiofiles` to write the file in chunks (async, non-blocking)
4. Creates a database record with status `"processing"`
5. Returns HTTP 202 (Accepted) immediately

**Why async file writing?** FastAPI is an asynchronous framework. If we used regular (synchronous) file I/O, the entire server would block while writing the file, preventing other requests from being served. `aiofiles` performs file I/O in a thread pool, keeping the event loop free.

**Code reference:** `backend/app/api/routes/upload.py`

### 5.3 PDF Parsing

**What happens:** The `PDFService` extracts text from each page of the PDF.

Under the hood, it uses **PyMuPDF** (imported as `fitz`):
1. Opens the PDF file
2. Iterates over each page
3. Extracts text using `page.get_text()`
4. Returns a list of `PageText` objects, each containing `page_number` and `text`

Page numbers are 1-indexed (humans count from 1, not 0) for citation purposes.

**Limitations:**
- Scanned PDFs (images of text) will return empty text — PyMuPDF extracts *digital* text, not OCR. To support scanned PDFs, you would need to add an OCR step (see Extension Guide).
- Complex layouts (multi-column, tables) may have jumbled text extraction. For better table extraction, you could integrate a library like `camelot` or `tabula-py`.

**Code reference:** `backend/app/services/pdf_service.py`

### 5.4 Text Chunking

**What happens:** The extracted text is split into overlapping chunks that are small enough for embedding and retrieval.

The `Chunker` class implements a **sliding window** algorithm:

```
Original text (1 page, 2500 characters):
┌─────────────────────────────────────────────────────────────┐
│ Lorem ipsum dolor sit amet, consectetur adipiscing elit...  │
│ ... (2500 characters total) ...                              │
│ ... Sed do eiusmod tempor incididunt ut labore et dolore.   │
└─────────────────────────────────────────────────────────────┘

With chunk_size=1000 and chunk_overlap=200:

Chunk 0: characters 0–999       (1000 chars)
Chunk 1: characters 800–1799    (1000 chars, overlaps with Chunk 0 by 200)
Chunk 2: characters 1600–2499   (900 chars, overlaps with Chunk 1 by 200)
```

Each `Chunk` is a dataclass with:
- `text`: the chunk's text content
- `page_number`: which page it came from (for citations)
- `chunk_index`: its position within the page (0, 1, 2, ...)

**Why overlap?** Imagine a sentence that says: "The revenue was $5.2 million, which represents a 12% increase." If the chunk boundary falls right after "$5.2 million," the second chunk would say "which represents a 12% increase" without knowing *what* increased. With overlap, the full sentence appears in both chunks.

**Implementation detail:** Before chunking, the text is normalized — multiple whitespace characters are collapsed into single spaces. This prevents chunks from being filled with blank space.

**Configuration:**
- `chunk_size` has a minimum of 200 characters (enforced in the constructor). This prevents chunks from being too small to be meaningful.
- `chunk_overlap` should be less than `chunk_size`, or you would get infinite loops.

**Code reference:** `backend/app/rag/chunker.py`

### 5.5 Embedding Generation

**What happens:** Each chunk of text is converted into a 384-dimensional vector using a pre-trained neural network.

The `EmbeddingService` wraps the `SentenceTransformer` model:

1. **Lazy loading**: The model is not loaded into memory when the service is created — only when `embed_texts()` or `embed_query()` is first called. This speeds up server startup.
2. **Thread-safe loading**: Uses a threading `Lock` with double-checked locking to ensure the model is only loaded once, even if multiple requests arrive simultaneously.
3. **Normalization**: Embeddings are L2-normalized (each vector has a length of 1.0). This makes cosine similarity equivalent to dot product, which is computationally faster.
4. **Output format**: Returns a list of lists of `float32` values. Each inner list has 384 elements.

**Analogy:** Think of embedding as translating text into a "coordinate system of meaning." The word "king" might be at position [0.8, 0.2, ...], while "queen" is at [0.7, 0.3, ...] (nearby because they are semantically similar), and "banana" is at [-0.1, 0.9, ...] (far away because it has a very different meaning).

**Code reference:** `backend/app/services/embedding_service.py`

### 5.6 Vector Storage (Indexing)

**What happens:** The embeddings and their associated metadata are stored in ChromaDB for later retrieval.

The `Retriever.add_chunks()` method:
1. Receives `document_id`, `filename`, and the list of chunks
2. Calls `EmbeddingService.embed_texts()` to generate embeddings for all chunk texts
3. Builds metadata for each chunk: `doc_id`, `filename`, `page_number`, `chunk_index`
4. Generates a unique ID for each chunk: `{document_id}_chunk_{i}`
5. Calls `collection.upsert()` to store everything in ChromaDB

**What is "upsert"?** It means "insert if new, update if already exists." This prevents duplicate entries if the same document is processed twice.

**ChromaDB collection configuration:**
- Collection name: `"rag_chunks"`
- Distance metric: cosine distance
- Persistence: data is saved to disk in the `chroma/` directory

**Code reference:** `backend/app/rag/retriever.py`

### 5.7 Retrieval (Semantic Search)

**What happens:** When a user asks a question, the system finds the most relevant chunks from all uploaded documents.

The `Retriever.search()` method:
1. Calls `EmbeddingService.embed_query()` to convert the question into a vector
2. Calls `collection.query()` on ChromaDB with the question vector and `n_results=top_k`
3. ChromaDB compares the question vector against all stored chunk vectors using cosine distance
4. Returns the top K most similar chunks, along with their metadata and distances

The search can optionally be filtered by `document_ids` — if specified, only chunks from those specific documents are searched.

**What does `top_k` mean?** It is the number of results to return. Default is 5, configurable per request (1–20). Higher values give the LLM more context but increase response time and token usage.

**Return format:** Each result contains:
- `text`: the chunk's original text
- `metadata`: `doc_id`, `filename`, `page_number`, `chunk_index`
- `distance`: how far the chunk is from the question (lower = more similar)

**Code reference:** `backend/app/rag/retriever.py`

### 5.8 Prompt Construction

**What happens:** The retrieved chunks, conversation history, and the user's question are assembled into a single prompt string for the LLM.

The `build_prompt()` function in `prompt.py` creates this structure:

```
SYSTEM: You are an enterprise assistant that answers only from the supplied context...

HISTORY:
User: [previous question 1]
Assistant: [previous answer 1]
User: [previous question 2]
Assistant: [previous answer 2]

CONTEXT:
[Source: report.pdf | Page 3]
Revenue in Q3 was $5.2 million, representing a 12% increase...

[Source: report.pdf | Page 7]
The company expanded into three new markets...

QUESTION:
What was the revenue in Q3?
```

**Why this structure?**
- **SYSTEM**: Tells the LLM how to behave. It instructs the LLM to only answer from the provided context and to admit when the context does not contain the answer.
- **HISTORY**: Provides conversational context. If the user asks a follow-up question like "What about Q4?", the LLM needs to know they were previously discussing revenue.
- **CONTEXT**: The retrieved chunks — the "open textbook" for the LLM.
- **QUESTION**: The user's current question.

**Code reference:** `backend/app/rag/prompt.py`

### 5.9 Answer Generation (LLM Call)

**What happens:** The assembled prompt is sent to Google Gemini, which generates a natural-language answer.

The `ChatService._load_llm()` method lazily loads a `ChatGoogleGenerativeAI` instance from the `langchain_google_genai` package:
- Model: `gemini-2.5-flash` (configurable via `model_name` setting)
- API key: from the `gemini_api_key` setting (loaded from the `.env` file)

The LLM call is straightforward: `llm.invoke(prompt)` returns a response object containing the generated text.

**Lazy loading** means the LLM client is only created when it is first needed (when a chat request comes in), not when the server starts. This allows the server to start and serve health checks even if the Gemini API key is not configured.

**Code reference:** `backend/app/services/chat_service.py`

### 5.10 Citation Generation & Deduplication

**What happens:** The system creates citations that link the answer back to specific documents and pages.

After retrieving chunks, the `ChatService.answer()` method:
1. Extracts citation data from each chunk's metadata: `document_name`, `page_number`, `chunk_preview`
2. Deduplicates citations by `(document_name, page_number)` — if multiple chunks came from the same page of the same document, they are merged into a single citation
3. Merged chunks have their previews joined with `"\n\n[...]\n\n"` to indicate that text has been concatenated from multiple excerpts

**Why deduplicate?** Because of chunk overlap, adjacent chunks from the same page might both be retrieved. Without deduplication, the user would see:
- Citation 1: report.pdf, Page 3
- Citation 2: report.pdf, Page 3

With deduplication, they see a single, merged citation with a longer preview.

**Code reference:** `backend/app/services/chat_service.py`

### 5.11 Document Deletion & Cleanup

**What happens:** When a document is deleted, all traces of it are removed from every storage layer.

The deletion process:
1. `RAGPipeline.delete_document()` is called
2. `Retriever.delete_document()` removes all chunks with the matching `doc_id` from ChromaDB
3. The raw PDF file is deleted from the file system (`pathlib.Path.unlink()`)
4. `DocumentService.delete_document()` removes the metadata row from SQLite

**Why delete from all three stores?** If you only deleted the SQLite row, the chunks would still be in ChromaDB and could appear in search results, confusing users. If you only deleted from ChromaDB, the PDF file would waste disk space. Full cleanup requires touching all three.

**Code reference:** `backend/app/rag/pipeline.py`, `backend/app/api/routes/documents.py`

### 5.12 Fallback Behavior

**What happens:** If the Gemini API key is not configured or the LLM call fails, the system still functions — but with a degraded experience.

The `ChatService._fallback_answer()` method returns a message like:
> "Gemini is not configured. Set the GEMINI_API_KEY environment variable to enable AI-generated answers."

This means:
- Users can still upload documents and verify they are processed correctly
- The retrieval pipeline still works (you can see which chunks would have been found)
- Only the answer generation step is skipped
- The health endpoint reports `gemini: false` in this state

**Code reference:** `backend/app/services/chat_service.py`, `backend/app/api/routes/health.py`

---

## 6. Module-by-Module Explanation

This section groups related files into logical modules, explaining the purpose of each module, what it depends on, and what depends on it.

### 6.1 API Layer

**Files:** `api/deps.py`, `api/routes/chat.py`, `api/routes/upload.py`, `api/routes/documents.py`, `api/routes/health.py`

**Purpose:** Receives HTTP requests from the frontend, validates input, delegates to services, and formats responses.

**Depends on:** Services layer, RAG engine, Models (request/response schemas), Config, Core (rate limiter)

**Depended on by:** Nothing (this is the outermost layer of the backend)

**Key responsibilities:**
- Route definition and HTTP method mapping
- Request validation (via Pydantic models)
- Response serialization (via Pydantic response models)
- Dependency injection (via `Depends()` and `deps.py`)
- Rate limiting (via SlowAPI decorator on the chat endpoint)
- Background task scheduling (for document processing)

### 6.2 Configuration

**Files:** `config/settings.py`

**Purpose:** Centralizes all application settings in a single, validated, type-safe object.

**Depends on:** Environment variables (`.env` file), Pydantic's `BaseSettings`

**Depended on by:** Nearly everything (main.py, services, routes, tests)

**Key responsibilities:**
- Loading values from environment variables with sensible defaults
- Type validation (e.g., `chunk_size` must be an integer)
- Singleton pattern via `@lru_cache` — settings are loaded once and reused
- CORS origin parsing (supports both JSON arrays and comma-separated strings)

### 6.3 Database Layer

**Files:** `models/db.py`, `models/requests.py`, `models/responses.py`

**Purpose:** Defines the database schema, request/response shapes, and database connection utilities.

**Depends on:** SQLAlchemy, Pydantic

**Depended on by:** Services layer (DocumentService), API routes, tests

**Key responsibilities:**
- `db.py`: Defines the `Document` ORM model, `build_engine()`, and `build_session_factory()`
- `requests.py`: Defines `ChatRequest` with field validation
- `responses.py`: Defines all API response shapes (UploadResponse, ChatResponse, etc.)

### 6.4 RAG Engine

**Files:** `rag/chunker.py`, `rag/pipeline.py`, `rag/retriever.py`, `rag/prompt.py`

**Purpose:** Implements the core RAG logic — chunking text, storing/retrieving vectors, and building prompts.

**Depends on:** Services (EmbeddingService, PDFService, DocumentService), ChromaDB, Config

**Depended on by:** API routes (upload, documents), ChatService

**Key responsibilities:**
- `chunker.py`: Splits text into overlapping chunks
- `retriever.py`: Manages the ChromaDB collection — add, search, delete, health check
- `pipeline.py`: Orchestrates the full processing pipeline (parse → chunk → embed → index)
- `prompt.py`: Constructs the LLM prompt from history, context, and question

### 6.5 Services

**Files:** `services/chat_service.py`, `services/document_service.py`, `services/embedding_service.py`, `services/pdf_service.py`

**Purpose:** Contains the business logic layer — each service encapsulates one domain of functionality.

**Depends on:** RAG engine (Retriever, Prompt), Config, Database models, External APIs (Gemini)

**Depended on by:** API routes, RAG pipeline

**Key responsibilities:**
- `chat_service.py`: Orchestrates the full chat flow (retrieve → prompt → LLM → citations) and manages session memory
- `document_service.py`: CRUD operations on document metadata in SQLite
- `embedding_service.py`: Generates text embeddings using SentenceTransformers
- `pdf_service.py`: Extracts text from PDF files

### 6.6 Utilities

**Files:** `utils/logger.py`, `utils/validators.py`

**Purpose:** Cross-cutting concerns that are used throughout the application.

**Depends on:** Python standard library, FastAPI exceptions

**Depended on by:** Main app (logger), Upload route (validators)

**Key responsibilities:**
- `logger.py`: Configures JSON-structured logging for production observability
- `validators.py`: Validates uploaded PDF files (type, extension, size)

### 6.7 Frontend API Client

**Files:** `api/client.ts`, `api/client.test.ts`

**Purpose:** Provides typed functions for every API call the frontend makes.

**Depends on:** Browser `fetch` API, `XMLHttpRequest`, Types

**Depended on by:** Hooks (`useChat`, `useDocuments`)

**Key responsibilities:**
- `fetchDocuments()`, `fetchDocument(id)`, `deleteDocument(id)`: Simple fetch wrappers
- `uploadDocument(file, onProgress)`: Uses XMLHttpRequest for upload progress tracking
- `sendChat(payload)`: Sends a chat request with JSON body
- `parseJson<T>(response)`: Generic response parser with error handling

### 6.8 Frontend Hooks

**Files:** `hooks/useChat.ts`, `hooks/useDocuments.ts` (and their test files)

**Purpose:** Encapsulate all state management and side effects into reusable hooks.

**Depends on:** API client, Types, React hooks (`useState`, `useEffect`, `useCallback`)

**Depended on by:** `App.tsx` (root page component)

**Key responsibilities:**
- `useChat`: Manages chat messages, session IDs, sending state, error state
- `useDocuments`: Manages document list, upload progress, polling for processing status

### 6.9 Frontend Components

**Files:** `components/Sidebar.tsx`, `components/ChatWindow.tsx`, `components/MessageBubble.tsx`, `components/CitationCard.tsx`, `components/UploadZone.tsx`, `components/ErrorToast.tsx`, `components/LoadingDots.tsx`

**Purpose:** Reusable UI building blocks that compose the application's interface.

**Depends on:** Types, Props from parent components

**Depended on by:** `App.tsx` (top-level), each other (e.g., ChatWindow renders MessageBubble, MessageBubble renders CitationCard)

**Key responsibilities:**
- Rendering UI based on props
- Handling user interactions (clicks, drag-and-drop, form submission)
- Applying Tailwind CSS styles for responsive, dark-mode design

### 6.10 Frontend Types

**Files:** `types/index.ts`

**Purpose:** Defines TypeScript interfaces that represent the data shapes used throughout the frontend.

**Depends on:** Nothing

**Depended on by:** Everything in the frontend (API client, hooks, components)

**Key types:** `DocumentItem`, `DocumentDetail`, `Citation`, `Message`, `ChatRequest`, `ChatResponse`, `UploadResponse`

---

## 7. File-by-File Documentation

This section documents every single file in the project using a consistent template.

### 7.1 Root Configuration Files

---

### File: `.env`

- **Purpose**: Stores sensitive configuration values (API keys) and environment-specific settings that should not be committed to version control.
- **Main Symbols**: Key-value pairs like `GEMINI_API_KEY=your_key_here`
- **Dependencies**: Read by Pydantic's `BaseSettings` in `config/settings.py`
- **How It Works**: When the FastAPI app starts, `Settings(BaseSettings)` automatically reads this file and maps each key to a setting field. For example, the key `GEMINI_API_KEY` maps to the `gemini_api_key` field.
- **Relationship to Other Files**: Referenced by `settings.py` via `SettingsConfigDict(env_file=".env")`. Also referenced in `docker-compose.yml` via `env_file: .env`.
- **Important Implementation Details**: This file is listed in `.gitignore` and must never be committed to version control, as it may contain real API keys.
- **Edge Cases / Limitations**: If this file is missing, the app still starts but will use defaults (no Gemini API key, meaning the LLM fallback will be used).
- **How to Extend It**: Add new key-value pairs here, then add corresponding fields to the `Settings` class in `settings.py`.
- **Learning Notes**: Environment variables are the standard way to configure applications in the cloud (the "twelve-factor app" methodology). The `.env` file is a development convenience — in production, these values typically come from a secrets manager or container orchestration platform.

---

### File: `.env.example`

- **Purpose**: A template showing which environment variables the project needs, with placeholder values. Safe to commit to version control.
- **Main Symbols**: Same keys as `.env`, but with dummy values like `your_gemini_api_key_here`.
- **Dependencies**: None — this file is for humans, not code.
- **How It Works**: New developers copy this file to `.env` and fill in their real values: `cp .env.example .env`.
- **Relationship to Other Files**: Mirrors the structure of `.env`.
- **Important Implementation Details**: Keep this in sync whenever you add a new environment variable.
- **Edge Cases / Limitations**: If this file gets out of sync with `settings.py`, developers might miss required variables.
- **How to Extend It**: Add new variables with descriptive placeholder values and comments.
- **Learning Notes**: The `.env.example` pattern is a widely adopted convention in open-source projects. It communicates which variables are needed without exposing actual secrets.

---

### File: `docker-compose.yml`

- **Purpose**: Defines and orchestrates the multi-container application (backend + frontend) with Docker Compose.
- **Main Symbols**: Services `backend` and `frontend`, volumes `backend_uploads`, `backend_chroma`, `backend_sqlite`.
- **Dependencies**: Docker Engine, Docker Compose CLI, backend `Dockerfile`, frontend `Dockerfile`.
- **How It Works**:
  1. Defines a `backend` service: builds from `./backend`, loads `.env`, exposes port 8000, mounts three named volumes for persistent data.
  2. Defines a `frontend` service: builds from `./frontend`, depends on `backend` (starts after it), exposes port 5173.
  3. Defines three named volumes to persist data across container restarts.
- **Relationship to Other Files**: References `backend/Dockerfile` and `frontend/Dockerfile` for build instructions. References `.env` for environment variables.
- **Important Implementation Details**:
  - The `depends_on` directive ensures the frontend container waits for the backend to start, but it does *not* wait for the backend to be *ready* (healthy). For true health-check-based startup, you would use `depends_on.condition: service_healthy`.
  - Named volumes (not bind mounts) are used, which Docker manages. This means data is stored inside Docker's internal storage, not in a directory you can see on your host machine.
- **Edge Cases / Limitations**: If you need to inspect or back up the volume data, you need to use `docker volume inspect` or mount the volumes to a utility container.
- **How to Extend It**: Add new services (e.g., a PostgreSQL database), add new volumes, add health checks, add resource limits.
- **Learning Notes**: Docker Compose files use YAML syntax. Indentation matters — use spaces, not tabs. The `version` key is optional in modern Docker Compose.

---

### File: `pytest.ini`

- **Purpose**: Configures pytest settings for the Python test suite.
- **Main Symbols**: Pytest configuration keys (e.g., `testpaths`, `addopts`).
- **Dependencies**: pytest package.
- **How It Works**: When you run `pytest`, it automatically reads this file and applies the settings. Common settings include the test directory path, default command-line options (like `-v` for verbose), and marker definitions.
- **Relationship to Other Files**: Affects all test files in `backend/tests/`.
- **Important Implementation Details**: This file is at the project root, so you can run `pytest` from the project root and it will find the tests.
- **Edge Cases / Limitations**: If you move test files, update the `testpaths` setting.
- **How to Extend It**: Add custom markers, change verbosity, add coverage options.
- **Learning Notes**: Alternatives to `pytest.ini` include `pyproject.toml` (under `[tool.pytest.ini_options]`) and `setup.cfg` (under `[tool:pytest]`). All achieve the same goal.

---

### File: `README.md`

- **Purpose**: The project's front page — the first thing visitors see on GitHub.
- **Main Symbols**: Markdown sections (headings, code blocks, badges).
- **Dependencies**: None.
- **How It Works**: Rendered as HTML by GitHub, GitLab, or any markdown viewer.
- **Relationship to Other Files**: May reference other files like `docker-compose.yml`, `.env.example`.
- **Important Implementation Details**: Keep it concise — detailed documentation belongs in this file (DOCUMENTATION.md).
- **Edge Cases / Limitations**: Large README files can be overwhelming; link to detailed docs instead.
- **How to Extend It**: Add badges (build status, coverage), screenshots, a quick-start section.
- **Learning Notes**: A good README answers: What is this? How do I install it? How do I use it? How do I contribute?

---

### 7.2 Backend Files

---

### File: `backend/Dockerfile`

- **Purpose**: Instructions for Docker to build the backend container image.
- **Main Symbols**: `FROM`, `WORKDIR`, `COPY`, `RUN`, `CMD` Dockerfile directives.
- **Dependencies**: Docker build context (the `backend/` directory), `requirements.txt`.
- **How It Works** (step by step):
  1. `FROM python:3.11-slim` — Start from a minimal Python 3.11 image (Debian-based, without extras).
  2. `WORKDIR /app/backend` — Set the working directory inside the container.
  3. `RUN apt-get update && apt-get install -y build-essential curl` — Install system-level build tools (needed for some Python packages that compile C extensions) and `curl` (useful for health checks).
  4. `COPY requirements.txt .` — Copy just the requirements file first (Docker layer caching optimization).
  5. `RUN pip install -r requirements.txt` — Install Python dependencies. This layer is cached if `requirements.txt` has not changed, making rebuilds faster.
  6. `COPY . .` — Copy the rest of the source code.
  7. `RUN mkdir -p uploads chroma data` — Create directories for file uploads, ChromaDB data, and SQLite database.
  8. `CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]` — Start the FastAPI app using Uvicorn ASGI server.
- **Relationship to Other Files**: Referenced by `docker-compose.yml` as the build context for the backend service.
- **Important Implementation Details**:
  - The two-step copy (`requirements.txt` first, then everything else) exploits Docker layer caching. If you only change source code but not dependencies, Docker reuses the cached layer with installed packages, making builds much faster.
  - `--host 0.0.0.0` is essential — it tells Uvicorn to listen on all network interfaces inside the container, making it accessible from outside.
- **Edge Cases / Limitations**: The `python:3.11-slim` image may lack some system libraries. If you add a Python package that needs a specific system lib (e.g., `psycopg2` needs `libpq-dev`), add it to the `apt-get install` line.
- **How to Extend It**: Add a non-root user for security, add a `.dockerignore` file to exclude test files, add a healthcheck instruction.
- **Learning Notes**: A Dockerfile is like a recipe: each instruction creates a "layer." Docker caches layers, so ordering instructions from least-frequently-changed to most-frequently-changed optimizes build speed.

---

### File: `backend/requirements.txt`

- **Purpose**: Lists all Python packages needed to run the backend in production.
- **Main Symbols**: Package names with version specifiers (e.g., `fastapi>=0.100.0`).
- **Dependencies**: pip (Python's package manager).
- **How It Works**: `pip install -r requirements.txt` reads this file and installs every listed package (and their transitive dependencies).
- **Relationship to Other Files**: Used in the `Dockerfile` and by developers setting up locally.
- **Important Implementation Details**: Pin versions (e.g., `fastapi==0.110.0`) for reproducible builds in production. Use `>=` during development for flexibility.
- **Edge Cases / Limitations**: Transitive dependency conflicts can arise. Use `pip freeze > requirements.txt` to capture exact versions.
- **How to Extend It**: Add new packages as needed. Consider using `pip-tools` or `poetry` for better dependency management.
- **Learning Notes**: `requirements.txt` is the simplest way to manage Python dependencies. For complex projects, `pyproject.toml` with Poetry or PDM is more robust.

---

### File: `backend/requirements-dev.txt`

- **Purpose**: Lists additional Python packages needed for development and testing (not needed in production).
- **Main Symbols**: `pytest`, `pytest-cov` (and potentially others like `httpx` for test client).
- **Dependencies**: `requirements.txt` (usually includes it via `-r requirements.txt`).
- **How It Works**: Developers install both: `pip install -r requirements-dev.txt`.
- **Relationship to Other Files**: Used by developers and CI/CD pipelines, not by the production Dockerfile.
- **Important Implementation Details**: Keeping dev dependencies separate prevents bloating the production image.
- **Edge Cases / Limitations**: Make sure test dependencies stay compatible with production dependencies.
- **How to Extend It**: Add linters (`ruff`, `flake8`), formatters (`black`), type checkers (`mypy`).
- **Learning Notes**: The convention of separate `requirements.txt` and `requirements-dev.txt` is common in Python projects. Some projects use a single file with "extras" instead.

---

### File: `backend/app/__init__.py`

- **Purpose**: Makes the `app` directory a Python package.
- **Main Symbols**: Empty file.
- **Dependencies**: None.
- **How It Works**: Python requires an `__init__.py` file in a directory to treat it as a package that can be imported. This file can be empty.
- **Relationship to Other Files**: Enables imports like `from app.main import app`.
- **Important Implementation Details**: In modern Python (3.3+), "namespace packages" allow imports without `__init__.py`, but it is still best practice to include it for clarity.
- **Edge Cases / Limitations**: None.
- **How to Extend It**: You can add package-level exports here, but keeping it empty is fine.
- **Learning Notes**: Every `__init__.py` in this project is empty — they exist solely to mark directories as packages.

---

### File: `backend/app/main.py`

- **Purpose**: The entry point of the FastAPI application. Creates the app, configures middleware, initializes services, and mounts routers.
- **Main Symbols**: `app` (FastAPI instance), `lifespan()` (async context manager), root route `/`.
- **Dependencies**: FastAPI, all services, all routers, settings, rate limiter.
- **How It Works** (step by step):
  1. **`from __future__ import annotations`** at the top. This defers evaluation of type annotations — all type hints become strings at runtime instead of being evaluated immediately. This is necessary because Pydantic v2 and certain decorators can conflict with eagerly-evaluated type annotations (see Troubleshooting).
  2. **`lifespan` async context manager**: This is FastAPI's way of running startup/shutdown code.
     - **On startup** (before `yield`):
       - Creates `uploads/` and `chroma/` directories if they don't exist
       - Builds the SQLAlchemy engine and creates all database tables
       - Instantiates all services: `EmbeddingService`, `Retriever`, `DocumentService`, `PDFService`, `SessionMemoryStore`, `ChatService`, `RAGPipeline`
       - Stores every service instance on `app.state` (e.g., `app.state.chat_service = chat_service`). This is the dependency injection mechanism — route handlers access services via `request.app.state`.
       - Records `app.state._start_time` for uptime calculation
     - **On shutdown** (after `yield`): Implicit cleanup. Python's garbage collector handles resource cleanup.
  3. **Middleware configuration**:
     - `CORSMiddleware`: Allows the frontend origin to make cross-origin requests. Configured with `allow_origins`, `allow_credentials`, `allow_methods`, `allow_headers`.
     - `SlowAPIMiddleware`: Enables rate limiting on routes decorated with `@limiter.limit()`.
     - `RateLimitExceeded` exception handler: Returns a clean JSON error when a rate limit is exceeded.
  4. **Router mounting**: Four routers under `/api/v1`:
     - `/api/v1/health` → health router
     - `/api/v1/upload` → upload router (tagged "Upload")
     - `/api/v1/chat` → chat router (tagged "Chat")
     - `/api/v1/documents` → documents router (tagged "Documents")
  5. **Root route**: `GET /` returns `{"status": "ok", "message": "Enterprise RAG API"}` — useful for quick smoke tests.
- **Relationship to Other Files**: This is the hub of the backend. It imports and wires together every other module.
- **Important Implementation Details**:
  - The `lifespan` pattern (using `@asynccontextmanager`) replaced the older `@app.on_event("startup")` pattern in FastAPI 0.93+.
  - `app.state` is a Starlette feature that allows arbitrary attributes to be attached to the app instance. It is thread-safe for reads.
  - The `from __future__ import annotations` import MUST be at the very top of the file (before any other imports) — this is a Python language requirement.
- **Edge Cases / Limitations**:
  - If `build_engine()` fails (e.g., invalid `db_url`), the entire startup fails and the server does not start.
  - The `chroma/` and `uploads/` directories are created with `exist_ok=True`, so re-running is safe.
- **How to Extend It**: Add new routers, add authentication middleware, add startup health checks.
- **Learning Notes**: The lifespan pattern is a "context manager" — code before `yield` runs on startup, code after `yield` runs on shutdown. This is similar to a `try/finally` block.

---

### File: `backend/app/config/settings.py`

- **Purpose**: Defines all application configuration as a typed, validated Pydantic model.
- **Main Symbols**: `Settings` (class), `get_settings()` (cached factory function).
- **Dependencies**: Pydantic's `BaseSettings`, `SettingsConfigDict`, `functools.lru_cache`.
- **How It Works** (step by step):
  1. `Settings` extends `BaseSettings`, which automatically loads values from environment variables.
  2. Each field has a type and a default value:
     - `gemini_api_key: str = ""` — empty by default (LLM is optional)
     - `model_name: str = "gemini-2.5-flash"` — the Gemini model to use
     - `chunk_size: int = 1000` — maximum characters per chunk
     - `chunk_overlap: int = 200` — overlap between consecutive chunks
     - `top_k: int = 5` — default number of retrieval results
     - `max_file_mb: int = 50` — maximum upload file size in megabytes
     - `session_memory_k: int = 10` — number of conversation turns to remember
     - `chroma_persist_dir: str = "chroma"` — ChromaDB storage directory
     - `upload_dir: str = "uploads"` — PDF storage directory
     - `db_url: str = "sqlite:///data/rag.db"` — SQLite database URL
     - `log_level: str = "INFO"` — logging verbosity
     - `cors_origins_raw: str = '["http://localhost:5173"]'` — allowed CORS origins
     - `rate_limit_chat: str = "10/minute"` — chat endpoint rate limit
  3. `model_config = SettingsConfigDict(env_file=".env", extra="ignore", protected_namespaces=('settings_',))`
     - `env_file=".env"`: read values from the `.env` file
     - `extra="ignore"`: ignore unknown environment variables without raising errors
     - `protected_namespaces=('settings_',)`: override Pydantic's default namespace protection (which would conflict with `model_name` since Pydantic reserves the `model_` prefix)
  4. `cors_origins` property: Parses `cors_origins_raw` as either a JSON array or a comma-separated string.
  5. `get_settings()` is decorated with `@lru_cache(maxsize=1)`: this means the `Settings` object is created once and reused for all subsequent calls. This is the **singleton pattern** — there is only ever one `Settings` instance.
- **Relationship to Other Files**: Used by `main.py` (to configure services), `deps.py` (to inject into routes), many services.
- **Important Implementation Details**:
  - `protected_namespaces=('settings_',)` is critical. Without it, Pydantic v2 would raise a warning or error because `model_name` starts with `model_`, which Pydantic reserves for its own internal attributes.
  - Environment variables override defaults. For example, setting `CHUNK_SIZE=500` in `.env` changes the chunk size.
  - The `@lru_cache` ensures that parsing `.env` only happens once, even if `get_settings()` is called hundreds of times.
- **Edge Cases / Limitations**:
  - `lru_cache` means settings are frozen after first load. If you change `.env` while the server is running, you need to restart the server.
  - The `cors_origins` parser tries JSON first, then falls back to comma-separated. This handles both `["http://localhost"]` and `http://localhost,http://example.com`.
- **How to Extend It**: Add new settings as class fields with defaults. They will automatically be configurable via environment variables.
- **Learning Notes**: `BaseSettings` is a Pydantic class specifically designed for configuration management. Unlike regular `BaseModel`, it reads from environment variables automatically.

---

### File: `backend/app/core/rate_limit.py`

- **Purpose**: Creates a singleton rate limiter instance used across the application.
- **Main Symbols**: `limiter` (Limiter instance).
- **Dependencies**: `slowapi` package, `slowapi.util.get_remote_address`.
- **How It Works**:
  1. Creates a `Limiter` instance with `key_func=get_remote_address` — this means rate limits are applied per IP address.
  2. `default_limits=[]` means no default rate limit — only routes explicitly decorated with `@limiter.limit()` are rate-limited.
- **Relationship to Other Files**: Imported by `main.py` (to add middleware) and by `chat.py` (to decorate the chat endpoint).
- **Important Implementation Details**: `get_remote_address` extracts the client's IP from the request. Behind a reverse proxy, you may need to use `X-Forwarded-For` instead.
- **Edge Cases / Limitations**: In-memory rate limiting is lost on server restart. For persistent rate limiting, use Redis as a backend.
- **How to Extend It**: Add `default_limits=["100/hour"]` to rate-limit all routes by default.
- **Learning Notes**: Rate limiting prevents abuse — a single user cannot overwhelm the server with thousands of requests per second.

---

### File: `backend/app/models/db.py`

- **Purpose**: Defines the SQLAlchemy database model and connection utilities.
- **Main Symbols**: `Base` (DeclarativeBase), `Document` (ORM model), `build_engine()`, `build_session_factory()`.
- **Dependencies**: SQLAlchemy, `datetime`, `uuid`.
- **How It Works** (step by step):
  1. `Base(DeclarativeBase)` — the base class that all ORM models inherit from. It provides the `__tablename__` and column mapping machinery.
  2. `Document(Base)` — represents a row in the `documents` table:
     - `id`: String(36), primary key. Set to a UUID4 string.
     - `filename`: String, the original file name.
     - `file_path`: String, the path on disk.
     - `page_count`: Integer, nullable (set after processing).
     - `status`: String, default `"processing"`. Transitions to `"ready"` or `"failed"`.
     - `error_msg`: String, nullable (set if processing fails).
     - `file_size`: Integer, nullable (file size in bytes).
     - `uploaded_at`: DateTime, default `utcnow`.
     - `updated_at`: DateTime, default `utcnow`, updates on every change (`onupdate=utcnow`).
  3. `build_engine(db_url)`: Creates a SQLAlchemy `Engine` with `check_same_thread=False` (required for SQLite when used in a multi-threaded ASGI server like Uvicorn).
  4. `build_session_factory(engine)`: Creates a `sessionmaker` bound to the engine, used to create database sessions.
- **Relationship to Other Files**: Used by `main.py` (creates engine, tables, session factory), `document_service.py` (CRUD operations).
- **Important Implementation Details**:
  - `check_same_thread=False` is a SQLite-specific workaround. SQLite by default only allows access from the thread that created the connection, but Uvicorn may serve requests from different threads.
  - UUIDs are stored as strings (not native UUID columns) for SQLite compatibility.
- **Edge Cases / Limitations**: SQLite has no concurrent write support — only one write at a time. For high-traffic production use, switch to PostgreSQL.
- **How to Extend It**: Add new columns (e.g., `uploaded_by` for user tracking), add new models (e.g., `User`).
- **Learning Notes**: The `DeclarativeBase` pattern maps Python classes to database tables. Each class attribute (with `Mapped[]` type) maps to a column.

---

### File: `backend/app/models/requests.py`

- **Purpose**: Defines the Pydantic model for incoming chat requests.
- **Main Symbols**: `ChatRequest` (BaseModel).
- **Dependencies**: Pydantic.
- **How It Works**:
  - `question: str` with `min_length=1, max_length=4000`: the user's question. Must be at least 1 character and at most 4,000 characters.
  - `session_id: str` with `min_length=8`: identifies the conversation session. Must be at least 8 characters to prevent accidental collisions.
  - `top_k: Optional[int]` with `ge=1, le=20`: optionally override the default number of retrieval results. Must be between 1 and 20 (inclusive).
- **Relationship to Other Files**: Used by the `chat.py` route as the request body type.
- **Important Implementation Details**: Pydantic validates these constraints automatically. If a request violates them, FastAPI returns a 422 Unprocessable Entity response with details about which fields are invalid.
- **Edge Cases / Limitations**: The `max_length=4000` limit is arbitrary. Adjust based on your LLM's context window.
- **How to Extend It**: Add fields like `document_ids: Optional[list[str]]` to filter which documents to search.
- **Learning Notes**: `Optional[int]` means the field can be `None` (omitted from the request). `ge` = "greater than or equal to", `le` = "less than or equal to".

---

### File: `backend/app/models/responses.py`

- **Purpose**: Defines Pydantic models for all API responses.
- **Main Symbols**: `UploadResponse`, `Citation`, `ChatResponse`, `DocumentListItem`, `DocumentDetail`, `DeleteResponse`, `HealthResponse`.
- **Dependencies**: Pydantic.
- **How It Works**: Each model defines the shape of an API response. FastAPI uses these to:
  1. Serialize Python objects to JSON
  2. Generate OpenAPI documentation (Swagger UI)
  3. Validate response data
  Here are all the response models:
  - `UploadResponse`: `document_id`, `filename`, `status`, `message` — returned after uploading a document.
  - `Citation`: `document_name`, `page_number`, `chunk_preview` — a single source reference in a chat response.
  - `ChatResponse`: `answer`, `citations` (list of Citation), `session_id`, `sources_used` — the complete answer to a chat question.
  - `DocumentListItem`: `id`, `filename`, `page_count`, `status`, `uploaded_at`, `file_size_bytes` — a document in the list view.
  - `DocumentDetail`: extends `DocumentListItem` with `error_msg`, `updated_at` — a document in the detail view.
  - `DeleteResponse`: `document_id`, `status`, `message` — confirmation of deletion.
  - `HealthResponse`: `status`, `chromadb` (bool), `gemini` (bool), `uptime_seconds` (float) — system health status.
- **Relationship to Other Files**: Used by all route handlers as `response_model` parameter. Consumed by the frontend (the TypeScript types mirror these shapes).
- **Important Implementation Details**: Using `response_model` in route decorators ensures FastAPI strips any extra fields from the response (security) and generates accurate API documentation.
- **Edge Cases / Limitations**: If you add a field here but not in the frontend `types/index.ts`, the frontend will silently ignore it.
- **How to Extend It**: Add new response models for new endpoints. Keep them in sync with frontend types.
- **Learning Notes**: Response models are part of the API contract. Changing them is a breaking change that may require frontend updates.

---

### File: `backend/app/api/deps.py`

- **Purpose**: Dependency injection helpers that extract services from `app.state`.
- **Main Symbols**: `get_settings()`, `get_document_service()`, `get_pipeline()`, `get_chat_service()`.
- **Dependencies**: FastAPI's `Request` object.
- **How It Works**: Each function receives the FastAPI `Request` object, accesses `request.app.state`, and returns the appropriate service:
  ```python
  def get_chat_service(request: Request) -> ChatService:
      return request.app.state.chat_service
  ```
  Route handlers use these with `Depends()`:
  ```python
  @router.post("/chat")
  def chat(body: ChatRequest, service = Depends(get_chat_service)):
      return service.answer(body.question, ...)
  ```
- **Relationship to Other Files**: Imported by all route handlers. The services were stored on `app.state` in `main.py`.
- **Important Implementation Details**: This is FastAPI's recommended dependency injection pattern. It decouples routes from service creation.
- **Edge Cases / Limitations**: If a service is not initialized on `app.state`, accessing it will raise an `AttributeError`.
- **How to Extend It**: Add new functions for new services.
- **Learning Notes**: `Depends()` is FastAPI's dependency injection mechanism. It calls the provided function and injects its return value as a parameter.

---

### File: `backend/app/api/routes/chat.py`

- **Purpose**: Implements the `POST /chat` endpoint for asking questions.
- **Main Symbols**: `router` (APIRouter), `limit_chat` (decorator), `chat()` (route handler).
- **Dependencies**: FastAPI, SlowAPI limiter, `ChatRequest`, `ChatResponse`, `deps.py`.
- **How It Works** (step by step):
  1. **`from __future__ import annotations`**: Defers type annotation evaluation (required to avoid Pydantic namespace conflicts).
  2. **`limit_chat` decorator**: A custom wrapper around `@limiter.limit()`. The direct SlowAPI decorator can conflict with Pydantic's namespace protection because SlowAPI inspects function signatures. This wrapper uses `functools.wraps` to apply the rate limit cleanly.
  3. **Route handler `chat()`**:
     - Receives a `ChatRequest` body (validated by Pydantic)
     - Receives `chat_service` via dependency injection
     - Receives `settings` via dependency injection
     - Calls `chat_service.answer(question, session_id, top_k or settings.top_k)`
     - Returns a `ChatResponse` with the answer, citations, session_id, and sources_used count
- **Relationship to Other Files**: Calls `ChatService.answer()`, uses `ChatRequest`/`ChatResponse` models, uses `limiter` from `rate_limit.py`.
- **Important Implementation Details**:
  - The `limit_chat` wrapper is a workaround for a specific compatibility issue between SlowAPI's introspection and Pydantic v2's `model_` namespace protection. See Troubleshooting for details.
  - `top_k` falls back to `settings.top_k` (default 5) if not provided in the request.
- **Edge Cases / Limitations**: Rate limit is per-IP. Behind a load balancer, all users may appear to have the same IP unless `X-Forwarded-For` is configured.
- **How to Extend It**: Add support for document filtering (only search specific documents), add streaming support.
- **Learning Notes**: A decorator is a function that wraps another function, adding behavior before/after it runs. `@limiter.limit("10/minute")` wraps the route handler to check and enforce the rate limit before the handler executes.

---

### File: `backend/app/api/routes/upload.py`

- **Purpose**: Implements the `POST /upload` endpoint for uploading PDF documents.
- **Main Symbols**: `router` (APIRouter), `_save_upload()` (async helper), `_background_process()` (background task), `upload()` (route handler).
- **Dependencies**: FastAPI (UploadFile, BackgroundTasks), aiofiles, uuid, settings, validators, services.
- **How It Works** (step by step):
  1. **`from __future__ import annotations`**: Same namespace conflict workaround.
  2. **`_save_upload(file, destination)`**: Reads the uploaded file in chunks and writes it to disk using `aiofiles`. This is async to avoid blocking the event loop during large file uploads.
  3. **`_background_process(document_id, file_path, filename, request_state)`**: Called as a FastAPI `BackgroundTask` after the response is sent. It calls `pipeline.process_document()` to run the full processing pipeline (PDF parsing → chunking → embedding → indexing).
  4. **`upload()` route handler**:
     - Receives the uploaded file (as `UploadFile`)
     - Calls `validate_pdf_upload()` to check type, extension, and size
     - Generates a UUID as `document_id`
     - Constructs the file path: `{upload_dir}/{document_id}_{filename}`
     - Saves the file to disk with `_save_upload()`
     - Creates a database record with `document_service.create_document()` (status = "processing")
     - Adds `_background_process` to `BackgroundTasks` (FastAPI will run it after sending the response)
     - Returns HTTP 202 (Accepted) with `UploadResponse`
- **Relationship to Other Files**: Uses `validators.py`, `DocumentService`, `RAGPipeline`, `Settings`. Returns `UploadResponse` model.
- **Important Implementation Details**:
  - HTTP 202 (Accepted) means "I received your request and will process it later." This is standard for asynchronous operations.
  - `BackgroundTasks` is a FastAPI feature that runs a function after the response is sent. This allows the upload response to return immediately while processing happens in the background.
  - The `request_state` is passed to the background task because the background task needs access to `app.state` services (pipeline), but FastAPI's `Request` object may not be available after the response is sent.
- **Edge Cases / Limitations**:
  - If the server crashes during background processing, the document will remain in "processing" status forever. A production system should have a periodic cleanup job for stale "processing" documents.
  - The file is saved before the database record is created. If the database insert fails, an orphan file remains on disk.
- **How to Extend It**: Add support for other file types (DOCX, TXT), add a webhook notification when processing completes.
- **Learning Notes**: The "accept immediately, process later" pattern is common in APIs that perform expensive operations. The client polls for status updates rather than waiting for the operation to complete.

---

### File: `backend/app/api/routes/documents.py`

- **Purpose**: Implements document listing, detail, and deletion endpoints.
- **Main Symbols**: `router` (APIRouter), `list_documents()`, `get_document()`, `delete_document()`.
- **Dependencies**: FastAPI, `DocumentService`, `RAGPipeline`, response models.
- **How It Works**:
  1. **`GET /documents`**: Calls `document_service.list_documents()`, returns a list of `DocumentListItem` objects sorted by `uploaded_at` descending (newest first).
  2. **`GET /documents/{document_id}`**: Calls `document_service.get_document(document_id)`. If found, returns a `DocumentDetail` object. If not found, raises HTTP 404.
  3. **`DELETE /documents/{document_id}`**: First retrieves the document (404 if not found). Then calls `pipeline.delete_document()` to remove from ChromaDB and file system. Then calls `document_service.delete_document()` to remove from SQLite. Returns a `DeleteResponse`.
- **Relationship to Other Files**: Uses `DocumentService` and `RAGPipeline` from deps. Returns response models from `responses.py`.
- **Important Implementation Details**: Deletion is a multi-step process across three storage systems (ChromaDB, file system, SQLite). If one step fails, the others may not execute, leaving the system in an inconsistent state. A production system should use transactions or compensating actions.
- **Edge Cases / Limitations**: No authentication — anyone can delete any document. See Extension Guide for adding auth.
- **How to Extend It**: Add filtering (by status, date range), add pagination, add bulk deletion.
- **Learning Notes**: `{document_id}` in the URL path is a *path parameter*. FastAPI automatically extracts it and passes it to the function.

---

### File: `backend/app/api/routes/health.py`

- **Purpose**: Implements the `GET /health` endpoint for system health monitoring.
- **Main Symbols**: `router` (APIRouter), `health()` (route handler).
- **Dependencies**: FastAPI, `Retriever`, `Settings`, `time`.
- **How It Works**:
  1. Calls `retriever.healthcheck()` to verify ChromaDB is responding (calls `collection.count()`).
  2. Checks if `gemini_api_key` is configured (non-empty string).
  3. Calculates uptime: `time.time() - app.state._start_time`.
  4. Returns a `HealthResponse` with status, `chromadb` (bool), `gemini` (bool), and `uptime_seconds`.
- **Relationship to Other Files**: Accesses `app.state` for retriever, settings, and start time.
- **Important Implementation Details**: The health endpoint does not require rate limiting (it is lightweight and should always be accessible for monitoring systems).
- **Edge Cases / Limitations**: This is a basic health check. A production system might also check database connectivity, disk space, and memory usage.
- **How to Extend It**: Add database health check, add version info, add dependency status.
- **Learning Notes**: Health endpoints are essential for container orchestration (Docker, Kubernetes) to determine if a container is alive and should receive traffic.

---

### File: `backend/app/rag/chunker.py`

- **Purpose**: Splits extracted page text into overlapping chunks suitable for embedding and retrieval.
- **Main Symbols**: `Chunk` (dataclass), `Chunker` (class), `chunk_page()`, `chunk_pages()`.
- **Dependencies**: Python standard library only (`dataclasses`, `re`).
- **How It Works** (step by step):
  1. **`Chunk` dataclass**: A simple container with `text`, `page_number`, and `chunk_index`.
  2. **`Chunker.__init__(chunk_size, chunk_overlap)`**: Stores chunk_size (minimum 200) and chunk_overlap.
  3. **`chunk_page(text, page_number)`**:
     - Normalizes whitespace: replaces multiple spaces/newlines with a single space and strips leading/trailing whitespace.
     - If the cleaned text is empty, returns an empty list.
     - Uses a sliding window: starts at position 0, takes `chunk_size` characters, creates a `Chunk`, then advances by `chunk_size - chunk_overlap` characters.
     - Continues until the start position exceeds the text length.
  4. **`chunk_pages(pages)`**: Iterates over all pages and calls `chunk_page()` for each, aggregating all chunks into a single list.
- **Relationship to Other Files**: Used by `RAGPipeline.process_document()`. Receives `PageText` objects from `PDFService`.
- **Important Implementation Details**:
  - The step size is `chunk_size - chunk_overlap`. With defaults (1000 - 200 = 800), each window advances 800 characters, creating a 200-character overlap.
  - Blank pages (empty after normalization) are silently skipped.
  - The minimum chunk_size of 200 prevents degenerate cases where chunk_overlap >= chunk_size (which would cause infinite loops).
- **Edge Cases / Limitations**:
  - Chunks may split mid-word or mid-sentence. For better quality, consider sentence-aware chunking (split at sentence boundaries).
  - Very short pages produce a single chunk even if shorter than `chunk_size`.
- **How to Extend It**: Add sentence-aware splitting (using NLP sentence tokenizers), add metadata about chunk position within the document.
- **Learning Notes**: The sliding window approach is the simplest chunking strategy. More sophisticated methods include recursive character splitting, semantic splitting (split at topic changes), and markdown-aware splitting.

---

### File: `backend/app/rag/pipeline.py`

- **Purpose**: Orchestrates the full document processing pipeline: parse → chunk → embed → index.
- **Main Symbols**: `RAGPipeline` (class), `process_document()`, `delete_document()`.
- **Dependencies**: `PDFService`, `EmbeddingService`, `Retriever`, `DocumentService`, `Settings`, `Chunker`.
- **How It Works** (step by step):
  1. **`__init__`**: Receives all dependencies and stores them. Creates a `Chunker` instance using `settings.chunk_size` and `settings.chunk_overlap`.
  2. **`process_document(document_id, file_path, filename)`**:
     - Wrapped in a try/except block for error handling.
     - Calls `pdf_service.extract_pages(file_path)` → list of `PageText`.
     - Calls `chunker.chunk_pages(pages)` → list of `Chunk`.
     - Calls `retriever.add_chunks(document_id, filename, chunks)` → embeds and stores in ChromaDB.
     - Calls `document_service.update_document(document_id, status="ready", page_count=len(pages))` → updates the database record.
     - **On error**: Calls `document_service.update_document(document_id, status="failed", error_msg=str(error))`.
  3. **`delete_document(document_id, file_path)`**:
     - Calls `retriever.delete_document(document_id)` → removes from ChromaDB.
     - Calls `Path(file_path).unlink()` → deletes the PDF file from disk.
- **Relationship to Other Files**: Called by `upload.py` (in background task) for processing, and by `documents.py` for deletion.
- **Important Implementation Details**:
  - The pipeline is the "controller" that sequences multiple operations. Each individual operation (PDF parsing, chunking, embedding) is handled by a separate service, keeping responsibilities clean.
  - Error handling updates the document status to "failed" with an error message, so the user can see what went wrong.
- **Edge Cases / Limitations**:
  - If `retriever.add_chunks()` succeeds but `document_service.update_document()` fails, the chunks are in ChromaDB but the document shows as "processing." This is an inconsistency.
  - The `delete_document` method does not catch errors (e.g., if the file was already deleted manually).
- **How to Extend It**: Add retry logic, add progress reporting (e.g., emit events after each step), add document type detection.
- **Learning Notes**: This is the **Facade pattern** — a single class provides a simplified interface to a complex subsystem (PDF parsing + chunking + embedding + indexing).

---

### File: `backend/app/rag/retriever.py`

- **Purpose**: Wraps ChromaDB to provide vector storage and semantic search capabilities.
- **Main Symbols**: `Retriever` (class), `add_chunks()`, `search()`, `delete_document()`, `healthcheck()`.
- **Dependencies**: ChromaDB, `EmbeddingService`.
- **How It Works** (step by step):
  1. **`__init__`**: Creates a ChromaDB `PersistentClient` (data saved to disk at `persist_directory`). Gets or creates a collection named `"rag_chunks"` with cosine distance as the similarity metric.
  2. **`add_chunks(document_id, filename, chunks)`**:
     - Extracts text from all chunks.
     - Calls `embedding_service.embed_texts(texts)` to generate vectors.
     - Builds metadata for each chunk: `{"doc_id": ..., "filename": ..., "page_number": ..., "chunk_index": ...}`.
     - Generates IDs: `"{document_id}_chunk_{i}"`.
     - Calls `collection.upsert(ids, embeddings, metadatas, documents)`.
  3. **`search(query, top_k, document_ids=None)`**:
     - Embeds the query text.
     - Builds an optional `where` filter for specific `doc_id` values.
     - Calls `collection.query(query_embeddings, n_results, where, include=["documents", "metadatas", "distances"])`.
     - Returns the raw results (a dict with `ids`, `documents`, `metadatas`, `distances`).
  4. **`delete_document(document_id)`**: Deletes all entries where `metadata.doc_id == document_id`.
  5. **`healthcheck()`**: Calls `collection.count()` — if ChromaDB is down, this will raise an exception.
- **Relationship to Other Files**: Used by `RAGPipeline` (add/delete chunks) and `ChatService` (search).
- **Important Implementation Details**:
  - `PersistentClient` saves data to the specified directory. Restarting the server retains all embeddings.
  - `upsert` (not `add`) is used to avoid duplicate entries if a document is reprocessed.
  - ChromaDB stores the original text in the `documents` field, so it can be returned with search results without a separate lookup.
- **Edge Cases / Limitations**:
  - ChromaDB's `PersistentClient` is single-process. For multi-process deployment, use ChromaDB's client-server mode.
  - No filtering by distance threshold — all top_k results are returned regardless of relevance. Low-quality matches could be filtered out with a distance cutoff.
- **How to Extend It**: Add distance threshold filtering, add metadata-based filtering (e.g., by date), add batch operations for large documents.
- **Learning Notes**: ChromaDB is an "embedding database" — it is optimized for storing vectors and finding the nearest neighbors. Under the hood, it uses algorithms like HNSW (Hierarchical Navigable Small World) for fast approximate nearest neighbor search.

---

### File: `backend/app/rag/prompt.py`

- **Purpose**: Constructs the prompt string that is sent to the LLM.
- **Main Symbols**: `SYSTEM_PROMPT` (constant string), `build_prompt()` (function).
- **Dependencies**: None (pure Python string formatting).
- **How It Works**:
  1. **`SYSTEM_PROMPT`**: A constant string instructing the LLM: "You are an enterprise assistant that answers only from the supplied context. If the context does not contain the answer, say so. Cite your sources."
  2. **`build_prompt(history, context, question)`**: Concatenates four sections:
     - `SYSTEM:` + the system prompt
     - `HISTORY:` + conversation history (previous Q&A turns)
     - `CONTEXT:` + the retrieved chunks (formatted with source and page info)
     - `QUESTION:` + the current user question
     Returns the full prompt as a single string.
- **Relationship to Other Files**: Called by `ChatService.answer()`.
- **Important Implementation Details**:
  - The system prompt is critical for RAG quality. It tells the LLM to stay grounded in the context and not make up information. Without it, the LLM might generate plausible-sounding but incorrect answers.
  - The context section formats each chunk with `[Source: filename | Page N]` headers, making it clear to the LLM where each piece of context came from.
- **Edge Cases / Limitations**:
  - The entire prompt (system + history + context + question) must fit within the LLM's context window. If there are too many chunks or too much history, the prompt may be truncated.
  - The prompt template is a simple string concatenation. For more complex prompts, consider using a templating engine like Jinja2.
- **How to Extend It**: Add few-shot examples, add output format instructions (e.g., "respond in bullet points"), add language preference.
- **Learning Notes**: Prompt engineering is the art of crafting effective prompts. Small changes to the system prompt can significantly affect the quality of LLM responses.

---

### File: `backend/app/services/chat_service.py`

- **Purpose**: Orchestrates the chat flow: retrieval → prompt → LLM → citations. Also manages conversation memory.
- **Main Symbols**: `SessionMemoryStore` (class), `ChatService` (class), `answer()`, `_load_llm()`, `_fallback_answer()`.
- **Dependencies**: `Retriever`, `Settings`, Prompt builder, LangChain (for Gemini), `collections.defaultdict`, `collections.deque`.
- **How It Works** (step by step):
  1. **`SessionMemoryStore`**:
     - Uses a `defaultdict(deque)` keyed by `session_id`.
     - Each deque has `maxlen = window_size * 2` (each turn has 2 entries: question + answer).
     - `add_turn(session_id, question, answer)`: Appends the question and answer to the deque.
     - `render(session_id)`: Formats the deque contents into a string: `"User: ...\nAssistant: ...\n"`.
     - `reset(session_id)`: Clears the deque for that session.
     - When the deque exceeds `maxlen`, the oldest entries are automatically dropped. This is the "sliding window" memory.
  2. **`ChatService.__init__`**: Takes `retriever`, `settings`, and `memory_store`. Sets `_llm = None` (lazy loading).
  3. **`_load_llm()`**: Imports `ChatGoogleGenerativeAI` from `langchain_google_genai` and creates an instance with the configured model name and API key. Only called once (lazy).
  4. **`answer(question, session_id, top_k)`**:
     - Calls `retriever.search(question, top_k)` to find relevant chunks.
     - Builds citations from the search results: extracts `document_name`, `page_number`, `chunk_preview` from each result.
     - **Deduplication**: Groups citations by `(document_name, page_number)`. If multiple chunks came from the same page, merges their previews with `"\n\n[...]\n\n"`.
     - Calls `memory_store.render(session_id)` to get conversation history.
     - Calls `build_prompt(history, context, question)` to construct the LLM prompt.
     - If the LLM is loaded (API key configured): calls `llm.invoke(prompt)` to get the answer.
     - If the LLM is not loaded: calls `_fallback_answer()`.
     - Calls `memory_store.add_turn(session_id, question, answer)` to save to memory.
     - Returns the answer and citations.
  5. **`_fallback_answer()`**: Returns a static string indicating that Gemini is not configured.
- **Relationship to Other Files**: Called by `chat.py` route. Uses `Retriever` for search, `prompt.py` for prompt building.
- **Important Implementation Details**:
  - The LLM is lazy-loaded: imported and instantiated only on first use. This avoids import errors at startup if `langchain_google_genai` is not installed or the API key is not set.
  - Citation deduplication prevents showing duplicate sources. The merge strategy uses `"\n\n[...]\n\n"` as a separator to indicate that multiple excerpts have been joined.
  - The `deque(maxlen=N)` is a brilliantly simple bounded buffer: when you append beyond maxlen, the oldest item is automatically discarded.
- **Edge Cases / Limitations**:
  - In-memory session storage is lost on server restart. For persistent memory, store sessions in Redis or the database.
  - The fallback answer is a hardcoded string. Consider returning the retrieved context even without an LLM, so users can at least see relevant chunks.
- **How to Extend It**: Add session persistence (Redis/database), add streaming responses, add retry logic for LLM calls.
- **Learning Notes**: The `defaultdict` from Python's `collections` module creates a new value (here, a `deque`) when you access a key that does not exist yet. This avoids `KeyError` exceptions.

---

### File: `backend/app/services/document_service.py`

- **Purpose**: Provides CRUD (Create, Read, Update, Delete) operations for document metadata in SQLite.
- **Main Symbols**: `DocumentService` (class), `create_document()`, `list_documents()`, `get_document()`, `update_document()`, `delete_document()`, `remove_file()`.
- **Dependencies**: SQLAlchemy session factory, `Document` model, `pathlib`.
- **How It Works** (step by step):
  1. **`__init__`**: Receives the SQLAlchemy `session_factory` and stores it.
  2. **`create_document(id, filename, file_path, file_size)`**: Creates a new `Document` object, adds it to the session, commits, and returns the created object.
  3. **`list_documents()`**: Queries all documents ordered by `uploaded_at` descending. Returns a list.
  4. **`get_document(document_id)`**: Queries a single document by primary key. Returns `None` if not found.
  5. **`update_document(document_id, **kwargs)`**: Retrieves the document, updates the specified fields using `setattr()`, commits. Accepts any keyword arguments matching `Document` fields.
  6. **`delete_document(document_id)`**: Retrieves and deletes the document from the database.
  7. **`remove_file(file_path)`**: Deletes a file from the filesystem using `pathlib.Path.unlink(missing_ok=True)`.
- **Relationship to Other Files**: Used by `RAGPipeline` (create, update), `documents.py` route (list, get, delete).
- **Important Implementation Details**:
  - Each operation creates a new session from the factory, uses it, and closes it (via context manager or manual close). This follows the "session-per-request" pattern.
  - `remove_file` uses `missing_ok=True` to avoid errors if the file has already been deleted.
- **Edge Cases / Limitations**:
  - No transaction spanning multiple service calls. If `delete_document()` succeeds but a subsequent step fails, the DB deletion cannot be rolled back.
  - No pagination on `list_documents()` — returns all documents. For large datasets, add `offset`/`limit` parameters.
- **How to Extend It**: Add pagination, add search/filtering, add soft delete (mark as deleted instead of removing).
- **Learning Notes**: CRUD stands for Create, Read, Update, Delete — the four basic operations on any persistent data store.

---

### File: `backend/app/services/embedding_service.py`

- **Purpose**: Generates text embeddings using the SentenceTransformers library.
- **Main Symbols**: `EmbeddingService` (class), `_load()`, `embed_texts()`, `embed_query()`.
- **Dependencies**: `sentence_transformers.SentenceTransformer`, `threading.Lock`.
- **How It Works** (step by step):
  1. **`__init__`**: Stores the `model_name` (default `"sentence-transformers/all-MiniLM-L6-v2"`). Sets `_model = None` and creates a `threading.Lock`.
  2. **`_load()`**: Implements double-checked locking:
     - First checks if `_model` is already loaded (without locking — fast path).
     - If not loaded, acquires the lock.
     - Checks again inside the lock (another thread may have loaded it while waiting).
     - If still not loaded, creates the `SentenceTransformer` instance.
     This ensures the model is loaded exactly once, even under concurrent access.
  3. **`embed_texts(texts)`**: Calls `_load()` to ensure the model is ready, then calls `model.encode(texts, normalize_embeddings=True)`. Returns a list of lists of `float32` values.
  4. **`embed_query(text)`**: Wraps `embed_texts([text])` and returns the first (only) result.
- **Relationship to Other Files**: Used by `Retriever` (for embedding chunks and queries).
- **Important Implementation Details**:
  - `normalize_embeddings=True` ensures each vector has unit length (L2 norm = 1). This makes cosine similarity equivalent to dot product, which is faster to compute.
  - The model is ~80MB and takes a few seconds to load. Lazy loading keeps server startup fast.
  - Double-checked locking is a threading pattern that avoids acquiring a lock on every call after initialization.
- **Edge Cases / Limitations**:
  - The model runs on CPU by default. For GPU acceleration, install PyTorch with CUDA support.
  - The `all-MiniLM-L6-v2` model produces 384-dimensional embeddings. Switching models may change the dimension, requiring re-embedding all existing documents.
- **How to Extend It**: Add GPU support, add batch size configuration, add model caching/preloading.
- **Learning Notes**: SentenceTransformers is built on top of Hugging Face Transformers and PyTorch. The model is downloaded from the Hugging Face Hub the first time it is used and cached locally.

---

### File: `backend/app/services/pdf_service.py`

- **Purpose**: Extracts text from PDF files page by page.
- **Main Symbols**: `PageText` (dataclass), `PDFService` (class), `extract_pages()`.
- **Dependencies**: `fitz` (PyMuPDF).
- **How It Works**:
  1. **`PageText` dataclass**: A simple container with `page_number` (int) and `text` (str).
  2. **`extract_pages(file_path)`**:
     - Opens the PDF with `fitz.open(file_path)`.
     - Iterates over each page in the document.
     - Calls `page.get_text()` to extract the page's text content.
     - Creates a `PageText` object with 1-based page number (`i + 1`) and the extracted text.
     - Returns the list of `PageText` objects.
- **Relationship to Other Files**: Used by `RAGPipeline.process_document()`.
- **Important Implementation Details**:
  - Page numbers are 1-indexed (human-friendly) even though `fitz` uses 0-indexed iteration.
  - `fitz` extracts text in reading order. For complex layouts, the order may not be perfect.
  - The file is opened and closed within the method (resource cleanup).
- **Edge Cases / Limitations**:
  - Scanned PDFs (images of text) return empty text — no OCR is performed.
  - Password-protected PDFs may fail to open.
  - Very large PDFs may use significant memory.
- **How to Extend It**: Add OCR support (using `pytesseract` or `fitz`'s own OCR capabilities), add table extraction, handle encrypted PDFs.
- **Learning Notes**: PyMuPDF (imported as `fitz` for historical reasons — it was originally based on the MuPDF C library by Artifex) is one of the fastest PDF parsing libraries in Python.

---

### File: `backend/app/utils/logger.py`

- **Purpose**: Configures structured JSON logging for the application.
- **Main Symbols**: `JsonFormatter` (class), `configure_logging()` (function).
- **Dependencies**: Python's `logging` module, `json`.
- **How It Works**:
  1. **`JsonFormatter(logging.Formatter)`**: A custom log formatter that outputs log records as JSON objects:
     ```json
     {"level": "INFO", "logger": "app.main", "message": "Server started", "timestamp": "2026-06-11T12:00:00"}
     ```
     If the log record includes exception info, it is added as an `"exception"` field.
  2. **`configure_logging(level)`**: Creates a `StreamHandler` (writes to stdout), sets the `JsonFormatter` on it, and attaches it to the root logger with the specified level.
- **Relationship to Other Files**: Called by `main.py` during startup.
- **Important Implementation Details**:
  - JSON logging is standard in production environments because log aggregation tools (ELK, Datadog, CloudWatch) can parse JSON natively, enabling searching and filtering by field.
  - The formatter outputs to stdout (not files). In containerized environments, stdout logs are captured by the container runtime.
- **Edge Cases / Limitations**: No log rotation (not needed for stdout in containers). For file-based logging, add rotation via `RotatingFileHandler`.
- **How to Extend It**: Add request ID to log context (for tracing), add custom fields, add log level per module.
- **Learning Notes**: Python's `logging` module follows the `Logger → Handler → Formatter` chain: a Logger generates log records, a Handler sends them somewhere (stdout, file, network), and a Formatter controls the output format.

---

### File: `backend/app/utils/validators.py`

- **Purpose**: Validates uploaded PDF files before processing.
- **Main Symbols**: `validate_pdf_upload()` (async function).
- **Dependencies**: FastAPI's `UploadFile` and `HTTPException`.
- **How It Works** (step by step):
  1. **Content type check**: Verifies `file.content_type == "application/pdf"`. If not, raises HTTP 400.
  2. **Extension check**: Verifies `file.filename` ends with `.pdf` (case-insensitive). If not, raises HTTP 400.
  3. **Size check**: Reads the file in chunks, counting total bytes. If total exceeds `max_bytes`, raises HTTP 413 (Payload Too Large).
  4. **File rewind**: Calls `await file.seek(0)` to reset the file pointer to the beginning. This is crucial — after reading the file to check its size, the pointer is at the end. Without rewinding, subsequent code would read zero bytes.
- **Relationship to Other Files**: Called by `upload.py` before saving the file.
- **Important Implementation Details**:
  - Reading in chunks (not `file.read()` all at once) prevents memory exhaustion from extremely large files. Even a 10GB file only uses a small buffer at a time.
  - The `content_type` header can be spoofed by the client. For true security, also check the file's magic bytes (the first few bytes that identify the file format).
- **Edge Cases / Limitations**:
  - An empty file (0 bytes) passes the content type and extension checks but will fail during PDF parsing (no pages to extract).
  - The `content_type` is self-reported by the client and can be incorrect.
- **How to Extend It**: Add magic byte validation, add virus scanning, add support for multiple file types.
- **Learning Notes**: File validation is a security concern. Never trust user-uploaded files — always validate type, size, and content before processing.

---

### File: `backend/tests/conftest.py`

- **Purpose**: Defines shared test fixtures and fake (mock) services used across all test files.
- **Main Symbols**: `FakeRetriever`, `FakePipeline`, `FakeChatService` (fake classes), `settings`, `session_factory`, `document_service`, `retriever`, `pipeline`, `chat_service`, `test_app`, `client` (pytest fixtures).
- **Dependencies**: pytest, FastAPI's TestClient, httpx (or Starlette's test client).
- **How It Works**:
  1. **Fake classes**: Simplified implementations of real services that return predetermined data:
     - `FakeRetriever`: Returns hardcoded search results (no ChromaDB needed).
     - `FakePipeline`: Records calls without actually processing documents.
     - `FakeChatService`: Returns a hardcoded answer without calling an LLM.
  2. **Fixtures**: pytest fixtures that create instances of services for testing:
     - `settings`: Creates a `Settings` instance with test-appropriate defaults.
     - `session_factory`: Creates an in-memory SQLite session factory (`sqlite:///:memory:`).
     - `document_service`: Creates a real `DocumentService` with the in-memory database.
     - `retriever`, `pipeline`, `chat_service`: Create fake instances.
     - `test_app`: Creates a FastAPI app with all services wired up, but using fakes for external dependencies.
     - `client`: Creates a TestClient that can make HTTP requests to the test app without a real server.
- **Relationship to Other Files**: Imported automatically by pytest for all test files in the same directory.
- **Important Implementation Details**:
  - In-memory SQLite (`sqlite:///:memory:`) creates a fresh database for each test, ensuring test isolation.
  - `conftest.py` is a pytest convention — fixtures defined here are automatically available to all test files in the same directory.
- **Edge Cases / Limitations**: Fake services may not perfectly replicate real service behavior. Integration tests with real services are also valuable.
- **How to Extend It**: Add more fakes as new services are added.
- **Learning Notes**: A **fixture** in pytest is a function that provides test data or test infrastructure. The `@pytest.fixture` decorator marks a function as a fixture. Tests can request fixtures by name as function parameters.

---

### 7.3 Frontend Files

---

### File: `frontend/Dockerfile`

- **Purpose**: Builds the frontend for production and serves it with nginx.
- **Main Symbols**: Multi-stage build: build stage (Vite) + serve stage (nginx).
- **Dependencies**: Node.js, Vite, nginx.
- **How It Works** (step by step):
  1. **Build stage**: Uses a Node.js image, copies `package.json`, installs dependencies (`npm install`), copies source code, runs `npm run build` (Vite produces static files in `dist/`).
  2. **Serve stage**: Uses an nginx image, copies the `dist/` folder from the build stage into nginx's web root, exposes port 5173 (or 80).
- **Relationship to Other Files**: Referenced by `docker-compose.yml`.
- **Important Implementation Details**: Multi-stage builds keep the final image small — it contains only the built static files and nginx, not the Node.js runtime or source code.
- **Edge Cases / Limitations**: nginx needs to be configured to route all paths to `index.html` for single-page app (SPA) routing to work.
- **How to Extend It**: Add gzip compression, add caching headers, add SSL termination.
- **Learning Notes**: A multi-stage Docker build uses multiple `FROM` instructions. Each stage can copy artifacts from a previous stage, discarding everything else.

---

### File: `frontend/index.html`

- **Purpose**: The HTML shell that React mounts into.
- **Main Symbols**: `<div id="root"></div>`, `<script type="module" src="/src/main.tsx"></script>`.
- **Dependencies**: None (static HTML).
- **How It Works**: The browser loads this file, which has an empty `<div id="root">`. The `<script>` tag loads the React application (`main.tsx`), which renders the entire UI inside that div.
- **Relationship to Other Files**: Points to `src/main.tsx` as the entry point.
- **Important Implementation Details**: `type="module"` enables ES module syntax (import/export) in the script.
- **Edge Cases / Limitations**: If JavaScript is disabled, the page will be blank.
- **How to Extend It**: Add meta tags (SEO, viewport), add favicon, add a loading spinner for the initial load.
- **Learning Notes**: In a single-page application (SPA), there is only one HTML file. JavaScript handles all page navigation by dynamically updating the DOM.

---

### File: `frontend/package.json`

- **Purpose**: Defines Node.js project metadata, dependencies, and scripts.
- **Main Symbols**: `dependencies`, `devDependencies`, `scripts` (dev, build, test, preview).
- **Dependencies**: npm (Node.js package manager).
- **How It Works**: `npm install` reads this file and installs all listed packages into `node_modules/`. Scripts define common commands: `npm run dev` starts the development server, `npm run build` creates a production build.
- **Relationship to Other Files**: Used by the Dockerfile, referenced by Vite.
- **Important Implementation Details**: `dependencies` are needed at runtime, `devDependencies` are only needed during development (testing, building).
- **Edge Cases / Limitations**: `package-lock.json` (auto-generated) should also be committed for reproducible installs.
- **How to Extend It**: Add new packages with `npm install <package>`.
- **Learning Notes**: `package.json` is the equivalent of Python's `requirements.txt` but with more features (scripts, metadata, version ranges).

---

### File: `frontend/vite.config.ts`

- **Purpose**: Configures the Vite development server and build process.
- **Main Symbols**: `defineConfig()` with plugins and server options.
- **Dependencies**: Vite, React plugin.
- **How It Works**: Exports a configuration object that Vite reads. Typically includes the React plugin (for JSX support), server port configuration, and proxy settings (to forward API calls to the backend during development).
- **Relationship to Other Files**: Used by Vite when running `npm run dev` or `npm run build`.
- **Important Implementation Details**: In development, Vite may proxy `/api` requests to `http://localhost:8000` to avoid CORS issues.
- **Edge Cases / Limitations**: The proxy only works in development. In production, nginx or a reverse proxy handles routing.
- **How to Extend It**: Add path aliases, add environment variable configuration, add build optimization settings.
- **Learning Notes**: Vite uses native ES modules during development (no bundling), which makes it extremely fast. Only production builds are bundled.

---

### File: `frontend/tailwind.config.js`

- **Purpose**: Configures Tailwind CSS (which files to scan for class usage, custom theme extensions).
- **Main Symbols**: `content` (file globs), `theme` (customizations), `plugins`.
- **Dependencies**: Tailwind CSS.
- **How It Works**: Tailwind scans the files listed in `content` for class names. Only the classes actually used appear in the final CSS (this is called "tree-shaking" or "purging"). Unused classes are removed, keeping the CSS bundle small.
- **Relationship to Other Files**: Used by Tailwind during the build process.
- **Important Implementation Details**: The `content` array must include all files that use Tailwind classes (`.tsx`, `.ts`, `.html`). Missing a file means its classes will be purged.
- **Edge Cases / Limitations**: Dynamically constructed class names (e.g., `bg-${color}-500`) will be purged because Tailwind cannot detect them. Use complete class names instead.
- **How to Extend It**: Add custom colors, fonts, spacing, breakpoints, and plugins.
- **Learning Notes**: Tailwind CSS generates a massive CSS file with every possible utility class, then removes unused ones at build time. The result is a tiny, optimized CSS file.

---

### File: `frontend/tsconfig.json`

- **Purpose**: Configures the TypeScript compiler options.
- **Main Symbols**: `compilerOptions` (target, module, strict, JSX, etc.), `include` (files to compile).
- **Dependencies**: TypeScript.
- **How It Works**: TypeScript reads this file to know how to check types and compile `.ts` and `.tsx` files. Key options include `strict: true` (enables all strict type checks), `jsx: "react-jsx"` (enables JSX syntax), and `target: "ES2020"` (output modern JavaScript).
- **Relationship to Other Files**: Affects all `.ts` and `.tsx` files in the `src/` directory.
- **Important Implementation Details**: `strict: true` is highly recommended — it catches many potential bugs. Disabling it makes TypeScript less useful.
- **Edge Cases / Limitations**: Very strict settings may require extra type annotations. This is a feature, not a bug.
- **How to Extend It**: Add path aliases, adjust strictness levels, add new compiler plugins.
- **Learning Notes**: TypeScript is a *compile-time* tool. At runtime, the browser sees only JavaScript (TypeScript is stripped away during the build).

---

### File: `frontend/src/main.tsx`

- **Purpose**: The entry point of the React application.
- **Main Symbols**: `ReactDOM.createRoot()`, `<App />`, `<React.StrictMode>`.
- **Dependencies**: React, ReactDOM, `App` component.
- **How It Works**:
  1. Finds the DOM element with `id="root"` (in `index.html`).
  2. Creates a React root on that element.
  3. Renders `<App />` inside `<React.StrictMode>`.
- **Relationship to Other Files**: Referenced by `index.html`. Imports `App.tsx` and `index.css`.
- **Important Implementation Details**: `React.StrictMode` is a development-only wrapper that helps find problems in your app. It renders components twice (in development) to detect side effects, and warns about deprecated APIs.
- **Edge Cases / Limitations**: StrictMode's double-rendering can cause confusion during debugging. It does not affect production builds.
- **How to Extend It**: Add providers (e.g., `ThemeProvider`, `AuthProvider`) around `<App />`.
- **Learning Notes**: `createRoot` is the React 18+ way to initialize an app. Older React versions used `ReactDOM.render()`.

---

### File: `frontend/src/index.css`

- **Purpose**: Global CSS styles including Tailwind directives, font configuration, and custom styles.
- **Main Symbols**: `@tailwind base`, `@tailwind components`, `@tailwind utilities`, custom properties.
- **Dependencies**: Tailwind CSS.
- **How It Works**:
  1. `@tailwind base` — injects Tailwind's base styles (CSS resets, default typography).
  2. `@tailwind components` — injects Tailwind's component classes.
  3. `@tailwind utilities` — injects Tailwind's utility classes.
  4. Custom styles set dark color scheme, IBM Plex Sans font, and custom scrollbar appearances.
- **Relationship to Other Files**: Imported by `main.tsx` to be loaded globally.
- **Important Implementation Details**: The order of `@tailwind` directives matters: base → components → utilities ensures proper CSS specificity.
- **Edge Cases / Limitations**: Custom scrollbar styles may not work in all browsers (Firefox has different syntax).
- **How to Extend It**: Add custom @layer rules, add CSS variables, add animations.
- **Learning Notes**: Tailwind's three layers (base, components, utilities) map to different CSS specificity levels, ensuring utilities always win over base styles.

---

### File: `frontend/src/types/index.ts`

- **Purpose**: Defines TypeScript interfaces for all data shapes used in the frontend.
- **Main Symbols**: `DocumentItem`, `DocumentDetail`, `Citation`, `Message`, `ChatRequest`, `ChatResponse`, `UploadResponse`.
- **Dependencies**: None.
- **How It Works**: Each interface defines the shape of an object:
  - `DocumentItem`: `id`, `filename`, `page_count`, `status`, `uploaded_at`, `file_size_bytes`
  - `DocumentDetail`: extends `DocumentItem` with `error_msg`, `updated_at`
  - `Citation`: `document_name`, `page_number`, `chunk_preview`
  - `Message`: `id`, `role` ("user" | "assistant"), `content`, `timestamp`, `citations?`, `isPending?`
  - `ChatRequest`: `question`, `session_id`, `top_k?`
  - `ChatResponse`: `answer`, `citations`, `session_id`, `sources_used`
  - `UploadResponse`: `document_id`, `filename`, `status`, `message`
- **Relationship to Other Files**: Imported by every other frontend file.
- **Important Implementation Details**: These interfaces mirror the backend Pydantic models. Keeping them in sync is essential — if the backend changes a response shape, the frontend types must be updated too.
- **Edge Cases / Limitations**: TypeScript interfaces are compile-time only. At runtime, there is no validation. If the backend sends unexpected data, TypeScript will not catch it.
- **How to Extend It**: Add new interfaces as new features are added. Consider using `zod` for runtime validation.
- **Learning Notes**: An **interface** in TypeScript is a way to define the shape of an object. It is similar to a Pydantic model in Python but only exists at compile time.

---

### File: `frontend/src/api/client.ts`

- **Purpose**: Provides typed functions for all HTTP calls to the backend API.
- **Main Symbols**: `API_BASE_URL`, `parseJson()`, `fetchDocuments()`, `fetchDocument()`, `deleteDocument()`, `uploadDocument()`, `sendChat()`.
- **Dependencies**: Browser `fetch` API, `XMLHttpRequest`, Types.
- **How It Works** (step by step):
  1. **`API_BASE_URL`**: Reads from `import.meta.env.VITE_API_BASE_URL` or defaults to `http://localhost:8000/api/v1`.
  2. **`parseJson<T>(response)`**: Checks `response.ok`, parses JSON, throws an error with the status and error message if the response is not OK.
  3. **`fetchDocuments()`**: `GET /documents` → returns `DocumentItem[]`.
  4. **`fetchDocument(id)`**: `GET /documents/{id}` → returns `DocumentDetail`.
  5. **`deleteDocument(id)`**: `DELETE /documents/{id}` → returns `DeleteResponse`.
  6. **`uploadDocument(file, onProgress)`**: Uses `XMLHttpRequest` instead of `fetch`. This is because `fetch` does not support upload progress events. The `onProgress` callback receives a 0–100 percentage value. Returns a `Promise<UploadResponse>`.
  7. **`sendChat(payload)`**: `POST /chat` with JSON body → returns `ChatResponse`.
- **Relationship to Other Files**: Used by `useChat` and `useDocuments` hooks.
- **Important Implementation Details**:
  - `XMLHttpRequest` is used for uploads because the `fetch` API (as of 2026) still does not support upload progress tracking in all browsers. `xhr.upload.onprogress` provides real-time progress.
  - The `parseJson` function is generic (`<T>`) — the caller specifies the expected return type for type safety.
  - Error handling extracts the `detail` field from FastAPI error responses (which FastAPI uses by convention).
- **Edge Cases / Limitations**: No retry logic. If a request fails due to a network glitch, it is not retried automatically.
- **How to Extend It**: Add retry logic (with exponential backoff), add request interceptors (for auth tokens), add request cancellation.
- **Learning Notes**: `XMLHttpRequest` (XHR) is the older way to make HTTP requests in JavaScript (before `fetch` existed). It is still useful for features that `fetch` does not support, like upload progress.

---

### File: `frontend/src/hooks/useChat.ts`

- **Purpose**: Custom React hook that manages chat state and actions.
- **Main Symbols**: `createSessionId()`, `createPendingMessage()`, `useChat()` hook.
- **Dependencies**: React hooks, API client, Types.
- **How It Works** (step by step):
  1. **`createSessionId()`**: Calls `crypto.randomUUID()` to generate a unique session ID.
  2. **`createPendingMessage()`**: Creates a `Message` object with `role: "assistant"`, `isPending: true`, empty content — displayed as loading dots.
  3. **`useChat()` hook**: Manages:
     - `messages: Message[]` — the list of chat messages.
     - `sessionId: string` — persisted in `sessionStorage` (survives page refreshes within the same tab).
     - `sending: boolean` — true while waiting for a response.
     - `error: string | null` — the latest error message.
  4. **`sendMessage(question)`**:
     - Sets `sending = true`.
     - Appends a user message and a pending (loading) message to `messages`.
     - Calls `sendChat({ question, session_id: sessionId })`.
     - On success: replaces the pending message with the real response (including citations).
     - On error: replaces the pending message with an error message.
     - Sets `sending = false`.
  5. **`clearConversation()`**: Resets `messages` to empty, generates a new session ID.
- **Relationship to Other Files**: Used by `App.tsx`. Calls `sendChat()` from the API client.
- **Important Implementation Details**:
  - `sessionStorage` persists the session ID across page refreshes but not across tabs or browser restarts. This means a user can continue a conversation after accidentally refreshing the page.
  - The pending message pattern provides instant visual feedback: the user sees their message appear immediately, followed by loading dots that are replaced with the actual answer.
- **Edge Cases / Limitations**: If the user sends another message while one is pending, both will be in flight simultaneously. The `sending` flag can prevent this in the UI by disabling the Send button.
- **How to Extend It**: Add message editing, add message deletion, add streaming response support.
- **Learning Notes**: Custom hooks are just functions that use React's built-in hooks. They let you extract and reuse stateful logic across components.

---

### File: `frontend/src/hooks/useDocuments.ts`

- **Purpose**: Custom React hook that manages document state, upload, and status polling.
- **Main Symbols**: `useDocuments()` hook.
- **Dependencies**: React hooks, API client, Types.
- **How It Works** (step by step):
  1. **State**: `documents: DocumentItem[]`, `loading: boolean`, `uploadProgress: number`, `uploading: boolean`, `error: string | null`.
  2. **`refresh()`**: Calls `fetchDocuments()` and updates the `documents` state.
  3. **Polling `useEffect`**: If any document has `status === "processing"`, sets up a 3-second interval that calls `refresh()`. When all documents are done (ready or failed), the interval is cleared. This automatically stops polling when there is nothing to poll for.
  4. **`upload(file)`**: Sets `uploading = true`, calls `uploadDocument(file, onProgress)` with a progress callback, then calls `refresh()` to show the new document. Sets `uploading = false` when done.
  5. **`remove(documentId)`**: Calls `deleteDocument(documentId)`, then calls `refresh()` to update the list.
- **Relationship to Other Files**: Used by `App.tsx`. Calls API client functions.
- **Important Implementation Details**:
  - The polling mechanism is elegant: it is driven by the data itself (presence of "processing" documents), not by external triggers. This means polling starts automatically when needed and stops automatically when done.
  - The `useEffect` cleanup function (`return () => clearInterval(...)`) prevents memory leaks when the component unmounts.
- **Edge Cases / Limitations**: Polling every 3 seconds creates network traffic. For large numbers of users, consider server-sent events (SSE) or WebSockets instead.
- **How to Extend It**: Add pagination, add search/filtering, replace polling with WebSocket/SSE updates.
- **Learning Notes**: `useEffect` with a dependency array is how React handles side effects (things that happen "outside" React, like API calls, timers, and DOM manipulation). The cleanup function runs when the effect re-runs or the component unmounts.

---

### File: `frontend/src/pages/App.tsx`

- **Purpose**: The root page component that wires together all state and UI.
- **Main Symbols**: `App` (component).
- **Dependencies**: `useDocuments`, `useChat`, all UI components.
- **How It Works**:
  1. Calls `useDocuments()` to get document state and actions.
  2. Calls `useChat()` to get chat state and actions.
  3. Manages local UI state: `sidebarOpen` (mobile toggle), `activeDocumentId` (selected document).
  4. Defines callback functions: `handleUpload`, `handleDelete`, `handleDocumentSelect`.
  5. Renders the layout:
     - `<Sidebar>` on the left: document list, upload zone
     - `<ChatWindow>` in the center: message list, input form
     - `<ErrorToast>` at the bottom-right: error notifications
     - Selected document indicator
- **Relationship to Other Files**: Top-level component. Renders all other components. Imported by `main.tsx`.
- **Important Implementation Details**: This component is the "orchestrator" — it does not contain business logic itself. Instead, it delegates to hooks for state management and to components for rendering. This separation makes the app easier to test and maintain.
- **Edge Cases / Limitations**: All state is in memory. Refreshing the page loses chat messages (but keeps the session ID in sessionStorage).
- **How to Extend It**: Add routing (React Router) for multiple pages, add authentication, add settings panel.
- **Learning Notes**: The pattern of lifting state up to a common ancestor and passing it down via props is called "lifting state up." It is a fundamental React pattern for sharing state between sibling components.

---

### File: `frontend/src/components/Sidebar.tsx`

- **Purpose**: Displays the document library and upload area in a side panel.
- **Main Symbols**: `Sidebar` (component).
- **Dependencies**: Props (documents, callbacks), `UploadZone` component.
- **How It Works**:
  1. Renders an app title/branding card at the top.
  2. Renders the `UploadZone` component for file uploads.
  3. Renders a "Library" section listing all documents as cards.
  4. Each document card shows: filename, page count, file size, status badge (color-coded: green=ready, yellow=processing, red=failed), upload date, delete button.
  5. Mobile responsive: slides in/out with a toggle button.
- **Relationship to Other Files**: Rendered by `App.tsx`. Renders `UploadZone`.
- **Important Implementation Details**:
  - Status badges use Tailwind utility classes for coloring (e.g., `bg-green-500` for "ready").
  - The delete button calls the `onDelete` callback passed from `App.tsx`.
  - Mobile animation uses CSS transitions or Tailwind's `translate-x` utilities.
- **Edge Cases / Limitations**: With many documents, the list can become long. Add pagination or virtual scrolling for large libraries.
- **How to Extend It**: Add search bar, add sort options, add document detail view, add batch operations.
- **Learning Notes**: The sidebar pattern (fixed panel on the left) is one of the most common UI layouts for dashboard-style applications.

---

### File: `frontend/src/components/UploadZone.tsx`

- **Purpose**: A drag-and-drop area for uploading PDF files.
- **Main Symbols**: `UploadZone` (component).
- **Dependencies**: Props (onUpload, uploading, uploadProgress), React hooks.
- **How It Works**:
  1. Renders a dashed-border zone with an icon and instructions.
  2. Listens for `dragover` and `drop` events on the zone.
  3. On drop: validates the file is a PDF (client-side), calls `onUpload(file)`.
  4. Also has a hidden `<input type="file">` for click-to-select.
  5. During upload: shows a progress bar based on `uploadProgress` (0–100).
- **Relationship to Other Files**: Rendered by `Sidebar.tsx`. Calls the `onUpload` callback from `App.tsx` → `useDocuments.upload()`.
- **Important Implementation Details**:
  - `e.preventDefault()` on `dragover` and `drop` is essential — without it, the browser would try to navigate to the dropped file.
  - Client-side PDF validation is a UX optimization (instant feedback). The server validates again for security.
  - The progress bar width is set with an inline style: `style={{ width: `${uploadProgress}%` }}`.
- **Edge Cases / Limitations**: Does not support multiple file uploads. To add this, accept multiple files from the drop event and upload them sequentially.
- **How to Extend It**: Add multi-file upload, add file type icons, add upload history.
- **Learning Notes**: Drag-and-drop in HTML uses four events: `dragenter`, `dragover`, `dragleave`, and `drop`. You must call `preventDefault()` on `dragover` to allow dropping.

---

### File: `frontend/src/components/ChatWindow.tsx`

- **Purpose**: The main chat interface with message list and input form.
- **Main Symbols**: `ChatWindow` (component).
- **Dependencies**: Props (messages, onSendMessage, onClearConversation, sending), `MessageBubble` component.
- **How It Works**:
  1. **Header**: Shows "Chat" title and a "Clear Conversation" button.
  2. **Message list**: Maps `messages` array to `MessageBubble` components. Uses `useRef` and `useEffect` to auto-scroll to the bottom when new messages arrive.
  3. **Empty state**: When there are no messages, shows a placeholder with instructions.
  4. **Input form**: A text input and Send button. On submit, calls `onSendMessage(text)` and clears the input. The Send button is disabled while `sending` is true.
- **Relationship to Other Files**: Rendered by `App.tsx`. Renders `MessageBubble`.
- **Important Implementation Details**:
  - Auto-scroll uses `messagesEndRef.current.scrollIntoView({ behavior: "smooth" })` to smoothly scroll to a hidden div at the bottom of the message list.
  - The form uses `onSubmit` with `e.preventDefault()` to prevent page refresh (default form behavior).
- **Edge Cases / Limitations**: Long messages may take up the entire viewport. Consider adding a max-height with scroll.
- **How to Extend It**: Add message timestamps, add markdown rendering for answers, add code highlighting.
- **Learning Notes**: `useRef` creates a "ref" — a mutable reference to a DOM element. Unlike state, changing a ref does not trigger a re-render. It is perfect for imperative DOM manipulation like scrolling.

---

### File: `frontend/src/components/MessageBubble.tsx`

- **Purpose**: Renders a single chat message with appropriate styling based on role.
- **Main Symbols**: `MessageBubble` (component).
- **Dependencies**: Props (message), `CitationCard`, `LoadingDots`.
- **How It Works**:
  1. **User messages**: Aligned to the right, dark background, light text.
  2. **Assistant messages**: Aligned to the left, light background, dark text.
  3. Shows the role label ("You" or "Assistant") and timestamp.
  4. If `message.isPending` is true: shows `<LoadingDots />` instead of content.
  5. If the message has citations: maps each citation to a `<CitationCard />`.
- **Relationship to Other Files**: Rendered by `ChatWindow.tsx`. Renders `CitationCard` and `LoadingDots`.
- **Important Implementation Details**: The alignment is achieved with Tailwind's `self-end` (right) and `self-start` (left) classes on flex items.
- **Edge Cases / Limitations**: Very long messages without spaces will overflow. Add `break-words` class to handle this.
- **How to Extend It**: Add message actions (copy, regenerate), add markdown rendering, add avatar icons.
- **Learning Notes**: Conditional rendering in React is done with `&&` or ternary operators: `{isPending ? <LoadingDots /> : <p>{content}</p>}`.

---

### File: `frontend/src/components/CitationCard.tsx`

- **Purpose**: A collapsible card showing a source citation with expandable preview text.
- **Main Symbols**: `CitationCard` (component).
- **Dependencies**: Props (citation, index), React `useState`.
- **How It Works**:
  1. Renders a card with "Source N" header, document name, and page number.
  2. Has a "Show/Hide" toggle button.
  3. When expanded: shows the `chunk_preview` text (the actual text from the document).
  4. Uses `useState` to toggle the expanded state.
- **Relationship to Other Files**: Rendered by `MessageBubble.tsx`.
- **Important Implementation Details**: The `index` prop is used for the "Source N" label (e.g., "Source 1", "Source 2").
- **Edge Cases / Limitations**: Very long chunk previews may dominate the screen. Consider adding a max-height with scroll.
- **How to Extend It**: Add a "go to document" link, add text highlighting for the query terms.
- **Learning Notes**: Collapsible UI patterns use a boolean state variable (`isExpanded`) that controls whether a section is rendered or hidden.

---

### File: `frontend/src/components/ErrorToast.tsx`

- **Purpose**: Displays error notifications as a toast in the bottom-right corner.
- **Main Symbols**: `ErrorToast` (component).
- **Dependencies**: Props (error, onDismiss).
- **How It Works**:
  1. If `error` is null or undefined, returns `null` (renders nothing).
  2. Otherwise, renders a fixed-position div with the error message and a dismiss (×) button.
  3. Clicking the dismiss button calls `onDismiss()`.
- **Relationship to Other Files**: Rendered by `App.tsx`.
- **Important Implementation Details**: `position: fixed` ensures the toast stays visible even when scrolling.
- **Edge Cases / Limitations**: Only shows one error at a time. For multiple errors, use a toast queue.
- **How to Extend It**: Add auto-dismiss (setTimeout), add different severity levels (warning, info), add animation.
- **Learning Notes**: The "toast" pattern (a small notification that slides in and disappears) is one of the most common UI feedback mechanisms.

---

### File: `frontend/src/components/LoadingDots.tsx`

- **Purpose**: Animated loading indicator (three bouncing dots).
- **Main Symbols**: `LoadingDots` (component).
- **Dependencies**: None (pure CSS animation with Tailwind).
- **How It Works**: Renders three `<span>` elements styled as cyan dots. Each dot has a CSS animation with staggered `animation-delay` values (0s, 0.2s, 0.4s), creating a wave-like bouncing effect.
- **Relationship to Other Files**: Rendered by `MessageBubble.tsx` when a message is pending.
- **Important Implementation Details**: The animation is defined in CSS (or Tailwind's `animate-bounce` class) with staggered delays applied via inline styles.
- **Edge Cases / Limitations**: None — this is a purely decorative component.
- **How to Extend It**: Change the animation (pulsing, rotating), change colors, add a "Thinking..." text label.
- **Learning Notes**: CSS animations with `animation-delay` are a simple way to create staggered effects. The `@keyframes` rule defines the animation, and each element starts at a different delay.

---

### File: `frontend/src/test/setup.ts`

- **Purpose**: Configures the test environment for frontend tests.
- **Main Symbols**: Setup functions and global mocks.
- **Dependencies**: Testing library (`@testing-library/jest-dom`, Vitest).
- **How It Works**: This file runs before all tests. It typically sets up global mocks (e.g., `fetch`), extends matchers (e.g., `toBeInTheDocument()`), and configures any test-specific global state.
- **Relationship to Other Files**: Referenced in `vite.config.ts` as the test setup file.
- **Important Implementation Details**: Matches should be extended before tests run, or assertions like `.toBeInTheDocument()` will not be available.
- **Edge Cases / Limitations**: Global mocks apply to all tests — be careful not to leak state between tests.
- **How to Extend It**: Add more global mocks, add custom matchers.
- **Learning Notes**: Test setup files run once before all tests in the suite. They are the place for global configuration that all tests need.

---

### File: `frontend/src/api/client.test.ts`

- **Purpose**: Tests the API client functions.
- **Main Symbols**: Test suites for `fetchDocuments`, `sendChat`, `uploadDocument`, `parseJson`.
- **Dependencies**: Vitest, mock fetch.
- **How It Works**: Mocks the global `fetch` function and `XMLHttpRequest`, then verifies that each API client function makes the correct HTTP request with the correct parameters and handles responses/errors appropriately.
- **Relationship to Other Files**: Tests `api/client.ts`.
- **Important Implementation Details**: Testing the API client ensures that the contract between frontend and backend is maintained. If someone changes a URL or HTTP method, these tests will catch it.
- **Edge Cases / Limitations**: Mocked tests do not verify real network behavior. Integration tests with a real backend are also valuable.
- **How to Extend It**: Add tests for error cases, add tests for network timeouts.
- **Learning Notes**: Mocking `fetch` is a common pattern in frontend testing. Libraries like `msw` (Mock Service Worker) provide more realistic mocking.

---

### File: `frontend/src/components/ChatWindow.test.tsx`

- **Purpose**: Tests the ChatWindow component rendering and interactions.
- **Main Symbols**: Test cases for rendering, empty state, sending messages.
- **Dependencies**: React Testing Library, Vitest.
- **How It Works**: Renders the `ChatWindow` with various props (messages, callbacks) and asserts that the correct elements appear in the DOM. Simulates user interactions (typing, clicking Send) and verifies callbacks are called.
- **Relationship to Other Files**: Tests `components/ChatWindow.tsx`.
- **Important Implementation Details**: React Testing Library encourages testing components the way users interact with them (clicking, typing) rather than testing internal implementation details.
- **Edge Cases / Limitations**: Does not test auto-scroll behavior (would require a real DOM measurement).
- **How to Extend It**: Add tests for keyboard navigation, add accessibility tests.
- **Learning Notes**: `screen.getByText("...")` and `screen.getByRole("...")` are the preferred React Testing Library selectors. They query the DOM the way a user would perceive it.

---

### File: `frontend/src/hooks/useChat.test.tsx`

- **Purpose**: Tests the `useChat` hook's state management logic.
- **Main Symbols**: Test cases for sendMessage, clearConversation, error handling.
- **Dependencies**: React Testing Library's `renderHook`, Vitest.
- **How It Works**: Uses `renderHook(useChat)` to test the hook in isolation. Calls hook methods (sendMessage, clearConversation) and verifies state changes (messages, sessionId, sending, error).
- **Relationship to Other Files**: Tests `hooks/useChat.ts`.
- **Important Implementation Details**: `renderHook` is a React Testing Library utility that renders a hook inside a dummy component, letting you test hook logic without building UI.
- **Edge Cases / Limitations**: Does not test integration with real API calls (uses mocked fetch).
- **How to Extend It**: Add tests for concurrent sends, add tests for session persistence.
- **Learning Notes**: Testing hooks separately from components is a best practice. It ensures your state logic works correctly regardless of how it is rendered.

---

### File: `frontend/src/hooks/useDocuments.test.tsx`

- **Purpose**: Tests the `useDocuments` hook's state management and polling logic.
- **Main Symbols**: Test cases for refresh, upload, remove, polling.
- **Dependencies**: React Testing Library's `renderHook`, Vitest, fake timers.
- **How It Works**: Tests that `refresh()` fetches documents, `upload()` calls the API and refreshes, `remove()` calls delete and refreshes, and the polling `useEffect` triggers every 3 seconds when documents are processing.
- **Relationship to Other Files**: Tests `hooks/useDocuments.ts`.
- **Important Implementation Details**: Fake timers (`vi.useFakeTimers()`) allow testing time-dependent behavior (polling intervals) without actually waiting.
- **Edge Cases / Limitations**: Fake timers can be tricky with async operations. Make sure to advance timers and flush promises in the correct order.
- **How to Extend It**: Add tests for error states, add tests for concurrent operations.
- **Learning Notes**: `vi.useFakeTimers()` replaces `setTimeout` and `setInterval` with controllable versions. `vi.advanceTimersByTime(3000)` simulates 3 seconds passing instantly.

---

## 8. Frontend Deep Dive

### 8.1 Application State Flow

The frontend's state is organized into two custom hooks, managed at the `App.tsx` level:

```mermaid
graph TD
    subgraph "App.tsx (Root Component)"
        subgraph "useDocuments Hook"
            DOCS["documents[]"]
            LOADING["loading"]
            UPLOADING["uploading"]
            PROGRESS["uploadProgress"]
            DOCERR["error"]
        end
        subgraph "useChat Hook"
            MSGS["messages[]"]
            SID["sessionId"]
            SENDING["sending"]
            CHATERR["error"]
        end
        subgraph "Local State"
            SIDEBAR["sidebarOpen"]
            ACTIVE["activeDocumentId"]
        end
    end

    DOCS --> Sidebar
    LOADING --> Sidebar
    UPLOADING --> Sidebar
    PROGRESS --> Sidebar
    MSGS --> ChatWindow
    SENDING --> ChatWindow
    DOCERR --> ErrorToast
    CHATERR --> ErrorToast
```

**State flows downward** (parent to child via props). **Actions flow upward** (child to parent via callbacks). This is the standard React "unidirectional data flow" pattern.

### 8.2 API Calls

Every API call in the frontend follows this pattern:

```
1. Set loading/sending state to true
2. Call the API client function
3. On success: update state with the response data
4. On error: set the error state
5. Set loading/sending state to false
```

| API Call | Trigger | Hook | Updates |
|----------|---------|------|---------|
| `fetchDocuments()` | On mount, after upload, after delete, every 3s during processing | `useDocuments` | `documents[]` |
| `uploadDocument(file, onProgress)` | User drops a file | `useDocuments` | `uploading`, `uploadProgress`, then refreshes `documents[]` |
| `deleteDocument(id)` | User clicks delete | `useDocuments` | Refreshes `documents[]` |
| `sendChat(payload)` | User sends a message | `useChat` | `messages[]` (append user msg, then replace pending with response) |

### 8.3 Hooks and Responsibilities

| Hook | State Managed | Actions Provided | Side Effects |
|------|---------------|------------------|-------------|
| `useChat` | messages, sessionId, sending, error | sendMessage, clearConversation | Persists sessionId in sessionStorage |
| `useDocuments` | documents, loading, uploading, uploadProgress, error | refresh, upload, remove | Polls every 3s when documents are processing |

### 8.4 Component Tree

```
App
├── Sidebar
│   ├── UploadZone
│   └── DocumentCard (×N)
├── ChatWindow
│   ├── MessageBubble (×N)
│   │   ├── LoadingDots (if pending)
│   │   └── CitationCard (×N, if citations exist)
│   └── InputForm
└── ErrorToast
```

### 8.5 Upload Workflow

1. User drags PDF onto `UploadZone` (or clicks to select).
2. `UploadZone` validates file type client-side.
3. `UploadZone` calls `onUpload(file)` → `App.handleUpload` → `useDocuments.upload(file)`.
4. `useDocuments.upload()` sets `uploading = true`.
5. API client uses `XMLHttpRequest` with progress events → updates `uploadProgress`.
6. Backend returns 202 Accepted with `document_id`.
7. `useDocuments.upload()` calls `refresh()` to fetch updated document list.
8. The new document appears in `Sidebar` with "Processing" badge.
9. `useDocuments`'s polling `useEffect` detects a "processing" document and starts polling every 3 seconds.
10. When the backend finishes processing and the document status changes to "ready," the next poll picks it up and the badge turns green.

### 8.6 Chat Workflow

1. User types a question in `ChatWindow`'s input form and presses Enter (or clicks Send).
2. `ChatWindow` calls `onSendMessage(text)` → `App.tsx` → `useChat.sendMessage(text)`.
3. `useChat` appends a user message to `messages[]`.
4. `useChat` appends a pending message (with `isPending: true`) to `messages[]`.
5. `MessageBubble` renders the pending message with `<LoadingDots />`.
6. API client sends `POST /chat` with the question and session ID.
7. Backend processes the question (retrieval → prompt → LLM) and returns a `ChatResponse`.
8. `useChat` replaces the pending message with the real response (answer + citations).
9. `MessageBubble` renders the answer text and `CitationCard` components for each citation.
10. User can expand citation cards to see the source text.

### 8.7 Document Management Workflow

**Listing:**
- On mount, `useDocuments` calls `refresh()` to fetch the document list.
- Documents are displayed in the `Sidebar` as cards.

**Deleting:**
1. User clicks the delete button on a document card.
2. `Sidebar` calls `onDelete(documentId)` → `App.handleDelete` → `useDocuments.remove(documentId)`.
3. API client sends `DELETE /documents/{id}`.
4. `useDocuments` calls `refresh()` to update the list.
5. The document disappears from the sidebar.

### 8.8 How UI State Maps to Backend State

| Backend Document Status | Sidebar Badge | Color | User Experience |
|------------------------|---------------|-------|----------------|
| `"processing"` | Processing | Yellow/Amber | User sees the document was received; polling is active |
| `"ready"` | Ready | Green | Document is searchable; polling stops |
| `"failed"` | Failed | Red | Something went wrong; error details may be available |

| Backend Chat State | Frontend UI |
|-------------------|-------------|
| Before response | Loading dots animation |
| Successful response | Answer text + citation cards |
| Error response | Error message in message bubble + error toast |
| No Gemini key | Fallback message displayed as answer |

---

## 9. Backend Deep Dive

### 9.1 Application Startup (Lifespan)

The FastAPI lifespan is an async context manager that runs on startup and shutdown:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP ---
    # 1. Create directories
    Path(settings.upload_dir).mkdir(exist_ok=True)
    Path(settings.chroma_persist_dir).mkdir(exist_ok=True)

    # 2. Initialize database
    engine = build_engine(settings.db_url)
    Base.metadata.create_all(engine)
    session_factory = build_session_factory(engine)

    # 3. Initialize services (wiring dependencies)
    embedding_service = EmbeddingService()
    retriever = Retriever(embedding_service, settings)
    document_service = DocumentService(session_factory)
    pdf_service = PDFService()
    memory_store = SessionMemoryStore(settings.session_memory_k)
    chat_service = ChatService(retriever, settings, memory_store)
    pipeline = RAGPipeline(pdf_service, embedding_service, retriever, document_service, settings)

    # 4. Store on app.state (dependency injection)
    app.state.settings = settings
    app.state.chat_service = chat_service
    # ... etc.
    app.state._start_time = time.time()

    yield  # Server runs here

    # --- SHUTDOWN ---
    # (Implicit cleanup — Python GC handles it)
```

**Why this order?**
1. Directories must exist before services try to write to them.
2. The database must be created before `DocumentService` can use it.
3. `EmbeddingService` must be created before `Retriever` (which depends on it).
4. `Retriever` must be created before `ChatService` (which depends on it).

### 9.2 Configuration System

The configuration system uses Pydantic's `BaseSettings` with a singleton pattern:

```
.env file → BaseSettings reads env vars → Settings object → @lru_cache (singleton)
```

**How environment variables map to settings:**

| Environment Variable | Settings Field | Default | Type |
|---------------------|----------------|---------|------|
| `GEMINI_API_KEY` | `gemini_api_key` | `""` | str |
| `MODEL_NAME` | `model_name` | `"gemini-2.5-flash"` | str |
| `CHUNK_SIZE` | `chunk_size` | `1000` | int |
| `CHUNK_OVERLAP` | `chunk_overlap` | `200` | int |
| `TOP_K` | `top_k` | `5` | int |
| `MAX_FILE_MB` | `max_file_mb` | `50` | int |
| `SESSION_MEMORY_K` | `session_memory_k` | `10` | int |
| `CHROMA_PERSIST_DIR` | `chroma_persist_dir` | `"chroma"` | str |
| `UPLOAD_DIR` | `upload_dir` | `"uploads"` | str |
| `DB_URL` | `db_url` | `"sqlite:///data/rag.db"` | str |
| `LOG_LEVEL` | `log_level` | `"INFO"` | str |
| `CORS_ORIGINS_RAW` | `cors_origins_raw` | `'["http://localhost:5173"]'` | str |
| `RATE_LIMIT_CHAT` | `rate_limit_chat` | `"10/minute"` | str |

### 9.3 Database Model

The SQLite database has a single table:

```
┌──────────────────────────────────┐
│           documents               │
├──────────────────────────────────┤
│ id          TEXT (PK, UUID)       │
│ filename    TEXT                   │
│ file_path   TEXT                   │
│ page_count  INTEGER (nullable)    │
│ status      TEXT (default: processing) │
│ error_msg   TEXT (nullable)       │
│ file_size   INTEGER (nullable)    │
│ uploaded_at DATETIME              │
│ updated_at  DATETIME              │
└──────────────────────────────────┘
```

**State transitions:**
```
processing → ready     (successful processing)
processing → failed    (error during processing)
```

### 9.4 API Routes

| Method | Path | Handler | Rate Limited | Response Model | Description |
|--------|------|---------|-------------|----------------|-------------|
| `GET` | `/` | root | No | JSON | Status check |
| `GET` | `/api/v1/health` | health | No | HealthResponse | System health |
| `POST` | `/api/v1/upload` | upload | No | UploadResponse (202) | Upload PDF |
| `POST` | `/api/v1/chat` | chat | Yes (10/min) | ChatResponse | Ask question |
| `GET` | `/api/v1/documents` | list_documents | No | list[DocumentListItem] | List all docs |
| `GET` | `/api/v1/documents/{id}` | get_document | No | DocumentDetail | Get one doc |
| `DELETE` | `/api/v1/documents/{id}` | delete_document | No | DeleteResponse | Delete doc |

### 9.5 Services Layer

The services layer follows a dependency graph:

```mermaid
graph LR
    ChatService --> Retriever
    ChatService --> SessionMemoryStore
    ChatService --> PromptBuilder
    ChatService --> Gemini["Google Gemini (LLM)"]
    RAGPipeline --> PDFService
    RAGPipeline --> Chunker
    RAGPipeline --> Retriever
    RAGPipeline --> DocumentService
    Retriever --> EmbeddingService
    Retriever --> ChromaDB
    DocumentService --> SQLite
```

### 9.6 Rate Limiting

Rate limiting protects the chat endpoint from abuse:

- **Limit**: 10 requests per minute per IP address
- **Implementation**: SlowAPI (a FastAPI port of Flask-Limiter)
- **Storage**: In-memory (default). Lost on restart.
- **Response**: HTTP 429 Too Many Requests with a JSON error message.
- **Key function**: `get_remote_address` extracts the client IP from the request.

The chat endpoint is the only rate-limited route because:
1. It is the most expensive operation (involves embedding, vector search, and LLM call).
2. The LLM API may have its own rate limits and costs.
3. Other endpoints (health, documents) are lightweight and less abuse-prone.

### 9.7 Structured Logging

The application uses JSON-structured logging:

```json
{"level": "INFO", "logger": "app.main", "message": "Server started", "timestamp": "2026-06-11T12:00:00"}
{"level": "ERROR", "logger": "app.rag.pipeline", "message": "Failed to process document", "exception": "FileNotFoundError: ...", "timestamp": "2026-06-11T12:01:00"}
```

**Why JSON?** Log aggregation tools (ELK Stack, Datadog, AWS CloudWatch) can parse JSON logs automatically, enabling:
- Filtering by log level: `level == "ERROR"`
- Searching by logger: `logger == "app.rag.pipeline"`
- Alerting on exceptions: `exception != null`

### 9.8 Request / Response Schemas

All request and response schemas are defined using Pydantic:

**Chat Request (what the frontend sends):**
```json
{
  "question": "What was the revenue in Q3?",
  "session_id": "a3f1e2d4-b5c6-...",
  "top_k": 5
}
```

**Chat Response (what the backend returns):**
```json
{
  "answer": "According to the quarterly report, revenue in Q3 was $5.2 million...",
  "citations": [
    {
      "document_name": "quarterly_report.pdf",
      "page_number": 3,
      "chunk_preview": "Revenue in Q3 reached $5.2 million, representing..."
    }
  ],
  "session_id": "a3f1e2d4-b5c6-...",
  "sources_used": 3
}
```

---

## 10. Feature Deep Dives

### 10.1 Document Upload & Background Processing

**Why it exists:** Users need to add their PDF documents to the system so they can be searched. Processing (parsing, chunking, embedding) is CPU-intensive and can take seconds to minutes for large documents. Blocking the HTTP response for that long would create a bad user experience and risk timeouts.

**How it works internally:**
1. Frontend sends the PDF file as multipart form data.
2. Backend validates (type, extension, size) using `validators.py`.
3. Backend saves the file and creates a "processing" DB record.
4. Backend returns HTTP 202 immediately.
5. FastAPI's `BackgroundTasks` runs the pipeline asynchronously.
6. The pipeline updates the DB record to "ready" or "failed."
7. Frontend polls `GET /documents` every 3 seconds until status changes.

**Files that implement it:** `upload.py`, `validators.py`, `pipeline.py`, `document_service.py`, `useDocuments.ts`, `UploadZone.tsx`.

**What user problem it solves:** Users can continue using the app while documents process. They see real-time status updates (processing → ready) in the sidebar.

**What could be improved:**
- Add WebSocket notifications instead of polling.
- Add a progress percentage for large documents (e.g., "Embedding chunk 42/100").
- Add retry logic for failed documents.
- Handle orphaned "processing" documents (server crashed during processing).

### 10.2 PDF Text Extraction

**Why it exists:** PDFs are the most common format for business documents, but their text is not directly searchable by vector databases. We need to extract the raw text first.

**How it works internally:** PyMuPDF opens the PDF binary, iterates over each page object, and calls `get_text()` to extract the text layer. Each page produces a `PageText` object with the page number and text.

**Files that implement it:** `pdf_service.py`.

**What user problem it solves:** Users can upload standard PDF documents and the system understands their content.

**What could be improved:**
- Add OCR for scanned PDFs (e.g., `pytesseract`).
- Add table extraction (e.g., `camelot`).
- Add image description (e.g., send images to a vision model).
- Support multi-column layouts with better text ordering.

### 10.3 Text Chunking

**Why it exists:** Entire documents are too large for embedding models and LLM context windows. Small, focused chunks enable precise retrieval.

**How it works internally:** The `Chunker` normalizes whitespace, then slides a window of `chunk_size` characters across the text with a step of `chunk_size - chunk_overlap`. Each window becomes a `Chunk` with the text, page number, and chunk index.

**Files that implement it:** `chunker.py`.

**What user problem it solves:** When users ask a question, the system finds the specific paragraphs that answer it — not the entire document.

**What could be improved:**
- Sentence-aware splitting (don't break mid-sentence).
- Semantic splitting (detect topic changes).
- Hierarchical chunking (document → section → paragraph → sentence).
- Adaptive chunk size based on content density.

### 10.4 Vector Embedding & Storage

**Why it exists:** Keyword search misses semantically similar text (e.g., "revenue" vs. "earnings"). Embedding converts text into a meaning-aware numerical representation, enabling semantic search.

**How it works internally:** `EmbeddingService` loads the `all-MiniLM-L6-v2` model and calls `model.encode()` to produce 384-dimensional normalized vectors. These vectors, along with metadata and the original text, are upserted into ChromaDB's `rag_chunks` collection.

**Files that implement it:** `embedding_service.py`, `retriever.py`.

**What user problem it solves:** Users can ask questions in natural language and find relevant content even when exact keywords don't match.

**What could be improved:**
- Use a larger/better embedding model (e.g., `all-mpnet-base-v2` for 768 dimensions).
- Add GPU acceleration for faster embedding.
- Batch embedding with configurable batch sizes for memory management.
- Add embedding caching to avoid re-embedding unchanged documents.

### 10.5 Semantic Search & Retrieval

**Why it exists:** Given a user's question, we need to find the most relevant chunks from all uploaded documents. Vector similarity search does this based on meaning, not just keywords.

**How it works internally:** The question is embedded using the same model. ChromaDB compares this vector against all stored chunk vectors using cosine distance. The top K closest chunks are returned.

**Files that implement it:** `retriever.py`, `chat_service.py`.

**What user problem it solves:** Users get answers based on the meaning of their question, even if they use different words than the document.

**What could be improved:**
- Add a minimum relevance threshold (reject very distant chunks).
- Add document filtering (search only specific documents).
- Add metadata filtering (search by date range, document type).
- Add a reranker for more accurate ranking (see Extension Guide).

### 10.6 Prompt Engineering

**Why it exists:** The LLM needs clear instructions to produce high-quality, grounded answers. A well-crafted prompt prevents hallucination and ensures citations.

**How it works internally:** The `build_prompt()` function assembles a string with four sections: SYSTEM (behavior instructions), HISTORY (conversation context), CONTEXT (retrieved chunks with source attribution), and QUESTION (the user's current question).

**Files that implement it:** `prompt.py`.

**What user problem it solves:** The LLM produces accurate, cited answers instead of making things up.

**What could be improved:**
- Add few-shot examples (show the LLM what a good answer looks like).
- Add output format instructions (e.g., "respond in bullet points").
- Add confidence indicators ("I am 90% sure" vs. "I couldn't find enough information").
- Use a templating engine (Jinja2) for complex prompts.

### 10.7 LLM Integration

**Why it exists:** The LLM is the "brain" that reads the retrieved context and writes a human-like answer.

**How it works internally:** `ChatService` lazy-loads a `ChatGoogleGenerativeAI` instance via LangChain. When a question is asked, the assembled prompt is sent to Gemini via `llm.invoke()`. If no API key is configured, a fallback message is returned.

**Files that implement it:** `chat_service.py`.

**What user problem it solves:** Users get natural-language answers instead of raw document excerpts.

**What could be improved:**
- Add streaming responses (show the answer word by word as it generates).
- Add model selection (let users choose between Gemini models).
- Add response caching (avoid re-generating answers for identical questions).
- Add retry logic with exponential backoff for API errors.

### 10.8 Citation Generation & Deduplication

**Why it exists:** Users need to verify answers against original sources. Citations provide traceability and build trust.

**How it works internally:** Each retrieved chunk carries metadata (document name, page number). The `ChatService` extracts this metadata to create `Citation` objects. When multiple chunks come from the same page of the same document, they are merged into a single citation with concatenated previews (separated by `"\n\n[...]\n\n"`).

**Files that implement it:** `chat_service.py`, `CitationCard.tsx`.

**What user problem it solves:** Users can verify every answer against the original document, page by page.

**What could be improved:**
- Add clickable links to the original PDF page.
- Highlight the specific text within the page that the answer is based on.
- Rank citations by relevance (show the most relevant source first).
- Show the relevance score (distance) for each citation.

### 10.9 Conversational Memory

**Why it exists:** Users often ask follow-up questions ("What about Q4?" after asking about Q3 revenue). Without memory, the LLM would not know what "Q4" refers to.

**How it works internally:** `SessionMemoryStore` uses a `defaultdict(deque)` keyed by `session_id`. Each deque has a maximum length (`session_memory_k * 2`, since each turn has a question and an answer). When a new turn is added, the oldest turn is automatically dropped if the deque is full. The history is rendered as a formatted string and included in the LLM prompt.

**Files that implement it:** `chat_service.py`.

**What user problem it solves:** Users can have natural, multi-turn conversations without repeating context.

**What could be improved:**
- Persist memory to Redis or the database (survives server restarts).
- Add memory summarization (compress old turns into a summary).
- Add per-session configuration (some users may want more/less memory).
- Add memory search (retrieve relevant past turns, not just recent ones).

### 10.10 Rate Limiting

**Why it exists:** The chat endpoint is expensive (embedding + vector search + LLM API call). Without rate limiting, a single user or bot could overwhelm the server and incur large API costs.

**How it works internally:** SlowAPI intercepts requests to the chat endpoint, identifies the client by IP address, and counts requests within a time window. If the count exceeds the limit (10 per minute by default), it returns HTTP 429.

**Files that implement it:** `rate_limit.py`, `chat.py`, `main.py`.

**What user problem it solves:** Protects the system from abuse, ensuring fair access for all users.

**What could be improved:**
- Use Redis as a rate limit backend (for multi-server deployments).
- Add per-user rate limits (requires authentication).
- Add different limits for different endpoints.
- Add rate limit headers in responses (X-RateLimit-Remaining, X-RateLimit-Reset).

### 10.11 Health Monitoring

**Why it exists:** In production, monitoring systems (Kubernetes, load balancers) need to know if the application is healthy and should receive traffic.

**How it works internally:** The `GET /health` endpoint checks two subsystems:
1. **ChromaDB**: Calls `collection.count()` — if it succeeds, ChromaDB is healthy.
2. **Gemini**: Checks if the API key is non-empty — does not actually call the API.
3. **Uptime**: Calculates `time.time() - start_time`.

**Files that implement it:** `health.py`.

**What user problem it solves:** Operations teams can monitor system health and receive alerts when something is down.

**What could be improved:**
- Add database connectivity check (actually query SQLite).
- Add disk space check (ensure upload/chroma directories have space).
- Add a "deep health" endpoint that actually calls the Gemini API.
- Add version information in the response.

### 10.12 Error Handling

**Why it exists:** Errors are inevitable (network failures, invalid input, missing files). Good error handling ensures the user gets clear feedback and the system remains stable.

**How it works internally:**
- **Validation errors** (Pydantic): FastAPI automatically returns 422 with field-level error details.
- **File validation errors** (validators.py): Returns 400 or 413 with a descriptive message.
- **Not found errors** (documents.py): Returns 404 with "Document not found."
- **Rate limit errors** (SlowAPI): Returns 429 with "Rate limit exceeded."
- **Processing errors** (pipeline.py): Caught by try/except, saved to DB as status="failed" with error message.
- **LLM errors** (chat_service.py): Falls back to a static message.
- **Frontend errors** (useChat, useDocuments): Caught and displayed as error toasts.

**Files that implement it:** Multiple files throughout the codebase.

**What user problem it solves:** Users see helpful error messages instead of cryptic stack traces.

**What could be improved:**
- Add error tracking (Sentry, Bugsnag).
- Add error codes (e.g., `ERR_FILE_TOO_LARGE`).
- Add error recovery guidance (e.g., "Try uploading a smaller file").
- Add request IDs for correlating frontend errors with backend logs.

### 10.13 Drag-and-Drop Upload UI

**Why it exists:** Drag-and-drop is the most intuitive way to upload files. Users can simply drag a PDF from their file explorer onto the browser.

**How it works internally:** The `UploadZone` component listens for HTML5 drag-and-drop events (`dragover`, `drop`). When a file is dropped, it reads the file from the event's `dataTransfer` object, validates it client-side, and calls the upload callback. A hidden `<input type="file">` provides an alternative click-to-select method.

**Files that implement it:** `UploadZone.tsx`.

**What user problem it solves:** Uploading files is quick and intuitive — no multi-step form required.

**What could be improved:**
- Add multi-file drag-and-drop.
- Add visual feedback during drag (highlight the zone).
- Add file type icons.
- Add upload queue management (progress for multiple files).

### 10.14 Real-time Processing Status Polling

**Why it exists:** After uploading a document, the user needs to know when processing is complete. Since the backend processes documents asynchronously, the frontend needs to check for updates.

**How it works internally:** The `useDocuments` hook's `useEffect` checks if any document has `status === "processing"`. If so, it sets up a `setInterval` that calls `refresh()` (which calls `GET /documents`) every 3 seconds. When all documents reach "ready" or "failed" status, the interval is cleared.

**Files that implement it:** `useDocuments.ts`.

**What user problem it solves:** Users see real-time status updates without manually refreshing the page.

**What could be improved:**
- Replace polling with WebSockets or Server-Sent Events (SSE) for instant updates.
- Add exponential backoff (poll less frequently over time).
- Add per-document polling (only poll for the specific document that is processing).
- Show a processing animation or progress percentage.

---

## 11. Test Suite Explanation

### 11.1 conftest.py — Shared Test Infrastructure

**What it covers:** Test fixtures and fake service implementations shared across all test files.

**Which module it protects:** The test infrastructure itself. If fixtures break, all tests break.

**Why it matters:** Consistent test setup prevents test pollution (one test affecting another) and reduces code duplication.

**What bugs it would catch:** Configuration errors in test setup, missing service initialization.

**Key components:**
- `FakeRetriever`: Returns hardcoded search results (avoids needing a real ChromaDB instance in tests).
- `FakePipeline`: Records method calls without performing real processing.
- `FakeChatService`: Returns a canned answer without calling Gemini.
- In-memory SQLite database: Each test gets a fresh database, ensuring complete isolation.

### 11.2 test_chat_service.py

**What it covers:** 6 tests covering the `ChatService` class.

**Which module it protects:** `services/chat_service.py` — the core chat orchestration logic.

**Why it matters:** The chat service is the most complex piece of the backend, combining retrieval, prompt building, LLM calling, citation generation, and memory management.

**What bugs it would catch:**
1. **Fallback without LLM**: Ensures the system works without a Gemini API key.
2. **Uses LLM when available**: Verifies the LLM is called when configured.
3. **Loads LLM from dependency**: Tests lazy loading of the LLM client.
4. **Falls back with no citations**: Handles the case where retrieval returns nothing.
5. **Session memory limits**: Ensures old conversation turns are dropped when the window is full.
6. **Citation deduplication**: Verifies that duplicate citations from the same page are merged correctly.

### 11.3 test_chunker.py

**What it covers:** 2 tests covering the `Chunker` class.

**Which module it protects:** `rag/chunker.py` — the text splitting logic.

**Why it matters:** Incorrect chunking (wrong overlap, missing chunks, empty chunks) directly affects retrieval quality.

**What bugs it would catch:**
1. **Splits with overlap**: Verifies chunks have the correct size and overlap.
2. **Ignores blank pages**: Ensures empty pages don't produce empty chunks.

### 11.4 test_deps_and_logger.py

**What it covers:** 3 tests covering dependency injection helpers and logging.

**Which module it protects:** `api/deps.py` and `utils/logger.py`.

**Why it matters:** Broken dependency injection would cause every route to fail. Broken logging would make debugging impossible in production.

**What bugs it would catch:**
1. **Dependency extraction**: Ensures services are correctly retrieved from `app.state`.
2. **JSON log format**: Verifies log output is valid JSON.
3. **Exception logging**: Ensures exceptions are captured in log output.

### 11.5 test_document_service.py

**What it covers:** 3 tests covering CRUD operations on document metadata.

**Which module it protects:** `services/document_service.py`.

**Why it matters:** Document metadata drives the entire UI — document listing, status display, and deletion.

**What bugs it would catch:**
1. **CRUD operations**: Create, read, list, delete all work correctly.
2. **Field updates**: Status and page_count can be updated after creation.
3. **File removal**: Filesystem cleanup works correctly.

### 11.6 test_embedding_service.py

**What it covers:** 3 tests covering the embedding service.

**Which module it protects:** `services/embedding_service.py`.

**Why it matters:** Incorrect embeddings would make semantic search completely useless.

**What bugs it would catch:**
1. **Lazy loading**: Model is loaded on first use, not at instantiation.
2. **embed_texts dimensions**: Output has the correct shape (N × 384).
3. **embed_query**: Single-text embedding works correctly.

### 11.7 test_main.py

**What it covers:** 1 test covering CORS configuration.

**Which module it protects:** `main.py` — the app configuration.

**Why it matters:** If CORS is misconfigured, the frontend cannot communicate with the backend at all.

**What bugs it would catch:** Missing CORS headers, incorrect allowed origins.

### 11.8 test_pdf_service.py

**What it covers:** 1 test covering PDF text extraction.

**Which module it protects:** `services/pdf_service.py`.

**Why it matters:** If PDF extraction fails or returns garbled text, the entire RAG pipeline produces garbage.

**What bugs it would catch:** Empty page extraction, incorrect page numbering, file reading errors.

### 11.9 test_pipeline.py

**What it covers:** 3 tests covering the RAG pipeline orchestrator.

**Which module it protects:** `rag/pipeline.py`.

**Why it matters:** The pipeline sequences multiple operations. If the sequence is wrong or error handling is missing, documents may be partially processed or have incorrect status.

**What bugs it would catch:**
1. **Successful processing**: All steps execute in order, status is "ready."
2. **Failed processing**: Error is caught, status is "failed" with error message.
3. **Document deletion**: Chunks and file are properly cleaned up.

### 11.10 test_retriever.py

**What it covers:** 2 tests covering ChromaDB operations.

**Which module it protects:** `rag/retriever.py`.

**Why it matters:** The retriever is the bridge between embedding generation and vector search. Bugs here would make search return wrong or no results.

**What bugs it would catch:**
1. **CRUD and search**: Adding chunks and searching for them works correctly.
2. **Deletion by doc_id**: Deleting a document removes all its chunks.

### 11.11 test_routes.py

**What it covers:** 8 tests covering all API endpoints.

**Which module it protects:** `api/routes/*.py` — all HTTP endpoints.

**Why it matters:** Routes are the external interface. If routes return wrong status codes, missing fields, or crash on valid input, the frontend breaks.

**What bugs it would catch:**
1. **Health endpoint**: Returns correct status and component health.
2. **Health degraded**: Handles partially degraded state.
3. **Upload**: Returns 202 with correct response shape.
4. **Document list/detail/delete**: CRUD endpoints work correctly.
5. **Document 404s**: Returns 404 for non-existent documents.
6. **Serialize helper**: Response serialization works correctly.
7. **Chat response**: Returns answer with citations.
8. **Root route**: Returns basic status.

### 11.12 test_settings.py

**What it covers:** 3 tests covering configuration parsing.

**Which module it protects:** `config/settings.py`.

**Why it matters:** Incorrect settings parsing could silently misconfigure the entire application (e.g., chunk_size of 0, wrong CORS origins).

**What bugs it would catch:**
1. **Defaults**: All settings have correct default values.
2. **CORS parsing (JSON)**: JSON array of origins is parsed correctly.
3. **CORS parsing (comma-separated)**: Comma-separated origins are parsed correctly.

### 11.13 test_validators.py

**What it covers:** 4 tests covering upload validation.

**Which module it protects:** `utils/validators.py`.

**Why it matters:** Validation is a security boundary. Broken validation could allow malicious files to be uploaded or cause crashes during processing.

**What bugs it would catch:**
1. **Valid PDF**: Accepts legitimate PDF files.
2. **Invalid extension**: Rejects non-PDF files.
3. **Empty file**: Handles zero-byte uploads.
4. **Too large**: Enforces file size limits.

### 11.14 Frontend Tests

**`client.test.ts`**: Tests the API client layer. Ensures HTTP requests are formed correctly and responses are parsed correctly.

**`ChatWindow.test.tsx`**: Tests the ChatWindow component. Ensures messages render correctly, the input form works, and the Send button behaves correctly.

**`useChat.test.tsx`**: Tests the useChat hook. Ensures message state management, session ID persistence, and error handling work correctly.

**`useDocuments.test.tsx`**: Tests the useDocuments hook. Ensures document fetching, upload progress tracking, and polling logic work correctly.

---

## 12. Deployment Guide

### 12.1 Prerequisites

Before deploying, ensure you have:
- **Docker** (version 20.10+): [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose** (version 2.0+): Usually included with Docker Desktop
- **A Google Gemini API key** (optional, for AI-generated answers): [Get an API key](https://makersuite.google.com/app/apikey)

### 12.2 Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your values:
   ```bash
   # Required for AI answers (optional — system works without it)
   GEMINI_API_KEY=your_gemini_api_key_here

   # Optional overrides (defaults are sensible)
   MODEL_NAME=gemini-2.5-flash
   CHUNK_SIZE=1000
   CHUNK_OVERLAP=200
   TOP_K=5
   MAX_FILE_MB=50
   SESSION_MEMORY_K=10
   LOG_LEVEL=INFO
   CORS_ORIGINS_RAW=["http://localhost:5173"]
   RATE_LIMIT_CHAT=10/minute
   ```

### 12.3 Running with Docker Compose

This is the recommended way to run the application:

```bash
# Build and start both services
docker-compose up --build

# Or run in the background (detached mode)
docker-compose up --build -d
```

After startup:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation (Swagger)**: http://localhost:8000/docs

To stop:
```bash
docker-compose down
```

To stop and remove volumes (deletes all data):
```bash
docker-compose down -v
```

**What Docker Compose does:**
1. Builds the backend image from `backend/Dockerfile`.
2. Builds the frontend image from `frontend/Dockerfile`.
3. Creates three named volumes for persistent data.
4. Starts the backend container (port 8000).
5. Starts the frontend container (port 5173) after the backend.
6. Loads environment variables from `.env` into the backend container.

### 12.4 Running Locally (Without Docker)

**Backend:**

```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies (for testing)
pip install -r requirements-dev.txt

# Create necessary directories
mkdir -p uploads chroma data

# Run the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The `--reload` flag enables auto-reload: the server restarts automatically when you change code. Do not use this in production.

**Frontend:**

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

**Running tests:**

```bash
# Backend tests
cd backend
pytest -v --cov=app

# Frontend tests
cd frontend
npm test
```

### 12.5 Production Considerations

For a production deployment, consider the following:

| Concern | Recommendation |
|---------|---------------|
| **Database** | Switch from SQLite to PostgreSQL for concurrent access |
| **Vector DB** | Use ChromaDB in client-server mode, or switch to Pinecone/Weaviate |
| **HTTPS** | Add an nginx reverse proxy with SSL termination |
| **Authentication** | Add OAuth2/JWT authentication (see Extension Guide) |
| **Rate limiting** | Use Redis as the SlowAPI backend for persistence across restarts |
| **Scaling** | Use Gunicorn with multiple Uvicorn workers |
| **Monitoring** | Add Prometheus metrics, structured logging with ELK |
| **Secrets** | Use a secrets manager (AWS SSM, HashiCorp Vault) instead of `.env` |
| **Backups** | Regular backups of SQLite DB and ChromaDB data |
| **Resource limits** | Set memory/CPU limits in Docker Compose |

---

## 13. Extension Guide

### 13.1 Swap the Embedding Model

The default model (`all-MiniLM-L6-v2`, 384 dimensions) is fast but not the most accurate. To use a better model:

1. **Choose a model** from the [SentenceTransformers model hub](https://www.sbert.net/docs/pretrained_models.html). For example, `all-mpnet-base-v2` (768 dimensions, higher quality but slower).

2. **Update `EmbeddingService`** in `embedding_service.py`:
   ```python
   class EmbeddingService:
       def __init__(self, model_name: str = "sentence-transformers/all-mpnet-base-v2"):
           ...
   ```

3. **Re-embed all existing documents.** Changing the model changes the vector dimensions and the embedding space. Old embeddings are incompatible with new ones. You must:
   - Delete the ChromaDB collection (or use a new collection name).
   - Re-upload all documents.

4. **Update tests** that assert embedding dimensions (384 → 768).

### 13.2 Add Authentication

To restrict access to authenticated users:

1. **Add a User model** in `models/db.py`:
   ```python
   class User(Base):
       __tablename__ = "users"
       id: Mapped[str] = mapped_column(String(36), primary_key=True)
       email: Mapped[str] = mapped_column(String, unique=True)
       hashed_password: Mapped[str] = mapped_column(String)
   ```

2. **Add JWT token generation** using `python-jose` and `passlib`:
   ```bash
   pip install python-jose[cryptography] passlib[bcrypt]
   ```

3. **Create an auth service** in `services/auth_service.py` with login, register, and token verification functions.

4. **Add a dependency** in `deps.py` that extracts and verifies the JWT from the `Authorization` header:
   ```python
   async def get_current_user(request: Request) -> User:
       token = request.headers.get("Authorization", "").replace("Bearer ", "")
       # Verify token and return user
   ```

5. **Protect routes** by adding the dependency:
   ```python
   @router.post("/chat")
   async def chat(body: ChatRequest, user = Depends(get_current_user)):
       ...
   ```

6. **Add login/register pages** to the frontend.

### 13.3 Add New Document Types

To support DOCX, TXT, or other file formats:

1. **Add parsers** for each format:
   ```python
   # services/docx_service.py
   from docx import Document as DocxDocument

   class DocxService:
       def extract_pages(self, file_path: str) -> list[PageText]:
           doc = DocxDocument(file_path)
           text = "\n".join([p.text for p in doc.paragraphs])
           return [PageText(page_number=1, text=text)]
   ```

2. **Update the validator** to accept new file types:
   ```python
   ALLOWED_TYPES = {"application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
   ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
   ```

3. **Update the pipeline** to choose the correct parser based on file extension:
   ```python
   if file_path.endswith(".pdf"):
       pages = self.pdf_service.extract_pages(file_path)
   elif file_path.endswith(".docx"):
       pages = self.docx_service.extract_pages(file_path)
   elif file_path.endswith(".txt"):
       pages = self.txt_service.extract_pages(file_path)
   ```

4. **Update the frontend** to accept new file types in `UploadZone.tsx`.

### 13.4 Add Streaming Responses

To show the LLM's answer word-by-word as it generates:

1. **Backend**: Change the chat endpoint to use `StreamingResponse`:
   ```python
   from fastapi.responses import StreamingResponse

   @router.post("/chat")
   async def chat(body: ChatRequest, ...):
       async def generate():
           async for chunk in chat_service.stream_answer(body.question, ...):
               yield f"data: {json.dumps(chunk)}\n\n"
       return StreamingResponse(generate(), media_type="text/event-stream")
   ```

2. **ChatService**: Add a `stream_answer()` method that yields chunks:
   ```python
   async def stream_answer(self, question, session_id, top_k):
       # ... retrieval and prompt building ...
       async for chunk in llm.astream(prompt):
           yield {"text": chunk.content}
       yield {"citations": citations}
   ```

3. **Frontend**: Use the `EventSource` API or `fetch` with ReadableStream:
   ```typescript
   const response = await fetch("/api/v1/chat", { method: "POST", body: ... });
   const reader = response.body!.getReader();
   const decoder = new TextDecoder();

   while (true) {
       const { done, value } = await reader.read();
       if (done) break;
       const text = decoder.decode(value);
       // Parse SSE data and update message in real-time
   }
   ```

### 13.5 Switch to PostgreSQL

For production deployments that need concurrent writes:

1. **Install the PostgreSQL driver**:
   ```bash
   pip install psycopg2-binary
   ```

2. **Update the database URL** in `.env`:
   ```bash
   DB_URL=postgresql://user:password@localhost:5432/rag_db
   ```

3. **Remove the SQLite workaround** in `db.py`:
   ```python
   def build_engine(db_url: str):
       # Remove check_same_thread for PostgreSQL
       if "sqlite" in db_url:
           return create_engine(db_url, connect_args={"check_same_thread": False})
       return create_engine(db_url)
   ```

4. **Add a PostgreSQL service** to `docker-compose.yml`:
   ```yaml
   postgres:
     image: postgres:16
     environment:
       POSTGRES_USER: rag_user
       POSTGRES_PASSWORD: rag_password
       POSTGRES_DB: rag_db
     volumes:
       - postgres_data:/var/lib/postgresql/data
   ```

5. **Update the backend service** to depend on `postgres` and set the `DB_URL` environment variable.

### 13.6 Add a Reranker

A reranker improves retrieval quality by re-scoring initial results using a more powerful model:

1. **Install a reranker model**:
   ```bash
   pip install sentence-transformers
   ```

2. **Add a reranker service**:
   ```python
   from sentence_transformers import CrossEncoder

   class RerankerService:
       def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
           self.model = CrossEncoder(model_name)

       def rerank(self, query: str, chunks: list[dict], top_k: int) -> list[dict]:
           pairs = [(query, chunk["text"]) for chunk in chunks]
           scores = self.model.predict(pairs)
           ranked = sorted(zip(scores, chunks), reverse=True)
           return [chunk for _, chunk in ranked[:top_k]]
   ```

3. **Insert into the chat flow** (in `chat_service.py`):
   ```python
   # After retrieval, before prompt building:
   results = retriever.search(question, top_k=top_k * 3)  # Retrieve more
   reranked = reranker.rerank(question, results, top_k)     # Rerank to top_k
   ```

### 13.7 Add Hybrid Search

Hybrid search combines vector search (semantic) with keyword search (lexical) for better recall:

1. **Add a keyword search index** using SQLite FTS5 or Elasticsearch:
   ```sql
   CREATE VIRTUAL TABLE chunk_fts USING fts5(text, doc_id, page_number);
   ```

2. **Search both indexes** and combine results:
   ```python
   def hybrid_search(self, query, top_k):
       vector_results = self.retriever.search(query, top_k * 2)
       keyword_results = self.keyword_search(query, top_k * 2)

       # Reciprocal Rank Fusion (RRF) to combine scores
       combined = {}
       for rank, result in enumerate(vector_results):
           combined[result.id] = combined.get(result.id, 0) + 1 / (rank + 60)
       for rank, result in enumerate(keyword_results):
           combined[result.id] = combined.get(result.id, 0) + 1 / (rank + 60)

       # Sort by combined score and return top_k
       return sorted(combined.items(), key=lambda x: x[1], reverse=True)[:top_k]
   ```

---

## 14. Troubleshooting Guide

### 14.1 Pydantic Namespace Conflict

**Error:**
```
UserWarning: Field "model_name" has conflict with protected namespace "model_"
```

**Cause:** Pydantic v2 reserves the `model_` prefix for its internal methods (like `model_dump()`, `model_validate()`). Having a field named `model_name` triggers this warning.

**Fix (already applied in this project):**
```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        protected_namespaces=('settings_',)  # Override the default 'model_' protection
    )
```

This tells Pydantic: "Only treat fields starting with `settings_` as protected, not `model_`."

### 14.2 SlowAPI Decorator Issues

**Error:**
```
TypeError: unsupported callable / unexpected keyword argument during rate limit check
```

**Cause:** SlowAPI inspects function signatures to extract request parameters. When combined with Pydantic v2 and `from __future__ import annotations`, the string-based type annotations confuse SlowAPI's introspection.

**Fix (already applied in this project):** Use a wrapper decorator in `chat.py`:
```python
def limit_chat(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await func(*args, **kwargs)
    return limiter.limit(settings.rate_limit_chat)(wrapper)
```

This wraps the original function first, then applies the rate limit to the wrapper (which has simple `*args, **kwargs` signature that SlowAPI can handle).

### 14.3 ChromaDB Connection Issues

**Error:**
```
chromadb.errors.ChromaError: Could not connect to persistence directory
```

**Cause:** The ChromaDB persistence directory does not exist or lacks write permissions.

**Fix:**
1. Ensure the directory exists: `mkdir -p chroma`
2. Check permissions: `chmod 755 chroma`
3. In Docker, ensure the volume is properly mounted in `docker-compose.yml`.
4. If using Docker, check that the container user has write access to the mount point.

**Error:**
```
ValueError: Collection rag_chunks has dimensionality X, but embeddings have dimensionality Y
```

**Cause:** You changed the embedding model (which changed the vector dimensions) without clearing the existing ChromaDB data.

**Fix:** Delete the ChromaDB data and re-upload all documents:
```bash
rm -rf chroma/
```

### 14.4 Model Loading Issues

**Error:**
```
OSError: Can't load tokenizer for 'sentence-transformers/all-MiniLM-L6-v2'
```

**Cause:** The model cannot be downloaded (no internet access, or behind a firewall).

**Fix:**
1. Ensure the machine has internet access.
2. If behind a firewall, download the model on a machine with access and copy it:
   ```bash
   python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
   ```
   The model is cached in `~/.cache/huggingface/`.
3. Copy the cache directory to the target machine.

**Error:**
```
google.api_core.exceptions.PermissionDenied: API key not valid
```

**Cause:** The `GEMINI_API_KEY` environment variable is incorrect or the key has been revoked.

**Fix:**
1. Verify the key at [Google AI Studio](https://makersuite.google.com/).
2. Ensure the key is correctly set in `.env` (no extra spaces or quotes).
3. Restart the server after changing `.env`.

### 14.5 Common Docker Issues

**Issue: "port is already allocated"**
```
Error starting userland proxy: listen tcp 0.0.0.0:8000: bind: address already in use
```
**Fix:** Another process is using port 8000. Stop it, or change the port in `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Map host port 8001 to container port 8000
```

**Issue: "no space left on device"**
**Fix:** Docker images and volumes consume disk space. Clean up:
```bash
docker system prune -a  # Remove all unused images, containers, networks
docker volume prune      # Remove all unused volumes
```

**Issue: "build context too large"**
**Fix:** Add a `.dockerignore` file to exclude large/unnecessary files:
```
node_modules
venv
__pycache__
.git
*.pyc
```

### 14.6 Frontend Build Issues

**Issue: "Module not found" errors**
**Fix:** Dependencies might not be installed:
```bash
cd frontend
rm -rf node_modules
npm install
```

**Issue: "VITE_API_BASE_URL not working"**
**Fix:** Vite environment variables must start with `VITE_`. Also, you need to restart the dev server after changing environment variables (Vite reads them at build time, not runtime).

**Issue: Blank page after build**
**Fix:** Check the browser console for JavaScript errors. Common causes:
- API URL pointing to the wrong backend address.
- CORS not configured to allow the production frontend URL.

---

## 15. Future Improvement Ideas

Here are potential enhancements, roughly ordered by impact and complexity:

| Idea | Impact | Complexity | Description |
|------|--------|-----------|-------------|
| **Streaming responses** | High | Medium | Show the LLM's answer as it generates (word by word) |
| **Authentication** | High | Medium | Restrict access to authorized users |
| **Multi-format support** | High | Low-Medium | Support DOCX, TXT, Markdown, HTML |
| **PostgreSQL** | High | Low | Replace SQLite for production |
| **Reranking** | Medium | Low | Re-score retrieved chunks with a cross-encoder |
| **OCR support** | Medium | Medium | Extract text from scanned PDFs |
| **Table extraction** | Medium | Medium | Properly parse tables in PDFs |
| **Hybrid search** | Medium | Medium | Combine vector search with keyword search |
| **WebSocket updates** | Medium | Medium | Replace polling with real-time push notifications |
| **Document versioning** | Medium | Medium | Track changes when a document is re-uploaded |
| **Multi-language support** | Medium | Low | Use multilingual embedding models |
| **User feedback** | Medium | Low | Let users rate answers (thumbs up/down) |
| **Answer caching** | Medium | Low | Cache answers for repeated questions |
| **Chunk preview highlighting** | Low | Low | Highlight query terms in citation previews |
| **Export chat history** | Low | Low | Download conversation as PDF/Markdown |
| **Admin dashboard** | Low | Medium | Monitor system metrics, manage users |
| **Fine-tuned models** | Low | High | Fine-tune the LLM on domain-specific data |
| **Knowledge graph** | Low | High | Build a graph of entities and relationships |

---

## 16. Glossary

| Term | Definition |
|------|-----------|
| **aiofiles** | A Python library that provides async file I/O operations, allowing file reads/writes without blocking the event loop. |
| **API (Application Programming Interface)** | A set of rules and protocols that allows different software programs to communicate with each other. |
| **API Key** | A secret string used to authenticate requests to an API. Like a password for your application. |
| **Async / Asynchronous** | A programming style where operations can run concurrently without blocking each other. While one operation waits (e.g., for a network response), others can proceed. |
| **Background Task** | A function that runs after an HTTP response has been sent, allowing the server to perform time-consuming work without making the client wait. |
| **BaseModel** | A Pydantic class for defining data models with automatic validation and serialization. |
| **BaseSettings** | A Pydantic class specifically for configuration management that can read values from environment variables. |
| **Callback** | A function passed as an argument to another function, to be called when an event occurs. In React, callbacks are how child components communicate with parents. |
| **ChromaDB** | An open-source vector database designed for storing and querying embeddings. |
| **Chunk** | A small piece of text extracted from a larger document. Used as the basic unit for embedding and retrieval. |
| **Citation** | A reference to a specific source (document name, page number, preview text) that supports an answer. |
| **Component** | In React, a reusable piece of UI defined as a function that returns JSX. |
| **Container** | A lightweight, isolated environment that packages an application with all its dependencies. Created from a Docker image. |
| **Content Type** | An HTTP header that tells the receiver what format the data is in (e.g., `application/json`, `application/pdf`). |
| **Context Manager** | A Python construct (using `with` or `async with`) that automatically handles setup and cleanup. The `lifespan` function is a context manager. |
| **Context Window** | The maximum amount of text (in tokens) that an LLM can process in a single request. |
| **CORS (Cross-Origin Resource Sharing)** | A security mechanism that controls which websites can make requests to your API. Required when frontend and backend are on different origins (ports). |
| **Cosine Distance** | A measure of how different two vectors are: `1 - cosine_similarity`. Lower distance = more similar. |
| **Cosine Similarity** | A measure of how similar two vectors are, based on the angle between them. Range: -1 (opposite) to 1 (identical). |
| **CRUD** | Create, Read, Update, Delete — the four basic operations on persistent data. |
| **CSS (Cascading Style Sheets)** | The language used to style HTML elements (colors, layout, fonts, animations). |
| **Dataclass** | A Python decorator (`@dataclass`) that automatically generates `__init__`, `__repr__`, and other methods for classes that primarily store data. |
| **Declarative Base** | A SQLAlchemy base class that ORM models inherit from to enable table mapping. |
| **Decorator** | A Python function that wraps another function, adding behavior before or after it runs. Denoted by `@decorator_name` above a function definition. |
| **Dependency Injection (DI)** | A design pattern where objects receive their dependencies from external code rather than creating them internally. |
| **Deque** | A double-ended queue from Python's `collections` module. Supports efficient append/pop from both ends. With `maxlen`, automatically drops the oldest item when full. |
| **Docker** | A platform for building, shipping, and running applications in containers. |
| **Docker Compose** | A tool for defining and running multi-container Docker applications using a YAML file. |
| **Docker Image** | A read-only template containing instructions for creating a Docker container. Built from a Dockerfile. |
| **Dockerfile** | A text file with instructions for building a Docker image. |
| **DOM (Document Object Model)** | The browser's internal representation of an HTML page as a tree of objects. React manipulates this tree to update the UI. |
| **Double-Checked Locking** | A threading pattern that checks a condition before and after acquiring a lock, minimizing lock contention. |
| **Embedding** | A numerical representation of text (or other data) as a vector, where similar content maps to nearby points in vector space. |
| **Endpoint** | A specific URL path + HTTP method combination that the API responds to (e.g., `GET /api/v1/health`). |
| **Environment Variable** | A key-value pair set in the operating system's environment, used to configure applications without hardcoding values. |
| **Event Loop** | The core mechanism of async programming. It continuously checks for and executes pending tasks, I/O callbacks, and timers. |
| **Facade Pattern** | A design pattern that provides a simplified interface to a complex subsystem. |
| **FastAPI** | A modern Python web framework for building APIs, with automatic documentation, type validation, and async support. |
| **Fetch API** | A modern JavaScript interface for making HTTP requests from the browser. |
| **Fixture** | In pytest, a function that provides test data or test infrastructure. Marked with `@pytest.fixture`. |
| **Float32** | A 32-bit floating-point number. Used for embedding vectors because it balances precision and memory usage. |
| **Hallucination** | When an LLM generates plausible-sounding but factually incorrect information. RAG reduces hallucination by grounding answers in real documents. |
| **HNSW (Hierarchical Navigable Small World)** | An algorithm for fast approximate nearest neighbor search in high-dimensional spaces. Used internally by ChromaDB. |
| **Hook (React)** | A special function (starting with `use`) that lets you add state, side effects, and other React features to function components. |
| **HTTP (HyperText Transfer Protocol)** | The standard protocol for communication between web browsers and servers. |
| **HTTPException** | A FastAPI exception class that returns an HTTP error response with a specific status code and message. |
| **JSX** | A syntax extension for JavaScript that looks like HTML. Used in React to describe UI structure. |
| **JSON (JavaScript Object Notation)** | A lightweight text format for representing structured data as key-value pairs. |
| **JWT (JSON Web Token)** | A compact, URL-safe way to represent claims between two parties. Commonly used for authentication. |
| **L2 Normalization** | Scaling a vector so its Euclidean length (L2 norm) equals 1. Makes cosine similarity equivalent to dot product. |
| **LangChain** | A Python framework for building applications with LLMs. Provides interfaces to many LLM providers. |
| **Lazy Loading** | A pattern where an object or resource is not created until it is first needed. Improves startup time. |
| **LLM (Large Language Model)** | An AI model trained on massive text data that can generate human-like text responses. Examples: GPT-4, Gemini, Claude. |
| **lru_cache** | A Python decorator that caches function return values. `maxsize=1` creates a singleton. |
| **Middleware** | Code that runs between receiving a request and executing the route handler. Used for cross-cutting concerns like CORS, rate limiting, and logging. |
| **Mock** | A test double that simulates the behavior of a real object. Used to isolate the unit being tested. |
| **Multipart Form Data** | An HTTP encoding format used for file uploads. Allows sending both files and text fields in a single request. |
| **Nearest Neighbor Search** | Finding the most similar items in a dataset based on distance in vector space. |
| **nginx** | A high-performance web server often used as a reverse proxy and static file server. |
| **Node.js** | A JavaScript runtime that allows running JavaScript outside the browser. Used for frontend build tools and development servers. |
| **npm** | Node Package Manager — the default package manager for Node.js. |
| **OCR (Optical Character Recognition)** | Technology that converts images of text into machine-readable text. |
| **ORM (Object-Relational Mapper)** | A technique that maps database tables to programming language objects, allowing database operations using object-oriented code. |
| **Path Parameter** | A variable part of a URL path (e.g., `{document_id}` in `/documents/{document_id}`). |
| **PDF (Portable Document Format)** | A file format for representing documents with fixed layout, fonts, and images. |
| **Polling** | Repeatedly checking for updates at regular intervals (e.g., every 3 seconds). |
| **Primary Key** | A column (or combination of columns) that uniquely identifies each row in a database table. |
| **Promise** | A JavaScript object representing the eventual completion (or failure) of an asynchronous operation. |
| **Props** | In React, the read-only inputs passed from a parent component to a child component. |
| **Pydantic** | A Python library for data validation and serialization using type annotations. |
| **PyMuPDF (fitz)** | A Python binding for the MuPDF PDF/XPS/EPUB rendering library. Used for fast PDF text extraction. |
| **pytest** | The most popular Python testing framework. Uses simple functions and assertions. |
| **RAG (Retrieval-Augmented Generation)** | A technique that improves LLM answers by first retrieving relevant information from a knowledge base and including it in the prompt. |
| **Rate Limiting** | Restricting the number of requests a client can make within a time period. Prevents abuse and protects expensive resources. |
| **React** | A JavaScript library for building user interfaces using a component-based, declarative approach. |
| **Ref (React)** | A mutable reference to a DOM element or value that persists across renders without causing re-renders. |
| **REST (Representational State Transfer)** | An architectural style for APIs that uses standard HTTP methods and URLs to represent resources and operations. |
| **Router** | In FastAPI, a group of related API endpoints. Routers can be mounted on the main app at a specific prefix. |
| **Schema** | A formal definition of data structure (fields, types, constraints). In this project, Pydantic models define request/response schemas. |
| **Semantic Search** | Finding content based on meaning rather than exact keyword matches. Powered by embeddings and vector similarity. |
| **SentenceTransformers** | A Python library for computing sentence and text embeddings using pre-trained transformer models. |
| **Session** | In databases: a connection to the database used for a series of operations. In chat: a conversation identified by a unique ID. |
| **Singleton** | A design pattern where only one instance of a class exists. Achieved with `@lru_cache(maxsize=1)` in this project. |
| **Sliding Window** | A technique where a fixed-size window moves across data, processing each position. Used in chunking with overlap. |
| **SlowAPI** | A FastAPI-compatible rate limiting library. Port of Flask-Limiter. |
| **SPA (Single Page Application)** | A web application that loads a single HTML page and dynamically updates content using JavaScript, without full page reloads. |
| **SQLAlchemy** | The most popular SQL toolkit and ORM for Python. |
| **SQLite** | A lightweight, serverless, file-based relational database. |
| **SSE (Server-Sent Events)** | A web technology where the server pushes updates to the client over a single HTTP connection. |
| **State (React)** | Data that can change over time within a component, causing re-renders when it changes. |
| **StrictMode (React)** | A development tool that renders components twice to detect side effects and warns about deprecated APIs. |
| **Swagger UI** | An interactive API documentation tool. FastAPI auto-generates it at `/docs`. |
| **Tailwind CSS** | A utility-first CSS framework that provides small, composable classes for styling. |
| **Token** | The smallest unit of text processed by an LLM. Typically a word or word fragment. |
| **Tree-Shaking** | Removing unused code from the final build. Tailwind CSS tree-shakes unused utility classes. |
| **TypeScript** | A superset of JavaScript that adds static type checking. Compiles to plain JavaScript. |
| **UUID (Universally Unique Identifier)** | A 128-bit identifier that is practically guaranteed to be unique. Format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`. |
| **Upsert** | A database operation that inserts a new record if it does not exist, or updates it if it does. |
| **Uvicorn** | An ASGI server for running Python async web applications. |
| **Vector** | An ordered list of numbers. In this project, vectors represent the semantic meaning of text. |
| **Vector Database** | A database optimized for storing and searching high-dimensional vectors. |
| **Virtual DOM** | React's lightweight in-memory representation of the actual DOM. React compares the virtual DOM with the real DOM and only updates what changed. |
| **Vite** | A modern build tool for web projects that provides instant development server startup and fast production builds. |
| **Volume (Docker)** | Persistent storage for Docker containers. Data in volumes survives container restarts. |
| **WebSocket** | A protocol that provides full-duplex (two-way) communication between browser and server over a single connection. |
| **XMLHttpRequest (XHR)** | An older browser API for making HTTP requests. Still useful for upload progress tracking, which `fetch` does not support. |
| **YAML** | A human-readable data serialization format used for configuration files (e.g., `docker-compose.yml`). |
| **Yield** | A Python keyword used in generators and context managers. In the `lifespan` function, `yield` separates startup code from shutdown code. |

---

> **End of Documentation**
>
> This documentation was written to be comprehensive and beginner-friendly. If you have questions, find errors, or want to add a section, please update this file directly. Good documentation is a living document — it grows with the project.
