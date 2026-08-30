import PersonaSelector from './PersonaSelector'

export default function StatsBar({ persona, onPersonaChange, usage, useTools, onToggleTools, streamMode, onToggleStream }) {
  return (
    <div className="border-b border-codex-border bg-codex-panel/90 backdrop-blur px-4 md:px-8 py-3 flex flex-wrap items-center justify-between gap-3">
      <PersonaSelector value={persona} onChange={onPersonaChange} />

      <div className="flex items-center gap-4">
        <label className="flex items-center gap-1.5 text-xs font-mono text-codex-muted cursor-pointer select-none">
          <input type="checkbox" checked={streamMode} onChange={onToggleStream} className="accent-gold-leaf" />
          stream
        </label>
        <label className="flex items-center gap-1.5 text-xs font-mono text-codex-muted cursor-pointer select-none">
          <input type="checkbox" checked={useTools} onChange={onToggleTools} className="accent-gold-leaf" />
          tools
        </label>
        <div className="text-xs font-mono text-gold-leaf/90 border-l border-codex-border pl-4">
          {usage.prompt_tokens + usage.completion_tokens} tok · ${usage.cost.toFixed(6)}
        </div>
      </div>
    </div>
  )
}
