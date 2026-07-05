import { useEffect, useState } from 'react'
import { fetchHealth } from '../api/client'
import type { HealthStats } from '../types'

interface StatCardProps {
  label: string
  value: number | string
  sub?: string
  colorClass?: string
  icon: string
}

function StatCard({ label, value, sub, colorClass = 'text-white', icon }: StatCardProps) {
  return (
    <div className="flex flex-col gap-2 rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur">
      <div className="flex items-center justify-between">
        <span className="text-lg">{icon}</span>
        {sub && (
          <span className="rounded-full bg-white/5 px-2 py-0.5 text-[10px] uppercase tracking-[0.2em] text-slate-400">
            {sub}
          </span>
        )}
      </div>
      <p className={`text-3xl font-bold ${colorClass}`}>{value}</p>
      <p className="text-xs uppercase tracking-[0.2em] text-slate-400">{label}</p>
    </div>
  )
}

interface DashboardProps {
  onClose: () => void
}

export function Dashboard({ onClose }: DashboardProps) {
  const [stats, setStats] = useState<HealthStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    async function load() {
      try {
        const data = await fetchHealth()
        if (!cancelled) setStats(data)
      } catch {
        // silently fail
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    void load()
    const interval = window.setInterval(() => void load(), 15_000)
    return () => {
      cancelled = true
      window.clearInterval(interval)
    }
  }, [])

  return (
    <div className="w-full rounded-[2rem] border border-white/10 bg-white/5 p-5 backdrop-blur-xl shadow-glow">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.3em] text-cyan-200/80">System Dashboard</p>
          <h2 className="mt-1 text-xl font-semibold text-white">Live Status Overview</h2>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-slate-300 transition hover:bg-white/10"
        >
          Hide
        </button>
      </div>

      {loading ? (
        <div className="grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-5">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="animate-pulse rounded-2xl border border-white/10 bg-white/5 p-4">
              <div className="h-8 w-12 rounded bg-white/10" />
              <div className="mt-2 h-3 w-20 rounded bg-white/10" />
            </div>
          ))}
        </div>
      ) : stats ? (
        <div className="grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-5">
          <StatCard
            icon="📄"
            label="Total Documents"
            value={stats.total_documents}
            colorClass="text-white"
          />
          <StatCard
            icon="✅"
            label="Ready"
            value={stats.ready_documents}
            colorClass="text-emerald-300"
            sub="indexed"
          />
          <StatCard
            icon="⚙️"
            label="Processing"
            value={stats.processing_documents}
            colorClass="text-amber-300"
            sub={stats.processing_documents > 0 ? 'active' : 'idle'}
          />
          <StatCard
            icon="✗"
            label="Failed"
            value={stats.failed_documents}
            colorClass={stats.failed_documents > 0 ? 'text-rose-300' : 'text-slate-400'}
          />
          <StatCard
            icon="🧩"
            label="Total Chunks"
            value={stats.total_chunks.toLocaleString()}
            colorClass="text-cyan-300"
            sub="indexed"
          />
        </div>
      ) : (
        <p className="text-sm text-slate-400">Could not load stats. Is the backend running?</p>
      )}

      {stats && (
        <div className="mt-3 flex flex-wrap gap-3">
          <span
            className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs ${
              stats.chromadb === 'healthy'
                ? 'border-emerald-400/25 bg-emerald-400/10 text-emerald-300'
                : 'border-rose-400/25 bg-rose-400/10 text-rose-300'
            }`}
          >
            <span className="h-1.5 w-1.5 rounded-full bg-current" />
            ChromaDB {stats.chromadb}
          </span>
          <span
            className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs ${
              stats.gemini === 'healthy'
                ? 'border-emerald-400/25 bg-emerald-400/10 text-emerald-300'
                : 'border-amber-400/25 bg-amber-400/10 text-amber-300'
            }`}
          >
            <span className="h-1.5 w-1.5 rounded-full bg-current" />
            Gemini {stats.gemini}
          </span>
          <span className="inline-flex items-center gap-1.5 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-400">
            Uptime {Math.floor(stats.uptime_seconds / 60)}m
          </span>
        </div>
      )}
    </div>
  )
}
