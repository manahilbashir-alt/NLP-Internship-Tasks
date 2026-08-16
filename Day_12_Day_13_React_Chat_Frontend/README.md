# Day 12 — React Chat Frontend

A modern React-based chat frontend built as part of the **NLP Internship**. This project provides a user-friendly chat interface that connects with the FastAPI backend developed in Day 11.

The application supports chat messaging, multiple chat sessions, session management, message history, and a live typing indicator.

---

## 📌 Project Overview

The goal of this project is to build a functional frontend for an AI/chat application using **React** and integrate it with a **FastAPI REST API** backend.

The React application communicates with the backend through HTTP requests and provides an interactive chat experience.

### Architecture

```text
React Frontend
      │
      │ HTTP Requests
      ▼
FastAPI Backend
      │
      │
      ▼
Gemini API
```

---

## ✨ Features

* 💬 Real-time-style chat interface
* 🗂️ Multiple chat sessions
* ➕ Create a new chat
* 🔄 Switch between conversations
* 🗑️ Manage chat sessions
* 💾 Persistent frontend state using local storage
* ⌨️ Typing/loading indicator
* 📜 Message history
* 🔗 FastAPI backend integration
* 🤖 Gemini-powered responses
* 📱 Responsive and clean user interface
* 🔐 Environment variables for API configuration

---

## 🛠️ Technologies Used

### Frontend

* React
* JavaScript
* CSS
* Vite
* React Hooks

### Backend

* Python
* FastAPI
* Pydantic
* Uvicorn

### AI

* Google Gemini API

### Development Tools

* Visual Studio Code
* Git
* GitHub
* npm

---

## 📁 Project Structure

```text
Day_12_React_Chat_Frontend/
│
├── src/
│   ├── components/
│   │   ├── Sidebar.jsx
│   │   ├── ChatMessage.jsx
│   │   └── MessageInput.jsx
│   │
│   ├── App.jsx
│   ├── main.jsx
│   └── ...
│
├── public/
│
├── .env
├── .gitignore
├── package.json
├── package-lock.json
├── vite.config.js
└── README.md
```

> The exact files may vary depending on the final project structure.

---

## 🔐 Environment Variables

The project uses environment variables for sensitive configuration such as the Gemini API key.

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

**Never upload your `.env` file or API keys to GitHub.**

Make sure `.gitignore` contains:

```gitignore
.env
.env.*
node_modules/
dist/
```

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

### 2. Navigate to the project

```bash
cd Day_12_React_Chat_Frontend
```

### 3. Install dependencies

```bash
npm install
```

### 4. Configure environment variables

Create the `.env` file and add your Gemini API key.

```env
GEMINI_API_KEY=your_api_key_here
```

---

## ▶️ Running the Frontend

Start the React development server:

```bash
npm run dev
```

Vite will provide a local development URL, usually:

```text
http://localhost:5173
```

Open the URL in your browser.

---

## 🔗 Backend Integration

The frontend communicates with the FastAPI backend developed in **Day 11 — FastAPI Chat Server**.

The backend provides endpoints such as:

```text
POST /api/chat
GET  /api/sessions
```

### Send a message

Example request:

```json
{
  "session_id": "session_1",
  "message": "Hello"
}
```

Example response:

```json
{
  "response": "You said: Hello"
}
```

The React frontend sends the user's message to the backend and displays the returned response in the chat interface.

---

## 🗂️ Multi-Session Chat

The application supports multiple conversations.

Users can:

1. Create a new chat session.
2. Select an existing conversation.
3. Send messages within the selected session.
4. Maintain separate conversation histories.
5. Switch between different sessions.

This allows the application to behave more like a complete chat application rather than a single-message interface.

---

## 💾 Local Storage

The frontend uses browser local storage to persist relevant chat/session information.

This helps preserve the user's conversations when the page is refreshed during development.

---

## ⌨️ Typing Indicator

While waiting for a response from the backend, the interface displays a typing/loading indicator.

This provides visual feedback to the user that the request is being processed.

---

## 🔄 Application Flow

```text
User enters message
        │
        ▼
React MessageInput
        │
        ▼
App.jsx
        │
        ▼
POST /api/chat
        │
        ▼
FastAPI Backend
        │
        ▼
Gemini / Chat Logic
        │
        ▼
Backend Response
        │
        ▼
React State Update
        │
        ▼
ChatMessage
        │
        ▼
Response displayed
```

---

## 🧪 Testing

The application can be tested by:

### Test 1 — Basic Chat

Send:

```text
Hello
```

Expected result:

The message should appear in the chat and the backend should return a response.

### Test 2 — Multiple Messages

Send:

```text
What is NLP?
```

Then:

```text
What are transformers?
```

The messages should appear in the correct order.

### Test 3 — Multiple Sessions

1. Create a new chat.
2. Send a message.
3. Create another chat.
4. Send a different message.
5. Switch between sessions.

Each session should maintain its own conversation.

### Test 4 — Page Refresh

Refresh the browser and verify that the stored session/chat information is preserved according to the application's local-storage implementation.

---

## ⚠️ Security

API keys and other secrets should **never** be committed to GitHub.

The following files should remain private:

```text
.env
```

Use `.gitignore` to prevent accidental uploads.

If an API key is accidentally exposed publicly, revoke it and generate a new one.

---

## 📚 Learning Outcomes

Through this project, I practiced:

* React component development
* React Hooks
* State management
* API integration
* REST API communication
* Async JavaScript
* Multi-session chat architecture
* Local storage
* Loading/typing states
* Frontend and backend integration
* Environment variable management
* Git and GitHub workflow

---

## 📌 Internship Task

**Internship:** NLP Internship
**Day:** 12
**Task:** React Chat Frontend

This project builds upon the FastAPI Chat Server developed in Day 11 and demonstrates full-stack integration between a React frontend and a Python FastAPI backend.

---

## 👩‍💻 Author

**Manahil Bashir**

Computer Science Student
FAST-NUCES


This project was created for educational and internship purposes.
