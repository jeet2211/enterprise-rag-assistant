import { useEffect, useState } from 'react'
import type { Citation } from '../types'

interface CitationCardProps {
  citation: Citation
  index: number
  highlighted?: boolean
}

export function CitationCard({ citation, index, highlighted }: CitationCardProps) {
  const [open, setOpen] = useState(false)

  // Auto-expand if the card is highlighted/targeted by the user
  useEffect(() => {
    if (highlighted) {
      setOpen(true)
    }
  }, [highlighted])

  return (
    <div
      className={`overflow-hidden rounded-lg border transition-all duration-300 ${
        highlighted
          ? 'border-cyan-400/60 bg-cyan-400/10'
          : 'border-white/5 bg-white/5'
      } text-left backdrop-blur`}
    >
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between gap-3 px-3 py-2 text-left transition hover:bg-white/5"
      >
        <div className="min-w-0 flex-1">
          <p className="truncate text-xs text-slate-200">
            [{index + 1}] {citation.document_name} · page {citation.page_number}
          </p>
          {citation.section_title ? (
            <p className="mt-0.5 truncate text-[11px] text-slate-500">
              {citation.section_title}
            </p>
          ) : null}
        </div>
        <div className="flex shrink-0 items-center gap-2">
          {citation.distance !== undefined && (
            <span
              className={`rounded-full px-1.5 py-0.5 text-[9px] ${
                citation.distance < 0.2
                  ? 'bg-emerald-400/10 text-emerald-300'
                  : citation.distance < 0.38
                    ? 'bg-amber-400/10 text-amber-300'
                    : 'bg-orange-400/10 text-orange-300'
              }`}
            >
              {(1 - citation.distance).toFixed(2)}
            </span>
          )}
          <span className="text-[10px] text-slate-500">{open ? 'Hide' : 'Show'}</span>
        </div>
      </button>
      {open ? (
        <div className="border-t border-white/5 bg-black/20 px-3 py-2 text-xs leading-5 text-slate-300">
          {citation.chunk_preview}
        </div>
      ) : null}
    </div>
  )
}
