const PERSONAS = [
  { id: 'formal', label: 'Formal', hint: 'Prof. Aldridge' },
  { id: 'casual', label: 'Casual', hint: 'Sam' },
  { id: 'technical', label: 'Technical', hint: 'Dr. Byte' },
]

export default function PersonaSelector({ value, onChange }) {
  return (
    <div className="flex items-center gap-1 bg-codex-panelAlt border border-codex-border rounded-lg p-1">
      {PERSONAS.map((p) => (
        <button
          key={p.id}
          onClick={() => onChange(p.id)}
          title={p.hint}
          className={`px-3 py-1.5 rounded-md text-xs font-mono transition-colors ${
            value === p.id
              ? 'bg-gradient-to-r from-gold-dim to-gold-leaf text-codex-bg font-medium'
              : 'text-codex-muted hover:text-codex-text'
          }`}
        >
          {p.label}
        </button>
      ))}
    </div>
  )
}
