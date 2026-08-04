import { useState } from 'react'
import { UploadZone } from './UploadZone'
import type { DocumentItem, DocumentStatus } from '../types'
import { type ChatSessionItem } from '../api/client'

interface SidebarProps {
  documents: DocumentItem[]
  loading: boolean
  uploading: boolean
  uploadProgress: number
  selectedDocumentIds: string[]
  onUpload: (file: File) => Promise<void>
  onDelete: (documentId: string) => Promise<void>
  onToggleDocumentSelection: (documentId: string) => void
  onClearSelection: () => void
  openOnMobile: boolean
  onCloseMobile: () => void

  // Chat Session Props
  sessions?: ChatSessionItem[]
  activeSessionId?: string
  onSelectSession?: (sessionId: string) => void
  onDeleteSession?: (sessionId: string) => void
  onNewChat?: () => void
  loadingSessions?: boolean
}

const STATUS_CONFIG: Record<
  DocumentStatus,
  { label: string; badgeClass: string; isLoading: boolean }
> = {
  uploaded: {
    label: 'Uploaded',
    badgeClass: 'bg-slate-400/15 text-slate-300',
    isLoading: true,
  },
  extracting_text: {
    label: 'Extracting',
    badgeClass: 'bg-sky-400/15 text-sky-300',
    isLoading: true,
  },
  chunking: {
    label: 'Chunking',
    badgeClass: 'bg-violet-400/15 text-violet-300',
    isLoading: true,
  },
  embedding: {
    label: 'Embedding',
    badgeClass: 'bg-amber-400/15 text-amber-300',
    isLoading: true,
  },
  indexing: {
    label: 'Indexing',
    badgeClass: 'bg-cyan-400/15 text-cyan-300',
    isLoading: true,
  },
  ready: {
    label: 'Ready',
    badgeClass: 'bg-emerald-400/15 text-emerald-200',
    isLoading: false,
  },
  failed: {
    label: 'Failed',
    badgeClass: 'bg-rose-400/15 text-rose-200',
    isLoading: false,
  },
}

function StatusBadge({ status }: { status: DocumentStatus }) {
  const config = STATUS_CONFIG[status] ?? STATUS_CONFIG.ready
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-[10px] font-medium uppercase tracking-[0.2em] ${config.badgeClass}`}>
      {config.isLoading && (
        <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-current" />
      )}
      {config.label}
    </span>
  )
}

export function Sidebar({
  documents,
  loading,
  uploading,
  uploadProgress,
  selectedDocumentIds,
  onUpload,
  onDelete,
  onToggleDocumentSelection,
  onClearSelection,
  openOnMobile,
  onCloseMobile,

  sessions = [],
  activeSessionId,
  onSelectSession,
  onDeleteSession,
  onNewChat,
  loadingSessions = false,
}: SidebarProps) {
  const [activeTab, setActiveTab] = useState<'chats' | 'docs'>('chats')
  const [search, setSearch] = useState('')

  const filteredDocs = search.trim()
    ? documents.filter((doc) => doc.filename.toLowerCase().includes(search.toLowerCase()))
    : documents

  return (
    <aside
      className={`fixed inset-y-0 left-0 z-30 w-[88vw] max-w-sm border-r border-white/10 bg-[#050816] px-4 py-5 backdrop-blur-xl transition-transform duration-300 md:static md:z-auto md:w-[350px] md:translate-x-0 md:bg-transparent md:px-0 md:py-0 ${
        openOnMobile ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
      }`}
    >
      <div className="flex h-full flex-col gap-3 md:sticky md:top-0 md:h-screen md:p-5">
        {/* Brand header */}
        <div className="rounded-3xl border border-white/10 bg-white/5 p-4 shadow-glow">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.3em] text-cyan-200/80">Enterprise Assistant</p>
              <h2 className="mt-1.5 text-xl font-semibold text-white">Enterprise RAG</h2>
              <p className="mt-1 text-xs leading-5 text-slate-400">
                Ask grounded questions with citation links.
              </p>
            </div>
            <button
              type="button"
              onClick={onCloseMobile}
              className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-200 md:hidden"
            >
              Close
            </button>
          </div>
        </div>

        {/* Tab Selector */}
        <div className="flex rounded-2xl bg-white/5 p-1 border border-white/10 shadow-glow">
          <button
            type="button"
            onClick={() => setActiveTab('chats')}
            className={`flex-1 py-2 text-xs font-semibold uppercase tracking-[0.1em] rounded-xl transition-all ${
              activeTab === 'chats'
                ? 'bg-cyan-300/10 text-cyan-200 border border-cyan-300/20 shadow-glow'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            💬 Chats
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('docs')}
            className={`flex-1 py-2 text-xs font-semibold uppercase tracking-[0.1em] rounded-xl transition-all ${
              activeTab === 'docs'
                ? 'bg-cyan-300/10 text-cyan-200 border border-cyan-300/20 shadow-glow'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            📂 Documents
          </button>
        </div>

        {/* Dynamic Content Panel */}
        <div className="flex min-h-0 flex-1 flex-col rounded-3xl border border-white/10 bg-slate-950/60 p-3 shadow-glow">
          {activeTab === 'chats' ? (
            <div className="flex flex-col h-full gap-3">
              {/* New Chat Button */}
              <button
                type="button"
                onClick={onNewChat}
                className="w-full flex items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-cyan-300 to-sky-300 py-3 text-sm font-semibold text-slate-950 transition hover:brightness-105 shadow-glow"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 4v16m8-8H4" />
                </svg>
                New Chat
              </button>

              <div className="mb-1 flex items-center justify-between text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                <span>Recent Conversations</span>
                <span className="rounded-full bg-white/5 px-2 py-0.5">{sessions.length}</span>
              </div>

              {/* Chat list */}
              <div className="flex-1 space-y-2 overflow-y-auto pr-0.5 scrollbar-thin">
                {loadingSessions ? (
                  <div className="space-y-2">
                    {Array.from({ length: 3 }).map((_, i) => (
                      <div key={i} className="animate-pulse rounded-2xl border border-white/10 bg-white/5 p-4">
                        <div className="h-4 w-2/3 rounded bg-white/10" />
                        <div className="mt-2 h-3 w-1/3 rounded bg-white/10" />
                      </div>
                    ))}
                  </div>
                ) : sessions.length === 0 ? (
                  <div className="rounded-2xl border border-dashed border-white/10 bg-white/5 p-6 text-xs leading-5 text-slate-400 text-center">
                    No past chats yet.<br />Start a new conversation above!
                  </div>
                ) : (
                  sessions.map((s) => {
                    const isActive = s.id === activeSessionId
                    return (
                      <div
                        key={s.id}
                        onClick={() => onSelectSession?.(s.id)}
                        className={`group relative flex items-center justify-between gap-2 p-3.5 rounded-2xl border cursor-pointer transition ${
                          isActive
                            ? 'border-cyan-300/40 bg-cyan-300/10 text-cyan-200'
                            : 'border-white/5 bg-white/5 hover:bg-white/10 text-slate-200'
                        }`}
                      >
                        <div className="min-w-0 flex-1 pr-6">
                          <p className="truncate text-sm font-medium" title={s.title || 'New Chat'}>
                            {s.title || 'New Chat'}
                          </p>
                          <p className="mt-1 text-[10px] text-slate-500">
                            {new Date(s.updated_at).toLocaleDateString()}
                          </p>
                        </div>
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation()
                            const confirmed = window.confirm('Delete this conversation?')
                            if (confirmed) onDeleteSession?.(s.id)
                          }}
                          className="absolute right-3 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 p-1.5 rounded-lg bg-slate-900/80 border border-white/10 text-slate-400 hover:text-rose-400 transition"
                          title="Delete chat"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-4v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>
                    )
                  })
                )}
              </div>
            </div>
          ) : (
            <div className="flex min-h-0 flex-col h-full gap-2.5">
              {/* Document Library List */}
              <UploadZone onUpload={onUpload} uploading={uploading} progress={uploadProgress} />

              <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                <span>Library</span>
                <div className="flex items-center gap-1.5">
                  {selectedDocumentIds.length > 0 && (
                    <button
                      type="button"
                      onClick={onClearSelection}
                      className="rounded-full bg-cyan-300/10 px-2 py-0.5 text-[10px] text-cyan-300 transition hover:bg-cyan-300/20"
                    >
                      Clear ({selectedDocumentIds.length})
                    </button>
                  )}
                  <span className="rounded-full bg-white/5 px-2 py-0.5">{documents.length}</span>
                </div>
              </div>

              {documents.length > 3 && (
                <input
                  type="search"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Search library…"
                  className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs text-white outline-none placeholder:text-slate-600 focus:border-cyan-300/30 focus:bg-white/10"
                />
              )}

              <div className="min-h-0 flex-1 space-y-2.5 overflow-y-auto pr-0.5 scrollbar-thin">
                {loading ? (
                  <div className="space-y-2.5">
                    {Array.from({ length: 3 }).map((_, i) => (
                      <div key={i} className="animate-pulse rounded-2xl border border-white/10 bg-white/5 p-4">
                        <div className="h-4 w-2/3 rounded bg-white/10" />
                        <div className="mt-2 h-3 w-1/2 rounded bg-white/10" />
                      </div>
                    ))}
                  </div>
                ) : filteredDocs.length === 0 ? (
                  <div className="rounded-2xl border border-dashed border-white/10 bg-white/5 p-4 text-xs leading-5 text-slate-400 text-center">
                    {search ? 'No documents match.' : 'No documents. Upload above!'}
                  </div>
                ) : (
                  filteredDocs.map((doc) => {
                    const selected = selectedDocumentIds.includes(doc.id)
                    const config = STATUS_CONFIG[doc.status] ?? STATUS_CONFIG.ready
                    return (
                      <div
                        key={doc.id}
                        role="button"
                        tabIndex={0}
                        onClick={() => onToggleDocumentSelection(doc.id)}
                        className={`w-full cursor-pointer rounded-2xl border p-3.5 text-left transition ${
                          selected
                            ? 'border-cyan-300/40 bg-cyan-300/10'
                            : 'border-white/10 bg-white/5 hover:bg-white/10'
                        }`}
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div
                            className={`mt-0.5 h-4 w-4 shrink-0 rounded border transition ${
                              selected
                                ? 'border-cyan-300 bg-cyan-300 text-slate-950'
                                : 'border-white/20 bg-white/5'
                            } flex items-center justify-center text-[10px] font-bold`}
                          >
                            {selected ? '✓' : ''}
                          </div>

                          <div className="min-w-0 flex-1">
                            <p className="truncate text-sm font-medium text-white" title={doc.filename}>
                              {doc.filename}
                            </p>
                            <p className="mt-0.5 text-[11px] text-slate-400">
                              {doc.page_count} pages
                              {doc.chunk_count > 0 ? ` · ${doc.chunk_count} chunks` : ''}
                              {' · '}
                              {Math.round(doc.file_size_bytes / 1024)} KB
                            </p>
                          </div>

                          <StatusBadge status={doc.status} />
                        </div>

                        <div className="mt-2.5 flex items-center justify-between gap-2">
                          <span className="text-[10px] text-slate-500">
                            {new Date(doc.uploaded_at).toLocaleDateString()}
                          </span>
                          <button
                            type="button"
                            onClick={async (e) => {
                              e.stopPropagation()
                              const confirmed = window.confirm(`Delete "${doc.filename}"?`)
                              if (confirmed) await onDelete(doc.id)
                            }}
                            className="rounded-full border border-white/10 px-2.5 py-0.5 text-[10px] text-slate-300 transition hover:border-rose-400/30 hover:bg-rose-400/10 hover:text-rose-300"
                          >
                            Delete
                          </button>
                        </div>

                        {doc.status === 'failed' && (
                          <p className="mt-2 text-[10px] text-rose-300/80">
                            Processing failed. Try re-uploading.
                          </p>
                        )}

                        {config.isLoading && (
                          <div className="mt-2 h-0.5 w-full overflow-hidden rounded-full bg-white/10">
                            <div className="h-full animate-pulse rounded-full bg-cyan-300/50" style={{ width: '60%' }} />
                          </div>
                        )}
                      </div>
                    )
                  })
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </aside>
  )
}
