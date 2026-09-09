# RBAC-based RAG Medical Chatbot (Ollama + Groq)

A secure, role-based access control (RBAC) chatbot designed for healthcare platforms, powered by Retrieval-Augmented Generation (RAG) with FastAPI, **Supabase PostgreSQL**, Pinecone, local **Ollama embeddings**, and **Groq Cloud LLMs**.

![Thumbnail](./assets/thumbnail.png)

## Overview

This project is a role-sensitive chatbot that answers medical queries using LLMs and vector document retrieval. It supports **Doctors**, **Nurses**, **Patients**, and **Admins**, so retrieved context is limited to documents the signed-in role is allowed to see.

Hybrid setup:
- **Embeddings**: Local **Ollama (`nomic-embed-text`)** for privacy and cost control.
- **LLM Inference**: **Groq Cloud** (default `openai/gpt-oss-120b`) for fast responses.
- **Vector Search**: **Pinecone**, with metadata filters applied **at query time** (not after retrieval).
- **Users & roles**: **Supabase PostgreSQL**.

![Application Flow](./assets/applicationFlow.png)

![Core Modules](./assets/coreModules.png)

[View Full Project Report (PDF)](./assets/projectReport.pdf)

## Tech Stack

- **Backend:** FastAPI
- **Database:** Supabase PostgreSQL (users and roles)
- **Vector DB:** Pinecone
- **LLM:** Groq API (default `openai/gpt-oss-120b`; override with `GROQ_MODEL`)
- **Embeddings:** Ollama (`nomic-embed-text`)
- **Authentication:** HTTP Basic Auth + bcrypt
- **Frontend:** Streamlit

## Core Modules

| Module | Responsibility |
| --- | --- |
| `server/auth/` | Signup, login, bcrypt hashing, role checks |
| `server/chat/` | RAG pipeline with Pinecone role filters and Groq |
| `server/docs/` | PDF loading, chunking, and upsert to Pinecone |
| `server/embeddings/` | HTTP wrapper for local Ollama embeddings |
| `server/config/` | Supabase PostgreSQL connection pool and schema |
| `client/` | Streamlit UI for auth, admin/doctor uploads, and chat |

## Role-Based Access Flow

- **Admin:** Uploads documents, assigns visibility, can retrieve all roles.
- **Doctor:** Can upload documents; can retrieve doctor, nurse, patient, and public (`other`) docs.
- **Nurse:** Can retrieve nurse, patient, and public docs.
- **Patient:** Can retrieve patient and public docs.
- **Other:** Restricted to public (`other`) documents.

Retrieval uses Pinecone metadata `filter` so unauthorized chunks never enter the top-k results.

## API Endpoints

| Method | Route | Description |
| --- | --- | --- |
| GET | `/health` | API and database status |
| POST | `/signup` | Register a user with a valid role |
| GET | `/login` | Authenticate with HTTP Basic Auth |
| POST | `/upload_docs` | Admin/Doctor PDF upload into the RAG index |
| POST | `/chat` | Role-aware Q&A |

## Getting Started

### 1. Local embeddings (Ollama)

1. Install Ollama: https://ollama.com/
2. Pull the embedding model:

```bash
ollama pull nomic-embed-text
```

3. Start Ollama:

```bash
ollama serve
```

### 2. Cloud accounts

- **Supabase** (PostgreSQL connection string)
- **Pinecone** (API key and index name, dimension **768**)
- **Groq Cloud** (API key)

### 3. Clone the repository

```bash
git clone https://github.com/PrathamBhat-prog/Secure-RBAC-Enabled-Medical-RAG-Assistant.git
cd Secure-RBAC-Enabled-Medical-RAG-Assistant
```

### 4. Environment variables

Copy `.env.example` to `.env` in the project root:

```env
# Supabase PostgreSQL (session pooler is IPv4-friendly; SSL required)
# Username must be postgres.<project-ref> when using *.pooler.supabase.com
DATABASE_URL=postgresql://postgres.YOUR-PROJECT-REF:[YOUR-PASSWORD]@aws-0-YOUR-REGION.pooler.supabase.com:5432/postgres?sslmode=require

# Vector Database (Pinecone)
PINECONE_API_KEY=your_pinecone_key_here
PINECONE_ENV=us-east-1
PINECONE_INDEX_NAME=medical-rag

# AI Services
GROQ_API_KEY=gsk_...
GROQ_MODEL=openai/gpt-oss-120b

# Backend URL used by the Streamlit client
API_URL=http://127.0.0.1:8001
```

The `users` table is created automatically on API startup.

### 5. Python environment

```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

## Running the Application

Use three processes (or `start_app.bat` on Windows).

### Terminal 1: Ollama

```bash
ollama serve
```

### Terminal 2: Backend

```bash
cd server
uvicorn main:app --reload --port 8001
```

API: `http://127.0.0.1:8001`

### Terminal 3: Frontend

From the project root:

```bash
streamlit run client/main.py
```

Client: `http://localhost:8501`

Windows shortcut from the project root:

```bat
start_app.bat
```

## Troubleshooting

**Ollama connection refused**
- Confirm `ollama serve` is running and `http://localhost:11434` responds.
- Confirm `nomic-embed-text` is pulled.

**Pinecone dimension mismatch**
- `nomic-embed-text` produces **768** dimensions.
- Create the index with `dimension=768`. The app will not delete an existing mismatched index.

**Supabase / Postgres connection**
- Direct `db.<project>.supabase.co:5432` is IPv6-only on many free projects.
- On IPv4-only networks, use the **session pooler** (`aws-0-<region>.pooler.supabase.com:5432`) with username `postgres.<project-ref>`.
- Always include `sslmode=require`. URL-encode the password if it has special characters.

**Client cannot reach API**
- `API_URL` in `.env` must match the uvicorn port (default `8001`).

## Interview prep (local only)

Generate a **project guide PDF** and **interview cheat sheet** (same pattern as the stock analyser repo):

```bash
python private/generate_deliverables.py
```

Outputs (gitignored under `private/deliverables/`):

- `Medical_RAG_Assistant_Project_Guide.pdf` — architecture, RBAC design, tradeoffs, bugs fixed
- `Interview_Cheat_Sheet.docx` — 30/60/90s pitches, Q&A, demo script

The script also refreshes `assets/projectReport.pdf` linked from this README.

## Future Enhancements

- JWT instead of HTTP Basic Auth
- Hybrid dense + keyword search
- Stronger citation highlighting in the UI
- Docker Compose for API, client, and Ollama
