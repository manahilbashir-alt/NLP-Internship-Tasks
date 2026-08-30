export default function Sidebar({ sessions, activeId, onSelect, onNewChat, onDelete, onOpenPromptLab }) {
  return (
    <aside className="w-64 shrink-0 bg-codex-panel border-r border-codex-border flex flex-col h-full">
      <div className="px-4 py-4 border-b border-codex-border">
        <div className="flex items-center gap-2 mb-3">
          <span className="w-2 h-2 rounded-full bg-gold-leaf glow-dot" />
          <h1 className="font-display text-xl tracking-tight text-codex-text">Learning Companion</h1>
        </div>
        <button
          onClick={onNewChat}
          className="w-full text-sm font-medium font-body tracking-wide bg-gradient-to-r from-gold-dim to-gold-leaf text-codex-bg rounded-md py-2 hover:brightness-110 transition-all shadow-illuminate"
        >
          + New chat
        </button>
      </div>

      <nav className="flex-1 overflow-y-auto py-2">
        {sessions.length === 0 && (
          <p className="text-codex-muted text-sm px-4 py-6 text-center font-mono italic">No sessions yet</p>
        )}
        {sessions.map((s) => (
          <div
            key={s.session_id}
            onClick={() => onSelect(s.session_id)}
            className={`group mx-2 mb-1 rounded-md px-3 py-2.5 cursor-pointer transition-colors border-l-2 ${
              s.session_id === activeId
                ? 'bg-codex-panelAlt border-gold-leaf'
                : 'hover:bg-codex-panelAlt border-transparent'
            }`}
          >
            <div className="flex items-center justify-between gap-2">
              <p className="text-sm truncate font-body text-codex-text">{s.title}</p>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  onDelete(s.session_id)
                }}
                className="opacity-0 group-hover:opacity-100 text-codex-muted hover:text-rubric-red text-xs transition-opacity"
                aria-label="Delete session"
              >
                ✕
              </button>
            </div>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-[10px] uppercase tracking-wider text-gold-leaf/80 font-mono">{s.persona}</span>
              <span className="text-[10px] text-codex-muted font-mono">· {s.message_count} msgs</span>
            </div>
          </div>
        ))}
      </nav>

      <div className="px-4 py-3 border-t border-codex-border space-y-2">
        <button
          onClick={onOpenPromptLab}
          className="w-full text-xs font-mono text-codex-muted hover:text-gold-leaf border border-codex-border hover:border-gold-leaf/50 rounded-md py-2 transition-colors"
        >
          ⚗ Prompt Lab
        </button>
        <p className="text-[11px] text-codex-muted font-mono">
          gemini-3.1-flash-lite · {sessions.length} session{sessions.length !== 1 ? 's' : ''}
        </p>
      </div>
    </aside>
  )
}
