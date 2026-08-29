import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [file, setFile] = useState(null);
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);

  const [sessionId] = useState(
    () => `session-${Date.now()}`
  );

  useEffect(() => {
    checkBackend();
    loadSources();
  }, []);

  async function checkBackend() {
    try {
      const response = await fetch(`${API_URL}/health`);

      if (!response.ok) {
        throw new Error("Backend unavailable");
      }

      console.log("Backend connected");
    } catch (error) {
      console.error("Backend connection failed:", error);
    }
  }

  async function loadSources() {
    try {
      const response = await fetch(
        `${API_URL}/api/rag/sources`
      );

      const data = await response.json();

      setSources(data.sources || []);
    } catch (error) {
      console.error("Could not load sources:", error);
    }
  }

  async function uploadDocument() {
    if (!file) {
      alert("Please select a document first.");
      return;
    }

    const formData = new FormData();

    formData.append("file", file);

    setUploading(true);

    try {
      const response = await fetch(
        `${API_URL}/api/rag/ingest`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Upload failed"
        );
      }

      alert(
        `${data.filename} uploaded successfully.\n` +
        `${data.chunks} chunks created.`
      );

      setFile(null);

      loadSources();

    } catch (error) {
      alert(error.message);
    } finally {
      setUploading(false);
    }
  }

  async function sendQuestion() {
    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || loading) {
      return;
    }

    const userMessage = {
      role: "user",
      content: trimmedQuestion,
    };

    setMessages((previous) => [
      ...previous,
      userMessage,
    ]);

    setQuestion("");
    setLoading(true);

    try {
      const response = await fetch(
        `${API_URL}/api/rag/chat`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            session_id: sessionId,
            question: trimmedQuestion,
            top_k: 3,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to get answer"
        );
      }

      const assistantMessage = {
        role: "assistant",
        content:
          data.answer ||
          data.response ||
          JSON.stringify(data),
      };

      setMessages((previous) => [
        ...previous,
        assistantMessage,
      ]);

    } catch (error) {
      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: `Error: ${error.message}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(event) {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();
      sendQuestion();
    }
  }

  return (
    <div className="app">

      <header className="header">
        <div>
          <h1>Conversational RAG</h1>
          <p>
            Ask questions about your documents
          </p>
        </div>

        <div className="status">
          <span className="status-dot"></span>
          Backend Connected
        </div>
      </header>

      <main className="main">

        <section className="upload-card">

          <h2>Upload Document</h2>

          <p>
            Supported formats: PDF, DOCX, TXT
          </p>

          <div className="upload-row">

            <input
              type="file"
              accept=".pdf,.docx,.txt"
              onChange={(event) =>
                setFile(event.target.files[0])
              }
            />

            <button
              onClick={uploadDocument}
              disabled={uploading}
            >
              {uploading
                ? "Uploading..."
                : "Upload"}
            </button>

          </div>

          {file && (
            <p className="selected-file">
              Selected: {file.name}
            </p>
          )}

        </section>

        <div className="content">

          <section className="chat-card">

            <div className="chat-header">
              <h2>Chat</h2>

              <span>
                Session: {sessionId.slice(-8)}
              </span>
            </div>

            <div className="messages">

              {messages.length === 0 && (
                <div className="empty-chat">
                  <h3>Start a conversation</h3>

                  <p>
                    Upload a document and ask a
                    question about its content.
                  </p>
                </div>
              )}

              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`message ${message.role}`}
                >
                  <div className="message-label">
                    {message.role === "user"
                      ? "You"
                      : "RAG Assistant"}
                  </div>

                  <div className="message-content">
                    {message.content}
                  </div>
                </div>
              ))}

              {loading && (
                <div className="message assistant">
                  <div className="message-label">
                    RAG Assistant
                  </div>

                  <div className="message-content">
                    Thinking...
                  </div>
                </div>
              )}

            </div>

            <div className="input-area">

              <textarea
                value={question}
                onChange={(event) =>
                  setQuestion(event.target.value)
                }
                onKeyDown={handleKeyDown}
                placeholder="Ask something about your documents..."
                rows="2"
              />

              <button
                onClick={sendQuestion}
                disabled={
                  loading ||
                  !question.trim()
                }
              >
                {loading
                  ? "Sending..."
                  : "Send"}
              </button>

            </div>

          </section>

          <aside className="sources-card">

            <h2>Documents</h2>

            {sources.length === 0 ? (
              <p className="no-sources">
                No documents uploaded yet.
              </p>
            ) : (
              <div className="source-list">

                {sources.map(
                  (source, index) => (
                    <div
                      className="source-item"
                      key={index}
                    >
                      {typeof source === "string"
                        ? source
                        : JSON.stringify(source)}
                    </div>
                  )
                )}

              </div>
            )}

          </aside>

        </div>

      </main>

    </div>
  );
}

export default App;