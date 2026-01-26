# 🏥 RBAC-based RAG Medical Chatbot

A secure, role-based access control (RBAC) chatbot designed for healthcare platforms, powered by Retrieval-Augmented Generation (RAG) with FastAPI, MongoDB, Pinecone, and LangChain.

![Thumbnail](./assets/thumbnail.png)

## 🧠 Overview

This project is a secure, role-sensitive chatbot that answers medical queries using LLMs and vector-based document retrieval. It supports role-based access for **Doctors**, **Nurses**, **Patients**, and **Admins**, ensuring that sensitive medical information is retrieved and displayed based on user privileges.

---

![Application Flow](./assets/applicationFlow.png)

![Core Modules](./assets/coreModules.png)

[📄 View Full Project Report (PDF)](./assets/projectReport.pdf)

---

## ⚙️ Tech Stack

- **Backend:** FastAPI (modular)
- **Database:** MongoDB Atlas (for users)
- **Vector DB:** Pinecone (RAG context)
- **LLM:** Groq API using LLaMA-3
- **Embeddings:** Google Generative AI Embeddings
- **Authentication:** HTTP Basic Auth + bcrypt
- **Frontend:** Streamlit

---

## 🧩 Core Modules

| Module      | Responsibility                                              |
| ----------- | ----------------------------------------------------------- |
| `auth/`     | Handles authentication (signup, login), hashing with bcrypt |
| `chat/`     | Manages chat routes and query answering logic using RAG     |
| `vectordb/` | Document loading, chunking, and Pinecone indexing           |
| `database/` | MongoDB setup and user operations                           |
| `main.py`   | Entry point for FastAPI app with route inclusion            |

---

## 🔐 Role-Based Access Flow

- **Admin:** Uploads documents and assigns roles.
- **Doctor/Nurse:** Retrieves clinical documents specific to their role.
- **Patient:** Can query general medical info (restricted access).
- **Other/Guest:** Limited access to public health content.

---

## 📡 API Endpoints

| Method | Route          | Description                         |
| ------ | -------------- | ----------------------------------- |
| POST   | `/signup`      | Register new users                  |
| GET    | `/login`       | Login with HTTP Basic Auth          |
| POST   | `/upload_docs` | Admin-only endpoint to upload files |
| POST   | `/chat`        | Role-sensitive chatbot Q&A          |

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/rbac-medicalAssistant.git
cd rbac-medicalAssistant
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory and add the following:

```env
# Database Configuration
MONGO_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority
DB_NAME=medical_db

# Vector Database (Pinecone)
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENV=us-east-1                   # Your Pinecone environment region
PINECONE_INDEX_NAME=medical-rag          # Your Index Name

# AI Services
GOOGLE_API_KEY=your_google_ai_key        # For Embeddings
GROQ_API_KEY=your_groq_api_key           # For LLM Inference

# App Configuration
API_URL=http://127.0.0.1:8000            # Backend URL for the Frontend to connect
```

### 3. Setup Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🏃‍♂️ Running the Application

You will need two terminals running simultaneously.

### Terminal 1: Backend Server

```bash
# Navigate to root directory
# Ensure venv is activated
uvicorn server.main:app --reload
```
*Server runs at `http://127.0.0.1:8000`*

### Terminal 2: Frontend Client

```bash
# Navigate to root directory
# Ensure venv is activated
streamlit run client/main.py
```
*Client runs at `http://localhost:8501`*

---

## 🛠 Troubleshooting

**MongoDB Connection Issues:**
If you see "DNS Timeout" or "SSL Handshake Failed", your network might be blocking SRV records.
1. Go to MongoDB Atlas -> Connect -> Drivers.
2. Select **Older Version** to get the **Standard Connection String** (starts with `mongodb://` instead of `mongodb+srv://`).
3. Replace `MONGO_URI` in your `.env` file with this string.

---

## 🌱 Future Enhancements

- Add JWT-based Auth + Refresh Tokens
- Document download/preview functionality
- Audit logs for medical compliance
- **🧍️‍ Contributions are welcome! Feel free to fork and submit PRs.**

---

© 2025 [Supratim / sn dev] — All rights reserved.
