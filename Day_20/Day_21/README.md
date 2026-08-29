# Day 21 — Conversational RAG Application

A complete **Conversational Retrieval-Augmented Generation (RAG)** application that allows users to upload documents and ask questions about their content through a web-based chat interface.

The application combines **FastAPI, React, Sentence Transformers, ChromaDB, and Google Gemini** to provide document-grounded conversational question answering.

---

## 📌 Project Overview

Traditional question-answering systems rely only on the knowledge stored inside an LLM. A RAG system improves this by first retrieving relevant information from a user's documents and then providing that information to the language model as context.

This project implements a complete conversational RAG pipeline:

```text
User
 │
 ▼
React Frontend
 │
 ▼
FastAPI Backend
 │
 ├── Document Ingestion
 │      │
 │      ├── PDF / DOCX / TXT
 │      ├── Text Extraction
 │      └── Chunking
 │
 ├── Embedding Generation
 │      │
 │      ▼
 │   Sentence Transformers
 │
 ├── Vector Storage
 │      │
 │      ▼
 │   ChromaDB
 │
 └── Conversational Chat
        │
        ├── Retrieve Relevant Chunks
        ├── Conversation History
        └── Gemini 3.6 Flash
                 │
                 ▼
          Grounded Answer
                 │
                 ▼
          React Chat Interface
```

---

## 🎯 Objectives

The main objectives of Day 21 were:

* Build a complete conversational RAG application.
* Support document uploading through a web interface.
* Extract text from PDF, DOCX, and TXT files.
* Split documents into manageable chunks.
* Generate vector embeddings for document chunks.
* Store embeddings in ChromaDB.
* Retrieve relevant document chunks for user questions.
* Maintain conversation/session history.
* Generate grounded answers using Google Gemini.
* Build a React-based frontend.
* Connect the React frontend with the FastAPI backend.
* Expose the RAG system through REST API endpoints.

---

## ✨ Features

### 📄 Document Upload

Users can upload:

* PDF
* DOCX
* TXT

The backend processes the uploaded document automatically.

### ✂️ Text Chunking

Extracted document text is divided into smaller chunks before embedding and storage.

### 🧠 Semantic Embeddings

The project uses:

```text
sentence-transformers
```

to convert document chunks and user questions into numerical vector representations.

### 🗄️ ChromaDB Vector Database

Document embeddings are stored in **ChromaDB** for efficient semantic similarity search.

### 🔎 Context Retrieval

For every user question, the system retrieves the most relevant document chunks using vector similarity.

The default configuration retrieves:

```text
Top K = 3
```

relevant chunks.

### 💬 Conversational Memory

The application maintains session-based conversation history.

This allows follow-up questions to use previous conversation context.

Example:

```text
User:
Where is PlanetBeyond located?

Assistant:
[Answer from document]

User:
What services do they provide?

Assistant:
[Answer using the document + conversation context]
```

### 🤖 Gemini-Powered Generation

The retrieved document context is passed to:

```text
Gemini 3.6 Flash
```

The model is instructed to answer using the retrieved document context and avoid inventing information.

### 🌐 React Web Interface

The frontend provides:

* Document upload
* Chat interface
* User messages
* Assistant responses
* Loading states
* Uploaded document/source list
* Session identification

### 🔌 REST API

FastAPI exposes endpoints for:

* Health checking
* Document ingestion
* RAG chat
* Source listing
* Conversation history

---

## 🏗️ Project Structure

```text
Day_21/
│
├── backend/
│   │
│   ├── venv/
│   │
│   ├── src/
│   │
│   ├── data/
│   │   ├── chroma_db/
│   │   └── uploads/
│   │
│   ├── api.py
│   ├── chat.py
│   ├── ingestion.py
│   ├── rag.py
│   └── requirements.txt
│
├── frontend/
│   │
│   ├── node_modules/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   │
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.js
│   └── eslint.config.js
│
├── data/
│   ├── chroma_db/
│   └── uploads/
│
├── evaluation/
│   └── results/
│
├── README.md
└── requirements.txt
```

> **Note:** Virtual environments, generated databases, uploaded documents, API keys, and other local/generated files should not be committed to GitHub.

---

# ⚙️ Technologies Used

| Technology            | Purpose                         |
| --------------------- | ------------------------------- |
| Python                | Backend development             |
| FastAPI               | REST API                        |
| Uvicorn               | ASGI server                     |
| React                 | Frontend                        |
| Vite                  | Frontend development/build tool |
| ChromaDB              | Vector database                 |
| Sentence Transformers | Embeddings                      |
| Google Gemini         | Answer generation               |
| python-dotenv         | Environment variable management |
| PyPDF                 | PDF processing                  |
| python-docx           | DOCX processing                 |
| Pydantic              | Request validation              |
| JavaScript            | Frontend logic                  |
| CSS                   | Frontend styling                |

---

# 🔄 RAG Workflow

The application follows the standard Retrieval-Augmented Generation workflow.

## 1. Document Upload

The user uploads a document through the React frontend.

```text
PDF / DOCX / TXT
        ↓
FastAPI
```

## 2. Text Extraction

The backend extracts readable text from the uploaded document.

```text
Document
   ↓
Text Extraction
   ↓
Raw Text
```

## 3. Chunking

The extracted text is divided into smaller chunks.

```text
Raw Text
   ↓
Chunking
   ↓
Chunk 1
Chunk 2
Chunk 3
...
```

## 4. Embedding Generation

Each chunk is converted into a vector representation using Sentence Transformers.

```text
Text Chunk
    ↓
Embedding Model
    ↓
Vector
```

## 5. Vector Storage

The embeddings and document metadata are stored in ChromaDB.

```text
Embedding
    +
Metadata
    +
Document Chunk
        ↓
    ChromaDB
```

## 6. User Question

The user asks a question through the chat interface.

```text
User Question
      ↓
React
      ↓
FastAPI
```

## 7. Query Embedding

The question is converted into an embedding using the same embedding model.

```text
Question
   ↓
Embedding Model
   ↓
Query Vector
```

## 8. Similarity Search

The query vector is compared against stored vectors.

```text
Query Vector
     ↓
ChromaDB
     ↓
Top-K Relevant Chunks
```

## 9. Context Construction

The retrieved chunks and conversation history are added to the prompt.

```text
Conversation History
        +
Retrieved Documents
        +
User Question
        ↓
     Prompt
```

## 10. Gemini Generation

The prompt is sent to Gemini.

```text
Prompt
   ↓
Gemini 3.6 Flash
   ↓
Grounded Answer
```

## 11. Response

The answer and retrieved sources are returned to the React frontend.

```text
Gemini
  ↓
FastAPI
  ↓
React
  ↓
User
```

---

# 🔐 Environment Configuration

The Gemini API key is stored in a `.env` file.

Inside:

```text
backend/.env
```

add:

```env
GEMINI_API_KEY=your_gemini_api_key
```

The application loads the key using `python-dotenv`.

### Important

Never commit `.env` to GitHub.

The `.gitignore` file should contain:

```gitignore
.env
venv/
.venv/
__pycache__/
*.pyc
node_modules/
.vscode/
*.log
```

---

# 📦 Backend Installation

Navigate to the backend directory:

```powershell
cd Day_21\backend
```

Create a virtual environment if required:

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

---

# ▶️ Running the Backend

From:

```text
Day_21/backend
```

run:

```powershell
.\venv\Scripts\python.exe -m uvicorn api:app --reload
```

The backend will run at:

```text
http://127.0.0.1:8000
```

FastAPI interactive documentation:

```text
http://127.0.0.1:8000/docs
```

Health endpoint:

```text
http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "healthy"
}
```

---

# 💻 Frontend Installation

Navigate to:

```powershell
cd Day_21\frontend
```

Install dependencies:

```powershell
npm install
```

Start the development server:

```powershell
npm run dev
```

The frontend will run at:

```text
http://localhost:5173
```

---

# 🔌 API Endpoints

## Root

```http
GET /
```

Returns the API status.

---

## Health Check

```http
GET /health
```

Checks whether the backend is healthy.

Example:

```json
{
  "status": "healthy"
}
```

---

## Document Ingestion

```http
POST /api/rag/ingest
```

Uploads and processes a document.

Supported:

```text
.pdf
.docx
.txt
```

The endpoint:

1. Saves the uploaded document.
2. Extracts text.
3. Splits the text into chunks.
4. Generates embeddings.
5. Stores the chunks in ChromaDB.
6. Returns ingestion information.

Example response:

```json
{
  "message": "Document ingested successfully",
  "filename": "example.pdf",
  "characters": 12500,
  "chunks": 15
}
```

---

## Conversational Chat

```http
POST /api/rag/chat
```

Request:

```json
{
  "session_id": "session-123",
  "question": "Where is PlanetBeyond located?",
  "top_k": 3
}
```

The backend retrieves relevant document chunks and generates a grounded response using Gemini.

---

## Sources

```http
GET /api/rag/sources
```

Returns documents currently available in the vector store.

---

## Conversation History

```http
GET /api/rag/chat/{session_id}/history
```

Returns the conversation history associated with a session.

---

# 🧪 Example RAG Interaction

### User Question

```text
Where is PlanetBeyond located?
```

### Processing

```text
Question
   ↓
Query Embedding
   ↓
ChromaDB Search
   ↓
Relevant PlanetBeyond Chunks
   ↓
Gemini
   ↓
Grounded Answer
```

### Result

The assistant generates an answer based on the retrieved document context rather than relying on unrelated external information.

---

# 🧠 Conversational RAG

Unlike a basic RAG system, this application maintains conversation history using a session ID.

Each session stores:

```text
User Message
      ↓
Assistant Response
      ↓
User Follow-up
      ↓
Assistant Response
```

The most recent conversation messages are included when generating subsequent answers.

This allows the system to handle contextual follow-up questions.

---

# 🛡️ Grounding and Hallucination Control

The Gemini prompt explicitly instructs the model to:

* Use only retrieved document context.
* Avoid inventing facts.
* Say when information is unavailable.
* Use conversation history when necessary.
* Avoid using outside knowledge.

This makes the system more suitable for document-based question answering.

---

# 📊 Validation

The application was tested through the complete pipeline:

```text
Document Upload
       ↓
Text Extraction
       ↓
Chunking
       ↓
Embedding
       ↓
ChromaDB Storage
       ↓
Question
       ↓
Retrieval
       ↓
Gemini Generation
       ↓
Answer
       ↓
React UI
```

The backend health endpoint was verified successfully, and the frontend was successfully connected to the FastAPI backend.

---

# 🚀 Future Improvements

Possible future improvements include:

* Streaming Gemini responses.
* Improved conversation persistence using a database.
* Authentication and user accounts.
* Better source citation display.
* Drag-and-drop document upload.
* Multiple document collections.
* Advanced hybrid retrieval.
* Reranking retrieved chunks.
* Conversation export.
* Deployment using Docker.
* Cloud deployment.
* Evaluation using a larger question-answer dataset.

---

# 📚 Key Concepts Learned

Through this project, the following concepts were implemented:

* Retrieval-Augmented Generation
* Conversational RAG
* Semantic Search
* Vector Embeddings
* Vector Databases
* ChromaDB
* Sentence Transformers
* Document Chunking
* Context Retrieval
* Prompt Construction
* LLM Grounding
* Session Memory
* FastAPI REST APIs
* React Frontend Development
* Frontend–Backend Integration
* CORS
* Environment Variables
* Gemini API Integration

---

# 👩‍💻 Internship Project

**Day:** 21
**Project:** Conversational RAG Application
**Focus:** End-to-End Retrieval-Augmented Generation

This project represents the implementation of a complete document-based conversational AI system, combining retrieval, vector search, LLM generation, session memory, backend APIs, and a web frontend.
