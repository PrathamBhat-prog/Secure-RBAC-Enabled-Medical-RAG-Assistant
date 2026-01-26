# 🏥 RBAC-based RAG Medical Chatbot (Ollama + Groq)

A secure, role-based access control (RBAC) chatbot designed for healthcare platforms, powered by Retrieval-Augmented Generation (RAG) with FastAPI, MongoDB, Pinecone, and seamless integration with **local Ollama embeddings** and **Groq Cloud LLMs**.

![Thumbnail](./assets/thumbnail.png)

## 🧠 Overview

This project is a secure, role-sensitive chatbot that answers medical queries using advanced LLMs and vector-based document retrieval. It supports role-based access for **Doctors**, **Nurses**, **Patients**, and **Admins**, ensuring that sensitive medical information is retrieved and displayed based on user privileges.

What makes this project unique is its hybrid approach:
- **Embeddings**: Generated locally using **Ollama (nomic-embed-text)** for privacy and cost-efficiency.
- **LLM Inference**: Powered by **Groq Cloud (Llama-3.3-70b-versatile)** for lightning-fast responses.
- **Vector Search**: Managed by **Pinecone** for scalable similarity search.

---

![Application Flow](./assets/applicationFlow.png)

![Core Modules](./assets/coreModules.png)

[📄 View Full Project Report (PDF)](./assets/projectReport.pdf)

---

## ⚙️ Tech Stack

- **Backend:** FastAPI (Async & Modular)
- **Database:** MongoDB Atlas (User Management & Roles)
- **Vector DB:** Pinecone (knowledge base indexing)
- **LLM:** Groq API (Model: `llama-3.3-70b-versatile`)
- **Embeddings:** Ollama (Model: `nomic-embed-text`) - **Local Execution**
- **Authentication:** HTTP Basic Auth + bcrypt hashing
- **Frontend:** Streamlit

---

## 🧩 Core Modules

| Module        | Responsibility                                              |
| ------------- | ----------------------------------------------------------- |
| `server/auth/`| Handles user authentication (signup, login) & role verification |
| `server/chat/`| Manages RAG pipeline, context retrieval, and LLM inference  |
| `server/docs/`| PDF loading, chunking, and vector upsertion to Pinecone     |
| `server/embeddings/`| Custom extensive wrapper for local Ollama embeddings    |
| `server/config/`| Database connections (MongoDB)                            |
| `client/`     | Streamlit frontend for chat interface and admin uploads     |

---

## 🔐 Role-Based Access Flow

- **Admin:** Uploads documents and assigns visibility roles (e.g., "Only for Doctors").
- **Doctor/Nurse:** Can access specialized clinical documents and patient records.
- **Patient:** Can query general medical advice and their own accessible records.
- **Other/Guest:** Restricted to public health information only.

---

## 📡 API Endpoints

| Method | Route          | Description                         |
| ------ | -------------- | ----------------------------------- |
| POST   | `/signup`      | Register new users with roles       |
| GET    | `/login`       | Authenticate & retrieve token/role  |
| POST   | `/upload_docs` | (Admin/Doctor) Upload PDFs to RAG   |
| POST   | `/chat`        | Context-aware Q&A based on role     |

---

## 🚀 Getting Started

### 1. Prerequisites (Local AI Setup)

This project uses **Ollama** for local embeddings. You must have Ollama installed and running.

1.  **Install Ollama**: [Download here](https://ollama.com/)
2.  **Pull the Embedding Model**:
    ```bash
    ollama pull nomic-embed-text
    ```
3.  **Start the Ollama Server**:
    ```bash
    ollama serve
    ```

### 2. AWS/Cloud Setup
Ensure you have accounts for:
- **MongoDB Atlas** (Cluster URL)
- **Pinecone** (API Key & Index Name)
- **Groq Cloud** (API Key)

### 3. Clone the Repository

```bash
git clone https://github.com/PrathamBhat-prog/MedicalAssistant.git
cd rbac-medicalAssistant
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory (based on `.env.example` if available):

```env
# Database Configuration
MONGO_URI=mongodb+srv://<user>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority
DB_NAME=medical_db

# Vector Database (Pinecone)
PINECONE_API_KEY=your_pinecone_key_here
PINECONE_ENV=us-east-1                   # Your Pinecone region
PINECONE_INDEX_NAME=medical-rag          # Must match your index name

# AI Services
GROQ_API_KEY=gsk_...                     # Groq Cloud API Key
# Note: Google API Key is NO LONGER REQUIRED as we use Ollama.

# App Configuration
API_URL=http://127.0.0.1:8000            # Backend URL for Client
```

### 5. Setup Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate
```

### 6. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🏃‍♂️ Running the Application

You will need **three** terminal windows running simultaneously.

### Terminal 1: Ollama Server
(Ensure Ollama is running in the background)
```bash
ollama serve
```

### Terminal 2: Backend Server
```bash
# From root directory
uvicorn server.main:app --reload
```
*Server runs at `http://127.0.0.1:8000`*

### Terminal 3: Frontend Client
```bash
# From root directory
streamlit run client/main.py
```
*Client runs at `http://localhost:8501`*

---

## 🛠 Troubleshooting

**Ollama Connection Refused:**
- Ensure `ollama serve` is running.
- Verify `http://localhost:11434` is accessible.
- If using Docker, ensure the container can reach the host network.

**Pinecone Dimension Mismatch:**
- The `nomic-embed-text` model outputs **768** dimensions.
- Ensure your Pinecone index is created with `dimension=768`.

**MongoDB DNS Issues:**
- If you see SSL/DNS timeouts, try using the standard `mongodb://` connection string instead of `mongodb+srv://`.

---

## 🌱 Future Enhancements

- **JWT Auth**: Upgrade from Basic Auth to JWT for better security.
- **Hybrid Search**: Combine dense vector search with keyword search (BM25).
- **Citation Tracking**: Better highlighting of source documents in UI.
- **Docker Support**: Containerize the entire stack including Ollama.

---
