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
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between gap-3 px-4 py-3 text-left transition hover:bg-white/5"
      >
        <div className="min-w-0 flex-1">
          <p className="text-xs uppercase tracking-[0.3em] text-cyan-200/80">Source {index + 1}</p>
          <p className="mt-1 truncate text-sm font-medium text-white">
            {citation.document_name} · page {citation.page_number}
          </p>
          {citation.section_title ? (
            <p className="mt-0.5 truncate text-[10px] uppercase tracking-[0.22em] text-slate-400">
              {citation.section_title}
            </p>
          ) : null}
          {citation.token_count ? (
            <p className="mt-0.5 text-[10px] text-slate-500">~{citation.token_count} tokens</p>
          ) : null}
        </div>
        <div className="flex shrink-0 flex-col items-end gap-1">
          {citation.distance !== undefined && (
            <span
              className={`rounded-full px-2 py-0.5 text-[10px] font-medium ${
                citation.distance < 0.2
                  ? 'bg-emerald-400/15 text-emerald-300'
                  : citation.distance < 0.38
                    ? 'bg-amber-400/15 text-amber-300'
                    : 'bg-orange-400/15 text-orange-300'
              }`}
            >
              {(1 - citation.distance).toFixed(2)} rel
            </span>
          )}
          <span className="text-xs text-slate-400">{open ? 'Hide' : 'Show'}</span>
        </div>
      </button>
      {open ? (
        <div className="border-t border-white/10 px-4 py-3 text-sm leading-6 text-slate-300">
          {citation.chunk_preview}
        </div>
      ) : null}
    </div>
  )
}
