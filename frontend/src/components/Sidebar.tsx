import { UploadZone } from './UploadZone'
import type { DocumentItem } from '../types'

interface SidebarProps {
  documents: DocumentItem[]
  loading: boolean
  uploading: boolean
  uploadProgress: number
  onUpload: (file: File) => Promise<void>
  onDelete: (documentId: string) => Promise<void>
  onSelectDocument?: (document: DocumentItem) => void
  activeDocumentId?: string | null
  openOnMobile: boolean
  onCloseMobile: () => void
}

export function Sidebar({
  documents,
  loading,
  uploading,
  uploadProgress,
  onUpload,
  onDelete,
  onSelectDocument,
  activeDocumentId,
  openOnMobile,
  onCloseMobile,
}: SidebarProps) {
  return (
    <aside
      className={`fixed inset-y-0 left-0 z-30 w-[88vw] max-w-sm border-r border-white/10 bg-slate-950/95 px-4 py-5 backdrop-blur-xl transition-transform duration-300 md:static md:z-auto md:w-[360px] md:translate-x-0 md:bg-transparent md:px-0 md:py-0 ${
        openOnMobile ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
      }`}
    >
      <div className="flex h-full flex-col gap-5 md:sticky md:top-0 md:h-screen md:p-5">
        <div className="rounded-3xl border border-white/10 bg-white/5 p-5 shadow-glow">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.3em] text-cyan-200/80">Documents</p>
              <h2 className="mt-2 text-2xl font-semibold text-white">Enterprise RAG Assistant</h2>
              <p className="mt-2 text-sm leading-6 text-slate-300">
                Upload PDFs, wait for indexing, then ask grounded questions with citations.
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

        <UploadZone onUpload={onUpload} uploading={uploading} progress={uploadProgress} />

        <div className="rounded-3xl border border-white/10 bg-slate-950/60 p-4 shadow-glow">
          <div className="mb-3 flex items-center justify-between">
            <h3 className="text-sm font-semibold uppercase tracking-[0.3em] text-slate-300">Library</h3>
            <span className="rounded-full bg-white/5 px-3 py-1 text-xs text-slate-300">{documents.length}</span>
          </div>

          <div className="max-h-[calc(100vh-360px)] space-y-3 overflow-y-auto pr-1">
            {loading ? (
              <div className="space-y-3">
                {Array.from({ length: 3 }).map((_, index) => (
                  <div key={index} className="animate-pulse rounded-2xl border border-white/10 bg-white/5 p-4">
                    <div className="h-4 w-2/3 rounded bg-white/10" />
                    <div className="mt-3 h-3 w-1/2 rounded bg-white/10" />
                  </div>
                ))}
              </div>
            ) : documents.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-white/10 bg-white/5 p-4 text-sm leading-6 text-slate-300">
                No documents yet. Upload a PDF to begin.
              </div>
            ) : (
              documents.map((document) => {
                const active = activeDocumentId === document.id
                return (
                  <div
                    key={document.id}
                    role="button"
                    tabIndex={0}
                    onClick={() => onSelectDocument?.(document)}
                    onKeyDown={(event) => {
                      if (event.key === 'Enter' || event.key === ' ') {
                        event.preventDefault()
                        onSelectDocument?.(document)
                      }
                    }}
                    className={`w-full cursor-pointer rounded-2xl border p-4 text-left transition ${
                      active
                        ? 'border-cyan-300/40 bg-cyan-300/10'
                        : 'border-white/10 bg-white/5 hover:bg-white/10'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <p className="text-sm font-medium text-white">{document.filename}</p>
                        <p className="mt-1 text-xs text-slate-400">
                          {document.page_count} pages · {Math.round(document.file_size_bytes / 1024)} KB
                        </p>
                      </div>
                      <span
                        className={`rounded-full px-2 py-1 text-[11px] uppercase tracking-[0.22em] ${
                          document.status === 'ready'
                            ? 'bg-emerald-400/15 text-emerald-200'
                            : document.status === 'failed'
                              ? 'bg-rose-400/15 text-rose-200'
                              : 'bg-amber-400/15 text-amber-200'
                        }`}
                      >
                        {document.status}
                      </span>
                    </div>
                    <div className="mt-3 flex items-center justify-between gap-3">
                      <span className="text-xs text-slate-400">
                        {new Date(document.uploaded_at).toLocaleDateString()}
                      </span>
                      <button
                        type="button"
                        onClick={async (event) => {
                          event.stopPropagation()
                          const confirmed = window.confirm(`Delete ${document.filename}?`)
                          if (confirmed) {
                            await onDelete(document.id)
                          }
                        }}
                        className="rounded-full border border-white/10 px-3 py-1 text-xs text-slate-200 transition hover:bg-white/10"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                )
              })
            )}
          </div>
        </div>
      </div>
    </aside>
  )
}
