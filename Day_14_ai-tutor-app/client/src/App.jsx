import { useState, useEffect, useRef, useCallback } from 'react'
import Sidebar from './components/Sidebar'
import ChatMessage from './components/ChatMessage'
import TypingIndicator from './components/TypingIndicator'
import MessageInput from './components/MessageInput'
import StatsBar from './components/StatsBar'
import PromptLab from './components/PromptLab'
import { sendChat, streamChat, generateTitle, regenerateChat, deleteSession as apiDeleteSession } from './api'

const STORAGE_KEY = 'ai-tutor-sessions-v1'

function loadStore() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : {}
  } catch {
    return {}
  }
}

function saveStore(store) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(store))
}

export default function App() {
  const [store, setStore] = useState(loadStore)
  const [activeId, setActiveId] = useState(() => Object.keys(loadStore())[0] || null)
  const [persona, setPersona] = useState('casual')
  const [useTools, setUseTools] = useState(false)
  const [streamMode, setStreamMode] = useState(true)
  const [isTyping, setIsTyping] = useState(false)
  const [streamBuffer, setStreamBuffer] = useState('')
  const [promptLabOpen, setPromptLabOpen] = useState(false)
  const scrollRef = useRef(null)

  useEffect(() => saveStore(store), [store])

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [store, activeId, streamBuffer, isTyping])

  const activeSession = activeId ? store[activeId] : null

  useEffect(() => {
    if (activeSession) setPersona(activeSession.persona)
  }, [activeId]) // eslint-disable-line react-hooks/exhaustive-deps

  function handleNewChat() {
    const id = crypto.randomUUID()
    setStore((prev) => ({
      ...prev,
      [id]: {
        title: 'New chat',
        persona,
        messages: [],
        usage: { prompt_tokens: 0, completion_tokens: 0, cost: 0 },
      },
    }))
    setActiveId(id)
  }

  function handleDeleteSession(id) {
    apiDeleteSession(id).catch(() => {})
    setStore((prev) => {
      const next = { ...prev }
      delete next[id]
      return next
    })
    if (activeId === id) {
      setActiveId(null)
    }
  }

  const updateSession = useCallback((id, updater) => {
    setStore((prev) => ({ ...prev, [id]: updater(prev[id]) }))
  }, [])

  async function handleSend(text) {
    let id = activeId
    const isFirstMessage = !id || (store[id]?.messages?.length ?? 0) === 0

    if (!id) {
      id = crypto.randomUUID()
      setStore((prev) => ({
        ...prev,
        [id]: { title: 'New chat', persona, messages: [], usage: { prompt_tokens: 0, completion_tokens: 0, cost: 0 } },
      }))
      setActiveId(id)
    }

    updateSession(id, (s) => ({
      ...s,
      persona,
      messages: [...s.messages, { role: 'user', content: text }],
    }))

    setIsTyping(true)

    if (streamMode && !useTools) {
      setStreamBuffer('')
      let acc = ''
      await streamChat(
        { sessionId: id, message: text, persona, temperature: 0.7 },
        (delta) => {
          acc += delta
          setStreamBuffer(acc)
        },
        (final) => {
          updateSession(id, (s) => ({
            ...s,
            messages: [...s.messages, {
              role: 'assistant',
              content: acc,
              usage: final.usage ? { ...final.usage, latency_ms: final.latency_ms } : null,
              moderated: !!final.moderated,
            }],
            usage: {
              prompt_tokens: s.usage.prompt_tokens + (final.usage?.prompt_tokens || 0),
              completion_tokens: s.usage.completion_tokens + (final.usage?.completion_tokens || 0),
              cost: s.usage.cost + (final.usage?.cost || 0),
            },
          }))
          setStreamBuffer('')
          setIsTyping(false)
          // Don't waste a title-generation call on a message that never
          // reached the model — nothing meaningful to title yet.
          if (isFirstMessage && !final.moderated) maybeTitle(id)
        },
        (err) => {
          updateSession(id, (s) => ({
            ...s,
            messages: [...s.messages, { role: 'assistant', content: `Error: ${err}` }],
          }))
          setStreamBuffer('')
          setIsTyping(false)
        }
      )
    } else {
      try {
        const res = await sendChat({ sessionId: id, message: text, persona, temperature: 0.7, useTools, jsonMode: false })
        updateSession(id, (s) => ({
          ...s,
          messages: [...s.messages, {
            role: 'assistant',
            content: res.reply,
            usage: { ...res.usage, latency_ms: res.latency_ms },
            moderated: !!res.moderated,
          }],
          usage: {
            prompt_tokens: s.usage.prompt_tokens + res.usage.prompt_tokens,
            completion_tokens: s.usage.completion_tokens + res.usage.completion_tokens,
            cost: s.usage.cost + res.usage.cost,
          },
        }))
        if (isFirstMessage && !res.moderated) maybeTitle(id)
      } catch (e) {
        updateSession(id, (s) => ({
          ...s,
          messages: [...s.messages, { role: 'assistant', content: `Error: ${e.message}` }],
        }))
      } finally {
        setIsTyping(false)
      }
    }
  }

  async function maybeTitle(id) {
    try {
      const { title } = await generateTitle(id)
      updateSession(id, (s) => ({ ...s, title }))
    } catch {
      /* non-critical */
    }
  }

  async function handleRegenerate() {
    if (!activeSession || !activeId) return
    const last = activeSession.messages[activeSession.messages.length - 1]
    if (!last || last.role !== 'assistant') return

    setIsTyping(true)
    try {
      const res = await regenerateChat(activeId)
      // Replace the last assistant message in place — no duplicate user turn,
      // no growth of the message list.
      updateSession(activeId, (s) => ({
        ...s,
        messages: [
          ...s.messages.slice(0, -1),
          { role: 'assistant', content: res.reply, usage: { ...res.usage, latency_ms: res.latency_ms } },
        ],
        usage: {
          prompt_tokens: s.usage.prompt_tokens + res.usage.prompt_tokens,
          completion_tokens: s.usage.completion_tokens + res.usage.completion_tokens,
          cost: s.usage.cost + res.usage.cost,
        },
      }))
    } catch (e) {
      updateSession(activeId, (s) => ({
        ...s,
        messages: [...s.messages, { role: 'assistant', content: `Error: ${e.message}` }],
      }))
    } finally {
      setIsTyping(false)
    }
  }

  const sessionsList = Object.entries(store)
    .map(([id, s]) => ({
      session_id: id,
      title: s.title,
      persona: s.persona,
      message_count: s.messages.length,
      usage: s.usage,
    }))
    .reverse()

  return (
    <div className="flex h-screen bg-codex-bg bg-vignette text-codex-text font-body">
      <Sidebar
        sessions={sessionsList}
        activeId={activeId}
        onSelect={setActiveId}
        onNewChat={handleNewChat}
        onDelete={handleDeleteSession}
        onOpenPromptLab={() => setPromptLabOpen(true)}
      />

      {promptLabOpen && <PromptLab onClose={() => setPromptLabOpen(false)} />}

      <main className="flex-1 flex flex-col min-w-0">
        <StatsBar
          persona={persona}
          onPersonaChange={setPersona}
          usage={activeSession?.usage || { prompt_tokens: 0, completion_tokens: 0, cost: 0 }}
          useTools={useTools}
          onToggleTools={() => setUseTools((v) => !v)}
          streamMode={streamMode}
          onToggleStream={() => setStreamMode((v) => !v)}
        />

        <div ref={scrollRef} className="flex-1 overflow-y-auto py-6 space-y-4">
          {!activeSession || activeSession.messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center px-8">
              <span className="w-3 h-3 rounded-full bg-gold-leaf glow-dot mb-4" />
              <h2 className="font-display text-3xl text-codex-text mb-2">What are you studying tonight?</h2>
              <p className="text-codex-muted text-sm max-w-sm font-body">
                Pick a persona above, ask a question, and I'll help you work through it — with
                live token and cost tracking as we go.
              </p>
            </div>
          ) : (
            activeSession.messages.map((m, i) => (
              <ChatMessage
                key={i}
                role={m.role}
                content={m.content}
                usage={m.usage}
                moderated={m.moderated}
                isLast={i === activeSession.messages.length - 1}
                onRegenerate={m.role === 'assistant' && !m.moderated ? handleRegenerate : null}
              />
            ))
          )}
          {streamBuffer && <ChatMessage role="assistant" content={streamBuffer} />}
          {isTyping && !streamBuffer && <TypingIndicator />}
        </div>

        <MessageInput onSend={handleSend} disabled={isTyping} />
      </main>
    </div>
  )
}
