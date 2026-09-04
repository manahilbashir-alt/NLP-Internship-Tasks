import { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import "./App.css";

const API_BASE = "http://127.0.0.1:8001";
const STORAGE_KEY = "stacks_sessions_v1";

function newId() {
  return Math.random().toString(36).slice(2, 9);
}

function loadSessions() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  } catch {
    /* ignore corrupt storage */
  }
  const first = { id: newId(), label: "New conversation", messages: [], ledger: [] };
  return [first];
}

function saveSessions(sessions) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions));
  } catch {
    /* storage full or unavailable — non-fatal */
  }
}

function topSource(sourcesStr) {
  if (!sourcesStr) return null;
  const first = sourcesStr.split("\n")[0] || "";
  const m = first.match(/-\s*(.+?),\s*page\s*(\S+)/i);
  if (!m) return null;
  return { file: m[1].trim(), page: m[2].trim() };
}

const UNCERTAIN_PHRASES = ["i don't know", "i do not know", "not provided in the text", "not fully listed"];
function isUncertain(text) {
  const t = (text || "").toLowerCase();
  return UNCERTAIN_PHRASES.some((p) => t.includes(p));
}

function titleFromQuestion(q) {
  const trimmed = q.trim();
  return trimmed.length > 42 ? trimmed.slice(0, 42) + "…" : trimmed;
}

// Gemini sometimes emits bullets separated by spaces instead of real line
// breaks (e.g. "...provided). * **Feedback:** ..."), which markdown can't
// parse as a list. Force each "* " bullet onto its own line first.
function normalizeMarkdown(text) {
  if (!text) return text;
  return text
    .replace(/\s+\*\s+(?=\*\*)/g, "\n\n* ")   // "  * **Label:**" -> new line
    .replace(/\s+\*\s+(?=[A-Z])/g, "\n\n* ")  // "  * Some text"  -> new line
    .trim();
}

export default function App() {
  const [sessions, setSessions] = useState(loadSessions);
  const [activeId, setActiveId] = useState(() => loadSessions()[0].id);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [recording, setRecording] = useState(false);
  const [transcribing, setTranscribing] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const [docs, setDocs] = useState([]);
  const [totalChunks, setTotalChunks] = useState(0);
  const [apiOk, setApiOk] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadNote, setUploadNote] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const [ledgerOpen, setLedgerOpen] = useState(false);
  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const active = sessions.find((s) => s.id === activeId) || sessions[0];

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    saveSessions(sessions);
  }, [sessions]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [active?.messages]);

  async function checkHealth() {
    try {
      const res = await fetch(API_BASE + "/");
      if (!res.ok) throw new Error();
      setApiOk(true);
      loadDocs();
    } catch {
      setApiOk(false);
    }
  }

  async function loadDocs() {
    try {
      const res = await fetch(API_BASE + "/api/rag/sources");
      const data = await res.json();
      setDocs(data.sources || []);
      setTotalChunks(data.total_chunks || 0);
    } catch {
      /* keep last known list */
    }
  }

  function updateActiveSession(patch) {
    setSessions((prev) => prev.map((s) => (s.id === activeId ? { ...s, ...patch } : s)));
  }

  function startNewSession() {
    const fresh = { id: newId(), label: "New conversation", messages: [], ledger: [] };
    setSessions((prev) => [fresh, ...prev]);
    setActiveId(fresh.id);
    inputRef.current?.focus();
  }

  function switchSession(id) {
    setActiveId(id);
    inputRef.current?.focus();
  }

  function deleteSession(id, e) {
    e.stopPropagation();
    setSessions((prev) => {
      const remaining = prev.filter((s) => s.id !== id);
      if (remaining.length === 0) {
        const fresh = { id: newId(), label: "New conversation", messages: [], ledger: [] };
        setActiveId(fresh.id);
        return [fresh];
      }
      if (id === activeId) setActiveId(remaining[0].id);
      return remaining;
    });
  }

  async function handleUpload(file) {
    if (!file) return;
    if (file.type !== "application/pdf") {
      setUploadNote({ type: "error", text: "Only PDF files are supported." });
      return;
    }
    setUploading(true);
    setUploadNote(null);
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await fetch(API_BASE + "/api/rag/ingest", { method: "POST", body: formData });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "ingest failed");
      setUploadNote({ type: "ok", text: `${data.chunks_added} passages indexed from "${data.filename}".` });
      loadDocs();
    } catch {
      setUploadNote({ type: "error", text: "Couldn't ingest that file — check the backend is running." });
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }

  function onDrop(e) {
    e.preventDefault();
    setDragOver(false);
    handleUpload(e.dataTransfer.files[0]);
  }

  async function startRecording() {
    if (recording || transcribing || sending) return;

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      alert("Your browser does not support microphone recording.");
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true,
      });

      audioChunksRef.current = [];

      const mimeTypes = [
        "audio/webm;codecs=opus",
        "audio/webm",
        "audio/ogg",
      ];

      const supportedMimeType = mimeTypes.find((type) =>
        MediaRecorder.isTypeSupported(type)
      );

      const options = supportedMimeType
        ? { mimeType: supportedMimeType }
        : undefined;

      const mediaRecorder = new MediaRecorder(stream, options);

      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        stream.getTracks().forEach((track) => track.stop());

        const audioBlob = new Blob(
          audioChunksRef.current,
          {
            type: mediaRecorder.mimeType || "audio/webm",
          }
        );

        await transcribeAudio(audioBlob);
      };

      mediaRecorder.start();

      setRecording(true);

    } catch (error) {
      console.error("Microphone error:", error);

      if (error.name === "NotAllowedError") {
        alert("Microphone permission was denied. Please allow microphone access.");
      } else {
        alert("Could not access the microphone.");
      }
    }
  }

  function stopRecording() {
    const recorder = mediaRecorderRef.current;

    if (!recorder || recorder.state === "inactive") {
      return;
    }

    recorder.stop();
    setRecording(false);
  }

  async function transcribeAudio(audioBlob) {
    setTranscribing(true);

    try {
      const extension = audioBlob.type.includes("ogg")
        ? "ogg"
        : "webm";

      const audioFile = new File(
        [audioBlob],
        `recording.${extension}`,
        {
          type: audioBlob.type,
        }
      );

      const formData = new FormData();
      formData.append("file", audioFile);

      const res = await fetch(
        API_BASE + "/api/transcribe",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await res.json();

      if (!res.ok) {
        throw new Error(
          data.detail || "Transcription failed"
        );
      }

      const transcript = (data.text || "").trim();

      if (!transcript) {
        alert("Whisper could not detect any speech.");
        return;
      }

      setInput(transcript);

      setTimeout(() => {
        inputRef.current?.focus();
      }, 0);

    } catch (error) {
      console.error("Transcription error:", error);

      alert(
        error.message ||
        "Could not transcribe the recording."
      );

    } finally {
      setTranscribing(false);
    }
  }

  async function handleAsk(e) {
    e.preventDefault();
    const question = input.trim();
    if (!question || sending) return;

    const isFirstMessage = active.messages.length === 0;
    const userMsg = { role: "user", text: question };
    const thinkingMsg = { role: "assistant", thinking: true };

    updateActiveSession({
      messages: [...active.messages, userMsg, thinkingMsg],
      label: isFirstMessage ? titleFromQuestion(question) : active.label,
    });
    setInput("");
    setSending(true);

    try {
      const res = await fetch(API_BASE + "/api/rag/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: active.id, question }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "chat failed");

      const uncertain = isUncertain(data.answer);
      const source = uncertain ? null : topSource(data.sources);
      const images = uncertain ? [] : (data.images || []);

      const finalMsgs = [...active.messages, userMsg, {
        role: "assistant",
        text: data.answer,
        uncertain,
        rewritten: data.rewritten_question,
        source,
        images,
      }];

      setSessions((prev) =>
        prev.map((s) =>
          s.id === active.id
            ? {
                ...s,
                messages: finalMsgs,
                ledger: source ? [source, ...s.ledger].slice(0, 12) : s.ledger,
                images: images.length ? [...images, ...(s.images || [])].filter((v, i, a) => a.indexOf(v) === i).slice(0, 12) : (s.images || []),
              }
            : s
        )
      );
    } catch {
      const finalMsgs = [...active.messages, userMsg, {
        role: "assistant",
        text: "Couldn't reach the backend just now. Confirm uvicorn is running, then try again.",
        error: true,
      }];
      setSessions((prev) => prev.map((s) => (s.id === active.id ? { ...s, messages: finalMsgs } : s)));
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="app">
      {/* TOP: brand + horizontal document shelf + status/ledger toggle */}
      <header className="topbar">
        <div className="brand"><h1>Stacks<span className="mark">.</span></h1></div>

        <div className="shelf-rail">
          <label
            className={"shelf-upload" + (dragOver ? " dragover" : "") + (uploading ? " busy" : "")}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={onDrop}
            title="Add a PDF document"
          >
            <span className="shelf-upload-icon">{uploading ? "…" : "＋"}</span>
            <input type="file" accept="application/pdf" ref={fileInputRef} disabled={uploading}
              onChange={(e) => handleUpload(e.target.files[0])} />
          </label>

          <div className="shelf-scroll">
            {docs.length === 0 ? (
              <span className="shelf-empty">Nothing shelved yet — add a PDF</span>
            ) : (
              docs.map((f) => (
                <div className="shelf-chip" key={f} title={f}>
                  <span className="shelf-dot" />
                  <span className="shelf-name">{f}</span>
                </div>
              ))
            )}
          </div>

          {docs.length > 0 && <span className="shelf-total">{totalChunks} passages</span>}
        </div>

        <div className="topbar-right">
          <div className="api-status">
            <span className={"dot" + (apiOk === null ? "" : apiOk ? " ok" : " bad")} />
            <span className="api-text">{apiOk === null ? "checking…" : apiOk ? "connected" : "unreachable"}</span>
          </div>
          <button className="ledger-toggle" onClick={() => setLedgerOpen((v) => !v)}>
            Ledger
            {active.ledger.length > 0 && <span className="ledger-count">{active.ledger.length}</span>}
          </button>
        </div>
      </header>

      {uploadNote && <div className={"upload-note-float " + uploadNote.type}>{uploadNote.text}</div>}

      {/* Conversation tabs */}
      <div className="session-tabs">
        <button className="tab-new" onClick={startNewSession} title="New conversation">+</button>
        <div className="tabs-scroll">
          {sessions.map((s) => (
            <div
              key={s.id}
              className={"tab" + (s.id === activeId ? " active" : "")}
              onClick={() => switchSession(s.id)}
            >
              <span className="tab-label">{s.label}</span>
              <button className="tab-close" onClick={(e) => deleteSession(s.id, e)} title="Delete conversation">×</button>
            </div>
          ))}
        </div>
      </div>

      {/* Centered reading column + sliding ledger drawer */}
      <div className="workspace">
        <main className="chat-col">
          <div className="chat-title">
            <h2>Reading room</h2>
            <span className="session-tag">{active.label}</span>
          </div>

          <div className="messages">
            {active.messages.length === 0 ? (
              <div className="empty-state">
                <div className="glyph">§</div>
                <p>Ask a question about anything on the shelf. Each answer names the single passage that best supports it.</p>
              </div>
            ) : (
              active.messages.map((m, i) => (
                <div className={"msg " + m.role} key={i}>
                  <div className="who">{m.role === "user" ? "You" : "Stacks"}</div>
                  <div className={"bubble" + (m.uncertain ? " uncertain" : "") + (m.error ? " error" : "")}>
                    {m.thinking ? (
                      <span className="thinking"><span className="dot-flash" /><span className="dot-flash" /><span className="dot-flash" /></span>
                    ) : m.role === "assistant" ? (
                      <ReactMarkdown>{normalizeMarkdown(m.text)}</ReactMarkdown>
                    ) : (
                      m.text
                    )}
                  </div>
                  {m.rewritten && <div className="rewrite-note">↳ read as: {m.rewritten}</div>}
                  {m.source && (
                    <div className="cite-strip">
                      <span className="cite-tag">{m.source.file.replace(/\.pdf$/i, "")} <em>p.{m.source.page}</em></span>
                    </div>
                  )}
                  {m.images && m.images.length > 0 && (
                    <div className="figure-strip">
                      {m.images.map((imgPath, idx) => (
                        <img
                          key={idx}
                          src={API_BASE + "/" + imgPath}
                          alt="Referenced figure"
                          className="figure-img"
                          onError={(e) => { e.target.style.display = "none"; }}
                        />
                      ))}
                    </div>
                  )}
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>

          <form className="composer" onSubmit={handleAsk}>
            <input
              ref={inputRef}
              type="text"
              placeholder={
                transcribing
                  ? "Transcribing your voice…"
                  : docs.length === 0
                  ? "Add a document before asking…"
                  : "Ask a question about your documents…"
              }
              value={input}
              onChange={(e) => setInput(e.target.value)}
              autoComplete="off"
              disabled={sending}
            />

            <button
              type="button"
              className={"mic-button" + (recording ? " recording" : "")}
              onClick={recording ? stopRecording : startRecording}
              disabled={sending || transcribing}
              title={recording ? "Stop recording" : "Start voice recording"}
            >
              {recording ? "⏹" : "🎤"}
            </button>

            <button
              type="submit"
              disabled={sending || !input.trim()}
            >
              {sending ? "Asking…" : "Ask"}
            </button>
          </form>
        </main>

        {/* Sliding citation ledger drawer */}
        <aside className={"ledger-drawer" + (ledgerOpen ? " open" : "")}>
          <div className="ledger-drawer-head">
            <h3>Citation ledger</h3>
            <button className="drawer-close" onClick={() => setLedgerOpen(false)}>×</button>
          </div>
          <p className="sub">The single passage behind each recent confident answer, most recent first.</p>
          {active.ledger.length === 0 ? (
            <div className="ledger-empty">Ask a question to see which passage was used to answer it.</div>
          ) : (
            active.ledger.map((s, i) => (
              <div className="ledger-item" key={i}>
                <span className="ledger-index">{String(i + 1).padStart(2, "0")}</span>
                <div>
                  <div className="file">{s.file}</div>
                  <div className="page">page {s.page}</div>
                </div>
              </div>
            ))
          )}
        </aside>
        {ledgerOpen && <div className="drawer-scrim" onClick={() => setLedgerOpen(false)} />}
      </div>
    </div>
  );
}
