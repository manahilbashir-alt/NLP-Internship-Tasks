
import { useState, useRef } from 'react'
import SpeechRecorder from './SpeechRecorder'

const MAX_CHARS = 2000

export default function MessageInput({ onSend, disabled }) {
  const [value, setValue] = useState('')
  const textareaRef = useRef(null)

  function handleSubmit() {
    const trimmed = value.trim()
    if (!trimmed || disabled) return

    onSend(trimmed)
    setValue('')

    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  function handleChange(e) {
    setValue(e.target.value.slice(0, MAX_CHARS))

    e.target.style.height = 'auto'
    e.target.style.height = Math.min(e.target.scrollHeight, 160) + 'px'
  }

  function handleTranscription(text) {
    setValue((prev) => {
      const newValue = prev
        ? `${prev} ${text}`
        : text

      return newValue.slice(0, MAX_CHARS)
    })

    setTimeout(() => {
      if (textareaRef.current) {
        textareaRef.current.focus()
        textareaRef.current.style.height = 'auto'
        textareaRef.current.style.height =
          Math.min(textareaRef.current.scrollHeight, 160) + 'px'
      }
    }, 0)
  }

  return (
    <div className="border-t border-codex-border bg-codex-panel/90 backdrop-blur px-4 md:px-8 py-3">
      <div className="flex items-end gap-3 bg-codex-panelAlt border border-codex-border rounded-lg px-3 py-2 focus-within:border-gold-leaf/60 transition-colors">

        <textarea
          ref={textareaRef}
          value={value}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          rows={1}
          placeholder="Ask about anything you're studying…"
          disabled={disabled}
          className="flex-1 bg-transparent resize-none outline-none text-[15px] font-body text-codex-text placeholder:text-codex-muted py-1.5 max-h-40"
        />

        <span className="text-[11px] font-mono text-codex-muted pb-2 select-none">
          {value.length}/{MAX_CHARS}
        </span>

        <SpeechRecorder
          onTranscription={handleTranscription}
        />

        <button
          onClick={handleSubmit}
          disabled={disabled || !value.trim()}
          className="shrink-0 bg-gradient-to-r from-gold-dim to-gold-leaf disabled:from-codex-border disabled:to-codex-border disabled:text-codex-muted text-codex-bg font-semibold text-sm rounded-md px-4 py-2 hover:brightness-110 transition-all"
        >
          Send
        </button>

      </div>

      <p className="text-[11px] text-codex-muted mt-1.5 px-1 font-mono">
        Enter to send · Shift+Enter for new line · 🎤 to speak
      </p>
    </div>
  )
}