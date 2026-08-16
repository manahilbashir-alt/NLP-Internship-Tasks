export default function TypingIndicator() {
  return (
    <div className="flex justify-start px-4 md:px-8">
      <div className="bg-codex-panel border border-gold-leaf/25 rounded-lg rounded-bl-sm px-4 py-3 flex items-center gap-1.5">
        <span className="w-1.5 h-1.5 rounded-full bg-gold-leaf animate-bounce [animation-delay:-0.3s]" />
        <span className="w-1.5 h-1.5 rounded-full bg-gold-leaf animate-bounce [animation-delay:-0.15s]" />
        <span className="w-1.5 h-1.5 rounded-full bg-gold-leaf animate-bounce" />
      </div>
    </div>
  )
}
