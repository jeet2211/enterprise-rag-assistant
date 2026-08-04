import { useEffect, useState } from 'react'
import { fetchEvalSummary, fetchHealth, fetchWorkerHealth } from '../api/client'
import type { EvalSummary, HealthStats, WorkerHealthStats } from '../types'

const LANGFUSE_URL = import.meta.env.VITE_LANGFUSE_URL ?? 'https://us.cloud.langfuse.com'
const GRAFANA_URL = import.meta.env.VITE_GRAFANA_URL ?? '/grafana/'
const GRAFANA_DASHBOARD_URL = `${GRAFANA_URL.replace(/\/?$/, '/')}d/rag-metrics-v1/rag-assistant-metrics?orgId=1&refresh=30s`

interface MetricCardProps {
  label: string
  value: number | string
  sub?: string
  tone?: 'cyan' | 'emerald' | 'amber' | 'rose' | 'slate'
}

function MetricCard({ label, value, sub, tone = 'slate' }: MetricCardProps) {
  const toneClass: Record<NonNullable<MetricCardProps['tone']>, string> = {
    cyan: 'text-cyan-300 border-cyan-300/20 bg-cyan-300/10',
    emerald: 'text-emerald-300 border-emerald-300/20 bg-emerald-300/10',
    amber: 'text-amber-300 border-amber-300/20 bg-amber-300/10',
    rose: 'text-rose-300 border-rose-300/20 bg-rose-300/10',
    slate: 'text-slate-200 border-white/10 bg-white/5',
  }

  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur">
      <p className="text-xs uppercase tracking-[0.28em] text-slate-400">{label}</p>
      <div className="mt-3 flex items-end justify-between gap-3">
        <p className={`rounded-2xl border px-3 py-2 text-3xl font-semibold ${toneClass[tone]}`}>{value}</p>
        {sub ? <span className="text-xs uppercase tracking-[0.22em] text-slate-400">{sub}</span> : null}
      </div>
    </div>
  )
}

interface MonitoringPageProps {
  onBack: () => void
}

function statusTone(status: string): 'emerald' | 'amber' | 'rose' {
  return status === 'healthy' ? 'emerald' : status === 'degraded' ? 'amber' : 'rose'
}

function StatusPill({ label, status }: { label: string; status: string }) {
  const tone = statusTone(status)
  const classes =
    tone === 'emerald'
      ? 'border-emerald-400/25 bg-emerald-400/10 text-emerald-300'
      : tone === 'amber'
        ? 'border-amber-400/25 bg-amber-400/10 text-amber-300'
        : 'border-rose-400/25 bg-rose-400/10 text-rose-300'

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs ${classes}`}>
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      {label} {status}
    </span>
  )
}

function formatScore(score: number | null | undefined): string {
  if (score === null || score === undefined) return 'No data'
  return `${Math.round(score * 100)}%`
}

export function MonitoringPage({ onBack }: MonitoringPageProps) {
  const [health, setHealth] = useState<HealthStats | null>(null)
  const [worker, setWorker] = useState<WorkerHealthStats | null>(null)
  const [evalSummary, setEvalSummary] = useState<EvalSummary | null>(null)
  const [evalError, setEvalError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false

    async function load() {
      try {
        const [appHealth, workerHealth, qualitySummary] = await Promise.all([
          fetchHealth(),
          fetchWorkerHealth(),
          fetchEvalSummary().catch((error) => {
            setEvalError(error instanceof Error ? error.message : 'Could not load eval summary')
            return null
          }),
        ])
        if (!cancelled) {
          setHealth(appHealth)
          setWorker(workerHealth)
          setEvalSummary(qualitySummary)
          if (qualitySummary) setEvalError(null)
        }
      } catch {
        if (!cancelled) {
          setHealth(null)
          setWorker(null)
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    void load()
    const interval = window.setInterval(() => void load(), 10_000)
    return () => {
      cancelled = true
      window.clearInterval(interval)
    }
  }, [])

  const uptimeMinutes = health ? Math.floor(health.uptime_seconds / 60) : 0

  return (
    <section className="min-h-screen px-4 py-4 md:px-6 md:py-5">
      <div className="mx-auto flex max-w-7xl flex-col gap-4">
        <div className="rounded-[2rem] border border-white/10 bg-white/5 p-5 shadow-glow backdrop-blur-xl md:p-6">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.3em] text-cyan-200/80">Monitoring</p>
              <h1 className="mt-1.5 text-2xl font-semibold text-white md:text-3xl">Live production control room</h1>
              <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">
                This page refreshes live health checks every 10 seconds and gives you quick links to the key runtime
                surfaces for the app.
              </p>
            </div>

            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                onClick={onBack}
                className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs text-slate-100 transition hover:bg-white/10"
              >
                Back to chat
              </button>
              <a
                href="/api/v1/health"
                target="_blank"
                rel="noreferrer"
                className="rounded-full border border-cyan-300/25 bg-cyan-300/10 px-4 py-2 text-xs text-cyan-200 transition hover:bg-cyan-300/15"
              >
                App health JSON
              </a>
              <a
                href={LANGFUSE_URL}
                target="_blank"
                rel="noreferrer"
                className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs text-slate-100 transition hover:bg-white/10"
              >
                Open Langfuse
              </a>
              <a
                href={GRAFANA_DASHBOARD_URL}
                target="_blank"
                rel="noreferrer"
                className="rounded-full border border-amber-300/25 bg-amber-300/10 px-4 py-2 text-xs text-amber-100 transition hover:bg-amber-300/15"
              >
                Open Grafana
              </a>
            </div>
          </div>

        </div>

        {loading ? (
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            {Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="animate-pulse rounded-2xl border border-white/10 bg-white/5 p-5">
                <div className="h-3 w-24 rounded bg-white/10" />
                <div className="mt-4 h-10 w-20 rounded bg-white/10" />
                <div className="mt-3 h-3 w-16 rounded bg-white/10" />
              </div>
            ))}
          </div>
        ) : (
          <>
            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
              <MetricCard
                label="Backend status"
                value={health?.status ?? 'unknown'}
                tone={health?.status === 'healthy' ? 'emerald' : 'rose'}
                sub="API"
              />
              <MetricCard
                label="Worker status"
                value={worker?.status ?? 'unknown'}
                tone={worker?.status === 'healthy' ? 'emerald' : 'amber'}
                sub={`${worker?.worker_count ?? 0} workers`}
              />
              <MetricCard
                label="Total docs"
                value={health?.total_documents ?? 0}
                tone="cyan"
                sub={`${health?.ready_documents ?? 0} ready`}
              />
              <MetricCard
                label="Total chunks"
                value={(health?.total_chunks ?? 0).toLocaleString()}
                tone="cyan"
                sub={`uptime ${uptimeMinutes}m`}
              />
            </div>

            <div className="grid gap-4 lg:grid-cols-2">
              <div className="rounded-[2rem] border border-white/10 bg-white/5 p-5 shadow-glow backdrop-blur-xl">
                <div className="mb-4 flex items-center justify-between gap-4">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.3em] text-cyan-200/80">System health</p>
                    <h2 className="mt-1 text-xl font-semibold text-white">Live status checks</h2>
                  </div>
                </div>

                <div className="flex flex-wrap gap-2">
                  {health ? (
                    <>
                      <StatusPill label="App" status={health.status} />
                      <StatusPill label="ChromaDB" status={health.chromadb} />
                      <StatusPill label="Gemini" status={health.gemini} />
                    </>
                  ) : (
                    <span className="text-sm text-slate-400">Could not load app health.</span>
                  )}
                  {worker ? (
                    <>
                      <StatusPill label="Redis" status={worker.redis} />
                      <StatusPill label="Celery" status={worker.celery} />
                    </>
                  ) : null}
                </div>

                <div className="mt-5 grid gap-3 sm:grid-cols-2">
                  <a
                    href="/api/v1/health/worker"
                    target="_blank"
                    rel="noreferrer"
                    className="rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm text-slate-200 transition hover:border-cyan-300/25 hover:bg-slate-900"
                  >
                    Open worker health JSON
                  </a>
                  <button
                    type="button"
                    onClick={() => void fetchEvalSummary().then(setEvalSummary).catch((error) => {
                      setEvalError(error instanceof Error ? error.message : 'Could not refresh eval summary')
                    })}
                    className="rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm text-slate-200 transition hover:border-cyan-300/25 hover:bg-slate-900"
                  >
                    Refresh answer quality
                  </button>
                </div>
              </div>

              <div className="rounded-[2rem] border border-white/10 bg-white/5 p-5 shadow-glow backdrop-blur-xl">
                <div className="mb-4">
                  <p className="text-xs font-semibold uppercase tracking-[0.3em] text-cyan-200/80">What to watch</p>
                  <h2 className="mt-1 text-xl font-semibold text-white">Operational signals</h2>
                </div>

                <ul className="space-y-3 text-sm leading-6 text-slate-300">
                  <li>
                    • <span className="text-white">Documents ready/processing/failed</span> shows ingestion health.
                  </li>
                  <li>
                    • <span className="text-white">ChromaDB healthy</span> means retrieval is working.
                  </li>
                  <li>
                    • <span className="text-white">Gemini healthy</span> means the model key is accepted.
                  </li>
                  <li>
                    • <span className="text-white">Worker status</span> tells you whether background processing is alive.
                  </li>
                  <li>
                    • <span className="text-white">Langfuse</span> captures traces and feedback for answer quality.
                  </li>
                </ul>

                <div className="mt-5 flex flex-wrap gap-2">
                  <a
                    href={LANGFUSE_URL}
                    target="_blank"
                    rel="noreferrer"
                    className="rounded-full border border-cyan-300/25 bg-cyan-300/10 px-4 py-2 text-xs text-cyan-200 transition hover:bg-cyan-300/15"
                  >
                    Open traces
                  </a>
                  <a
                    href="/api/v1/health"
                    target="_blank"
                    rel="noreferrer"
                    className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs text-slate-100 transition hover:bg-white/10"
                  >
                    Health endpoint
                  </a>
                  <a
                    href={GRAFANA_DASHBOARD_URL}
                    target="_blank"
                    rel="noreferrer"
                    className="rounded-full border border-amber-300/25 bg-amber-300/10 px-4 py-2 text-xs text-amber-100 transition hover:bg-amber-300/15"
                  >
                    Grafana dashboards
                  </a>
                </div>
              </div>
            </div>

            <div className={evalError || (evalSummary?.sample_count ?? 0) > 0 ? 'grid gap-4 lg:grid-cols-2' : ''}>
              {evalError || (evalSummary?.sample_count ?? 0) > 0 ? (
                <div className="rounded-[2rem] border border-white/10 bg-white/5 p-5 shadow-glow backdrop-blur-xl">
                  <div className="mb-4">
                    <p className="text-xs font-semibold uppercase tracking-[0.3em] text-cyan-200/80">Answer quality</p>
                    <h2 className="mt-1 text-xl font-semibold text-white">Evaluation summary</h2>
                  </div>

                  {evalError ? (
                    <div className="rounded-2xl border border-amber-300/20 bg-amber-300/10 p-4 text-sm leading-6 text-amber-100">
                      {evalError}
                    </div>
                  ) : (
                    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                      <MetricCard
                        label="Samples"
                        value={evalSummary?.sample_count ?? 0}
                        tone="cyan"
                        sub={`${evalSummary?.period_days ?? 7} days`}
                      />
                      <MetricCard label="Overall" value={formatScore(evalSummary?.overall_score)} tone="emerald" />
                      <MetricCard label="Faithful" value={formatScore(evalSummary?.faithfulness)} tone="emerald" />
                      <MetricCard label="Relevant" value={formatScore(evalSummary?.answer_relevancy)} tone="emerald" />
                    </div>
                  )}
                </div>
              ) : null}

              <div className="rounded-[2rem] border border-white/10 bg-white/5 p-5 shadow-glow backdrop-blur-xl">
                <div className="mb-4">
                  <p className="text-xs font-semibold uppercase tracking-[0.3em] text-cyan-200/80">Where to look</p>
                  <h2 className="mt-1 text-xl font-semibold text-white">Monitoring map</h2>
                </div>

                <div className="grid gap-3">
                  <a
                    href={GRAFANA_DASHBOARD_URL}
                    target="_blank"
                    rel="noreferrer"
                    className="rounded-2xl border border-amber-300/20 bg-amber-300/10 p-4 transition hover:bg-amber-300/15"
                  >
                    <span className="block text-sm font-semibold text-amber-100">Grafana: production metrics</span>
                    <span className="mt-1 block text-sm leading-6 text-slate-300">
                      Use this for request volume, latency, failures, feedback, container health, Redis, and Postgres.
                    </span>
                  </a>
                  <a
                    href={LANGFUSE_URL}
                    target="_blank"
                    rel="noreferrer"
                    className="rounded-2xl border border-cyan-300/20 bg-cyan-300/10 p-4 transition hover:bg-cyan-300/15"
                  >
                    <span className="block text-sm font-semibold text-cyan-100">Langfuse: answer traces</span>
                    <span className="mt-1 block text-sm leading-6 text-slate-300">
                      Open your project, then check Traces after asking a question in this app.
                    </span>
                  </a>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </section>
  )
}
