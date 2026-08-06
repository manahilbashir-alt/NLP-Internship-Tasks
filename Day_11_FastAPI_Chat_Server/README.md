# Day 11 - FastAPI Chat Server

## Overview

This project is a simple AI Chat Server built using **FastAPI** and **Pydantic**. It demonstrates how to build REST APIs, validate request and response data, manage in-memory chat sessions, implement structured logging, and handle HTTP errors.

The project was developed as part of an NLP Internship Day 11.

---

## Features

- FastAPI REST API
- POST `/api/chat` endpoint
- GET `/api/sessions` endpoint
- Pydantic request and response models
- In-memory chat session storage
- Automatic session creation
- Conversation history management
- System prompt initialization
- Structured logging
- HTTP error handling (400, 404, 500)
- Interactive Swagger UI

---

## Project Structure

```
Day_11_FastAPI_Chat_Server/
│
├── app.py
├── models.py
├── requirements.txt
└── README.md
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/manahilbashir-alt/NLP-Internship-Week-1.git
```

Navigate to the project folder:

```bash
cd Day_11_FastAPI_Chat_Server
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment:

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Running the Server

Start the FastAPI server using:

```bash
uvicorn app:app --reload
```

The server will run at:

```
http://127.0.0.1:8000
```

Swagger Documentation:

```
http://127.0.0.1:8000/docs
```

ReDoc Documentation:

```
http://127.0.0.1:8000/redoc
```

---

## API Endpoints

### POST `/api/chat`

Creates or continues a chat session.

### Request

```json
{
    "session_id": "A123",
    "message": "Hello"
}
```

### Response

```json
{
    "response": "You said: Hello"
}
```

---

### GET `/api/sessions`

Returns all active chat sessions along with their message counts.

Example Response:

```json
[
    {
        "session_id": "A123",
        "message_count": 3
    }
]
```

---

### GET `/api/sessions/{session_id}`

Returns the complete conversation history for a specific session.

Example Response:

```json
{
    "session_id": "A123",
    "history": [
        {
            "role": "system",
            "content": "You are a helpful AI assistant."
        },
        {
            "role": "user",
            "content": "Hello"
        },
        {
            "role": "assistant",
            "content": "You said: Hello"
        }
    ]
}
```

---

## Session Management

The application stores chat history in memory using a Python dictionary.

Example:

```python
chat_sessions = {
    "A123": [
        {
            "role": "system",
            "content": "You are a helpful AI assistant."
        },
        {
            "role": "user",
            "content": "Hello"
        },
        {
            "role": "assistant",
            "content": "You said: Hello"
        }
    ]
}
```

> Note: Since the session store is in memory, all conversations are cleared when the server restarts.

---

## Logging

Each request records structured information including:

- Timestamp
- Session ID
- Model Name
- Token Usage
- Latency (milliseconds)

---

## Error Handling

The API supports structured error responses for:

- **400 Bad Request** – Invalid or empty input.
- **404 Not Found** – Session not found.
- **500 Internal Server Error** – Unexpected server errors.

---

## Technologies Used

- Python 3
- FastAPI
- Pydantic
- Uvicorn

---

## Learning Outcomes

Through this project, the following concepts were implemented:

- REST API Development
- FastAPI Routing
- Pydantic Models
- Request Validation
- Response Models
- Session Management
- In-Memory Data Storage
- Structured Logging
- Exception Handling
- Interactive API Documentation using Swagger
