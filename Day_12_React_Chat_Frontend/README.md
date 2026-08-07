# Day 12 — React Chat Frontend

A React-based chat frontend developed as part of the NLP Internship.  
The frontend is connected to the FastAPI Chat Server developed in Day 11.

## Overview

This project demonstrates how a React frontend communicates with a FastAPI backend through a REST API.

### Features

- React + Vite frontend
- Chat message interface
- User and assistant message bubbles
- Message input and send button
- React state management using `useState`
- FastAPI backend integration
- Fetch API for sending requests
- Typing indicator
- Responsive and modern UI

## Technologies Used

- React
- Vite
- JavaScript
- CSS
- FastAPI
- REST API
- Fetch API

## Project Structure

```text
day12-react-chat-frontend/
│
├── src/
│   ├── components/
│   │   ├── ChatMessage.jsx
│   │   ├── ChatMessage.css
│   │   ├── MessageInput.jsx
│   │   └── MessageInput.css
│   │
│   ├── App.jsx
│   ├── App.css
│   ├── index.css
│   └── main.jsx
│
├── public/
├── package.json
├── package-lock.json
├── vite.config.js
└── README.md
How to Run
1. Install Dependencies
npm install
2. Start the FastAPI Backend

From the Day 11 FastAPI project:

python -m uvicorn app:app --reload

Backend:

http://127.0.0.1:8000
3. Start the React Frontend

From the Day 12 project:

npm run dev

Frontend:

http://localhost:5173

Both the frontend and backend should be running at the same time.

API Integration

The frontend sends messages to:

POST /api/chat

Example request:

{
  "session_id": "react-demo-session",
  "message": "Hello"
}

The current backend returns a mock response for testing:

{
  "session_id": "react-demo-session",
  "response": "You said: Hello"
}

A real AI/LLM can be connected to the backend in the future.

What I Learned
React components and JSX
Props and useState
Event handling
Fetch API
REST API communication
Connecting React with FastAPI
CSS styling and animations
Building a responsive chat interface