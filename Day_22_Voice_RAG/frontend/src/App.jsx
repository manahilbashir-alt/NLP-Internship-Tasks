import { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import "./App.css";

const API_BASE = "http://127.0.0.1:8000";
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
  const [mode, setMode] = useState("text"); // "text" | "voice"
  const [recordingSeconds, setRecordingSeconds] = useState(0);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timerRef = useRef(null);
  const [docs, setDocs] = useState([]);
  const [totalChunks, setTotalChunks] = useState(0);
  const [apiOk, setApiOk] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadNote, setUploadNote] = useState(null);
  const [dragOver, setDragOver] = useState(false);
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
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
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
    setRecordingSeconds(0);
    timerRef.current = setInterval(() => {
      setRecordingSeconds((s) => s + 1);
    }, 1000);

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
  if (timerRef.current) {
    clearInterval(timerRef.current);
    timerRef.current = null;
  }
}

function formatDuration(totalSeconds) {
  const m = Math.floor(totalSeconds / 60);
  const s = totalSeconds % 60;
  return `${m}:${String(s).padStart(2, "0")}`;
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
      alert("Whisper could not detect any speech. Try again.");
      return;
    }

    setInput(transcript);
    setMode("text");

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
      {/* LEFT: sessions + source library */}
      <aside className="sidebar">
        <div className="brand"><h1>Stacks<span className="mark">.</span></h1></div>
        <p className="tagline">Upload a document, then ask it anything. Every answer names its shelf and page.</p>

        <label
          className={"upload-box" + (dragOver ? " dragover" : "") + (uploading ? " busy" : "")}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={onDrop}
        >
          <span className="upload-icon">{uploading ? "…" : "＋"}</span>
          <span className="upload-label">{uploading ? "Reading document…" : "Add a document"}</span>
          <span className="upload-sub">PDF · drag here or click to browse</span>
          <input type="file" accept="application/pdf" ref={fileInputRef} disabled={uploading}
            onChange={(e) => handleUpload(e.target.files[0])} />
        </label>
        {uploadNote && <div className={"upload-note " + uploadNote.type}>{uploadNote.text}</div>}

        <div className="section-label"><span>Shelved</span><span>{docs.length}</span></div>
        <div className="doc-list compact">
          {docs.length === 0 ? (
            <div className="doc-empty">Nothing ingested yet.</div>
          ) : (
            <>
              {docs.map((f) => (
                <div className="doc-card" key={f}>
                  <span className="doc-dot" />
                  <div className="name">{f}</div>
                </div>
              ))}
              <div className="chunk-total">{totalChunks} passages total</div>
            </>
          )}
        </div>

        <div className="section-label" style={{ marginTop: 22 }}>
          <span>Conversations</span>
          <button className="new-chat-btn" onClick={startNewSession}>+ New</button>
        </div>
        <div className="session-list">
          {sessions.map((s) => (
            <div
              key={s.id}
              className={"session-item" + (s.id === activeId ? " active" : "")}
              onClick={() => switchSession(s.id)}
            >
              <span className="session-label">{s.label}</span>
              <button className="session-delete" onClick={(e) => deleteSession(s.id, e)} title="Delete conversation">×</button>
            </div>
          ))}
        </div>

        <div className="api-status">
          <span className={"dot" + (apiOk === null ? "" : apiOk ? " ok" : " bad")} />
          <span>{apiOk === null ? "checking backend…" : apiOk ? "backend connected" : "backend unreachable"}</span>
        </div>
      </aside>

      {/* CENTER: chat */}
      <main className="chat-col">
        <div className="chat-header">
          <div>
            <h2>Reading room</h2>
            <span className="session-tag">{active.label}</span>
          </div>
          <span className="header-stat">{docs.length} doc{docs.length === 1 ? "" : "s"} · {totalChunks} passages</span>
        </div>

        <div className="messages">
          {active.messages.length === 0 ? (
            <div className="empty-state">
              <div className="glyph">§</div>
              <h3>Nothing asked yet</h3>
              <p>Ask a question about anything on the shelf. Each answer names the single passage that best supports it.</p>
              <div className="empty-tips">
                <span>📄 Upload a PDF</span>
                <span>💬 Ask in text or voice</span>
                <span>§ Get a cited answer</span>
              </div>
            </div>
          ) : (
            active.messages.map((m, i) => (
              <div className={"msg " + m.role} key={i}>
                <div className="row">
                  <span className={"avatar" + (m.role === "user" ? " avatar-user" : " avatar-bot")}>
                    {m.role === "user" ? "Y" : "§"}
                  </span>
                  <div className="bubble-col">
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
                  </div>
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

        <div className="composer-wrap">
          <div className="mode-toggle" role="tablist" aria-label="Input mode">
            <button
              type="button"
              role="tab"
              aria-selected={mode === "text"}
              className={"mode-btn" + (mode === "text" ? " active" : "")}
              onClick={() => { if (recording) stopRecording(); setMode("text"); }}
            >
              <span className="mode-icon">✎</span> Text
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={mode === "voice"}
              className={"mode-btn" + (mode === "voice" ? " active" : "")}
              onClick={() => setMode("voice")}
              disabled={sending}
            >
              <span className="mode-icon">🎤</span> Voice
            </button>
          </div>

          {mode === "text" ? (
            <form className="composer" onSubmit={handleAsk}>
              <input
                ref={inputRef}
                type="text"
                placeholder={
                  docs.length === 0
                    ? "Add a document before asking…"
                    : "Ask a question about your documents…"
                }
                value={input}
                onChange={(e) => setInput(e.target.value)}
                autoComplete="off"
                disabled={sending}
              />
              <button type="submit" disabled={sending || !input.trim()}>
                {sending ? "Asking…" : "Ask"}
              </button>
            </form>
          ) : (
            <div className="voice-panel">
              {recording ? (
                <>
                  <div className="voice-wave" aria-hidden="true">
                    {Array.from({ length: 9 }).map((_, i) => (
                      <span key={i} className="wave-bar" style={{ animationDelay: `${i * 0.08}s` }} />
                    ))}
                  </div>
                  <button
                    type="button"
                    className="mic-button large recording"
                    onClick={stopRecording}
                    title="Stop recording"
                  >
                    ⏹
                  </button>
                  <div className="voice-status">
                    <span className="rec-dot" /> Listening… <span className="rec-timer">{formatDuration(recordingSeconds)}</span>
                  </div>
                  <p className="voice-hint">Tap the square to stop and transcribe.</p>
                </>
              ) : transcribing ? (
                <>
                  <div className="mic-button large busy"><span className="spinner" /></div>
                  <div className="voice-status">Transcribing your voice…</div>
                  <p className="voice-hint">Whisper is turning your recording into text.</p>
                </>
              ) : (
                <>
                  <button
                    type="button"
                    className="mic-button large"
                    onClick={startRecording}
                    disabled={sending || docs.length === 0}
                    title="Start voice recording"
                  >
                    🎤
                  </button>
                  <div className="voice-status">Tap to speak your question</div>
                  <p className="voice-hint">
                    {docs.length === 0
                      ? "Add a document before asking…"
                      : "Your recording is transcribed on the server and dropped into the text box for review."}
                  </p>
                </>
              )}
            </div>
          )}
        </div>
      </main>

      {/* RIGHT: single-source citation ledger */}
      <aside className="citations">
        <h3>Citation ledger</h3>
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
    </div>
  );
}