import { useState } from 'react'

export default function ChatMessage({ role, content, usage, onRegenerate, isLast }) {
  const [copied, setCopied] = useState(false)
  const isUser = role === 'user'

  function handleCopy() {
    navigator.clipboard.writeText(content)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }

  return (
    <div className={`msg-enter flex ${isUser ? 'justify-end' : 'justify-start'} px-4 md:px-8`}>
      <div className="max-w-[75%] group">
        <div
          className={
            isUser
              ? 'bg-rubric-red/10 border border-rubric-red/35 text-codex-text rounded-lg rounded-br-sm px-4 py-3 shadow-rubric'
              : 'bg-codex-panel border border-gold-leaf/25 text-codex-text rounded-lg rounded-bl-sm px-4 py-3 shadow-illuminate'
          }
        >
          {!isUser && (
            <div className="flex items-center gap-1.5 mb-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-gold-leaf glow-dot" />
              <span className="text-[11px] uppercase tracking-[0.15em] text-gold-leaf/80 font-mono">Companion</span>
            </div>
          )}
          {isUser && (
            <div className="flex items-center justify-end gap-1.5 mb-1.5">
              <span className="text-[11px] uppercase tracking-[0.15em] text-rubric-red/80 font-mono">You</span>
            </div>
          )}
          <p className="whitespace-pre-wrap leading-relaxed text-[15.5px] font-body">{content}</p>
        </div>

        <div className={`flex items-center gap-3 mt-1.5 px-1 opacity-0 group-hover:opacity-100 transition-opacity ${isUser ? 'justify-end' : ''}`}>
          <button
            onClick={handleCopy}
            className="text-[11px] font-mono text-codex-muted hover:text-gold-leaf transition-colors"
          >
            {copied ? 'copied' : 'copy'}
          </button>
          {!isUser && isLast && onRegenerate && (
            <button
              onClick={onRegenerate}
              className="text-[11px] font-mono text-codex-muted hover:text-gold-leaf transition-colors"
            >
              regenerate
            </button>
          )}
          {!isUser && usage && (
            <span className="text-[11px] font-mono text-codex-muted">
              {usage.prompt_tokens + usage.completion_tokens} tok · ${usage.cost?.toFixed(6)} · {usage.latency_ms}ms
            </span>
          )}
        </div>
      </div>
    </div>
  )
}
