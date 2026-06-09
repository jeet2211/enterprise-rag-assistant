import { useState } from 'react'
import type { Citation } from '../types'

interface CitationCardProps {
  citation: Citation
  index: number
}

export function CitationCard({ citation, index }: CitationCardProps) {
  const [open, setOpen] = useState(false)

  return (
    <div className="overflow-hidden rounded-2xl border border-white/10 bg-white/5 text-left backdrop-blur">
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        className="flex w-full items-center justify-between gap-3 px-4 py-3 text-left transition hover:bg-white/5"
      >
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-cyan-200/80">Source {index + 1}</p>
          <p className="mt-1 text-sm font-medium text-white">
            {citation.document_name} · page {citation.page_number}
          </p>
        </div>
        <span className="text-xs text-slate-300">{open ? 'Hide' : 'Show'}</span>
      </button>
      {open ? (
        <div className="border-t border-white/10 px-4 py-3 text-sm leading-6 text-slate-300">
          {citation.chunk_preview}
        </div>
      ) : null}
    </div>
  )
}

