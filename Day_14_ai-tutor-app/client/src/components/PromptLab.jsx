import { useState } from 'react'
import { runProductionPrompt } from '../api'

const MODES = [
  { id: 'structured_json', label: 'Structured JSON', placeholder: 'e.g. "Make me a study plan for learning linear algebra"' },
  { id: 'text_parsing', label: 'Text Parsing', placeholder: 'Paste messy notes or a passage to extract key facts from…' },
  { id: 'code_generation', label: 'Code Generation', placeholder: 'e.g. "Write a Python function that checks if a number is prime"' },
  { id: 'summarization', label: 'Summarization', placeholder: 'Paste a passage or document to summarize…' },
]

export default function PromptLab({ onClose }) {
  const [mode, setMode] = useState('structured_json')
  const [input, setInput] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  async function handleRun() {
    if (!input.trim()) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await runProductionPrompt(mode, input.trim())
      setResult(res)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const activeMode = MODES.find((m) => m.id === mode)

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 px-4">
      <div className="bg-codex-panel border border-gold-leaf/25 rounded-lg w-full max-w-2xl max-h-[85vh] flex flex-col shadow-illuminate">
        <div className="flex items-center justify-between px-5 py-4 border-b border-codex-border">
          <h2 className="font-display text-xl text-codex-text">Prompt Lab</h2>
          <button onClick={onClose} className="text-codex-muted hover:text-gold-leaf text-sm font-mono">✕ close</button>
        </div>

        <div className="px-5 py-3 flex flex-wrap gap-1.5 border-b border-codex-border">
          {MODES.map((m) => (
            <button
              key={m.id}
              onClick={() => { setMode(m.id); setResult(null); setError(null) }}
              className={`px-3 py-1.5 rounded-md text-xs font-mono transition-colors ${
                mode === m.id ? 'bg-gradient-to-r from-gold-dim to-gold-leaf text-codex-bg font-medium' : 'bg-codex-panelAlt text-codex-muted hover:text-codex-text'
              }`}
            >
              {m.label}
            </button>
          ))}
        </div>

        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-3">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={activeMode.placeholder}
            rows={4}
            className="w-full bg-codex-panelAlt border border-codex-border rounded-md px-3 py-2 text-sm font-body text-codex-text outline-none focus:border-gold-leaf/60 resize-none"
          />
          <button
            onClick={handleRun}
            disabled={loading || !input.trim()}
            className="bg-gradient-to-r from-gold-dim to-gold-leaf disabled:from-codex-border disabled:to-codex-border disabled:text-codex-muted text-codex-bg font-semibold text-sm rounded-md px-4 py-2 hover:brightness-110 transition-all"
          >
            {loading ? 'Running…' : 'Run prompt'}
          </button>

          {error && (
            <div className="bg-rubric-red/10 border border-rubric-red/35 rounded-md px-3 py-2 text-sm text-rubric-red">
              {error}
            </div>
          )}

          {result && mode === 'structured_json' && (
            <div className="bg-codex-panelAlt border border-codex-border rounded-md p-3 space-y-2">
              <div className="flex items-center gap-2 text-xs font-mono text-codex-muted">
                <span className={result.valid ? 'text-gold-leaf' : 'text-rubric-red'}>
                  {result.valid ? '✓ schema valid' : '✗ schema invalid'}
                </span>
                <span>· {result.attempts} attempt{result.attempts !== 1 ? 's' : ''}</span>
                <span>· {result.usage.prompt_tokens + result.usage.completion_tokens} tok</span>
                <span>· ${result.usage.cost.toFixed(6)}</span>
              </div>
              <pre className="text-xs font-mono whitespace-pre-wrap text-codex-text">{JSON.stringify(result.data, null, 2)}</pre>
            </div>
          )}

          {result && mode !== 'structured_json' && (
            <div className="bg-codex-panelAlt border border-codex-border rounded-md p-3 space-y-2">
              <p className="text-sm font-body whitespace-pre-wrap leading-relaxed text-codex-text">{result.output}</p>
              <div className="text-xs font-mono text-codex-muted border-t border-codex-border pt-2">
                {result.usage.prompt_tokens + result.usage.completion_tokens} tok · ${result.usage.cost.toFixed(6)} · {result.latency_ms}ms
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
