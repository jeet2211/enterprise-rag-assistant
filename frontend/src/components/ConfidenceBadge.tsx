import type { Confidence } from '../types'

interface ConfidenceBadgeProps {
  confidence: Confidence
}

const CONFIG: Record<Confidence, { label: string; className: string }> = {
  high: {
    label: 'High confidence',
    className: 'bg-emerald-400/15 text-emerald-300 border-emerald-400/25',
  },
  medium: {
    label: 'Medium confidence',
    className: 'bg-amber-400/15 text-amber-300 border-amber-400/25',
  },
  low: {
    label: 'Low confidence',
    className: 'bg-orange-400/15 text-orange-300 border-orange-400/25',
  },
  not_found: {
    label: 'Not found in docs',
    className: 'bg-rose-400/15 text-rose-300 border-rose-400/25',
  },
}

const ICONS: Record<Confidence, string> = {
  high: '●',
  medium: '◐',
  low: '○',
  not_found: '✕',
}

export function ConfidenceBadge({ confidence }: ConfidenceBadgeProps) {
  const { label, className } = CONFIG[confidence] ?? CONFIG.medium

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-[11px] font-medium uppercase tracking-[0.2em] ${className}`}
      title={`Answer confidence: ${label}`}
    >
      <span className="text-[9px]">{ICONS[confidence]}</span>
      {label}
    </span>
  )
}
