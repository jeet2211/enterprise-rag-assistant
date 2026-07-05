interface FollowUpChipsProps {
  questions: string[]
  onSelect: (question: string) => void
  disabled?: boolean
}

export function FollowUpChips({ questions, onSelect, disabled = false }: FollowUpChipsProps) {
  if (!questions || questions.length === 0) return null

  return (
    <div className="mt-4 space-y-2">
      <p className="text-[10px] font-semibold uppercase tracking-[0.3em] text-slate-500">
        You may also ask
      </p>
      <div className="flex flex-wrap gap-2">
        {questions.map((question, index) => (
          <button
            key={index}
            type="button"
            onClick={() => onSelect(question)}
            disabled={disabled}
            className="rounded-2xl border border-cyan-300/20 bg-cyan-300/5 px-3 py-1.5 text-left text-xs text-cyan-200/80 transition
              hover:border-cyan-300/40 hover:bg-cyan-300/10 hover:text-cyan-100
              disabled:cursor-not-allowed disabled:opacity-40
              focus:outline-none focus:ring-1 focus:ring-cyan-300/40"
          >
            {question}
          </button>
        ))}
      </div>
    </div>
  )
}
