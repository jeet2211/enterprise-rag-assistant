import { useRef, useState } from 'react'

interface UploadZoneProps {
  onUpload: (file: File) => Promise<void>
  uploading: boolean
  progress: number
}

export function UploadZone({ onUpload, uploading, progress }: UploadZoneProps) {
  const inputRef = useRef<HTMLInputElement | null>(null)
  const [dragActive, setDragActive] = useState(false)
  const [localError, setLocalError] = useState<string | null>(null)

  async function handleFiles(fileList: FileList | null) {
    const file = fileList?.[0]
    if (!file) return
    if (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
      setLocalError('Please upload a PDF file.')
      return
    }
    setLocalError(null)
    try {
      await onUpload(file)
    } catch (error) {
      setLocalError(error instanceof Error ? error.message : 'Upload failed')
    }
  }

  return (
    <div
      className={`rounded-3xl border border-dashed px-4 py-5 transition ${
        dragActive ? 'border-cyan-300 bg-cyan-300/10' : 'border-white/15 bg-white/5'
      }`}
      onDragOver={(event) => {
        event.preventDefault()
        setDragActive(true)
      }}
      onDragLeave={() => setDragActive(false)}
      onDrop={async (event) => {
        event.preventDefault()
        setDragActive(false)
        await handleFiles(event.dataTransfer.files)
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept="application/pdf"
        className="hidden"
        onChange={async (event) => {
          await handleFiles(event.target.files)
          event.target.value = ''
        }}
      />
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.28em] text-cyan-200/80">Upload PDF</p>
          <h3 className="mt-2 text-lg font-semibold text-white">Drop a document or choose one to start chatting</h3>
          <p className="mt-1 text-sm leading-6 text-slate-300">
            Files are processed in the background, then indexed for grounded answers with citations.
          </p>
        </div>
        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          className="shrink-0 rounded-full bg-white px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-100 disabled:cursor-not-allowed disabled:opacity-50"
          disabled={uploading}
        >
          {uploading ? 'Uploading...' : 'Choose file'}
        </button>
      </div>

      <div className="mt-4">
        <div className="h-2 overflow-hidden rounded-full bg-white/10">
          <div
            className="h-full rounded-full bg-gradient-to-r from-cyan-300 via-sky-300 to-amber-300 transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
        <div className="mt-2 flex items-center justify-between text-xs text-slate-400">
          <span>{uploading ? 'Uploading and processing...' : 'PDF only, max size configured in .env'}</span>
          <span>{progress}%</span>
        </div>
      </div>

      {localError ? <p className="mt-3 text-sm text-rose-300">{localError}</p> : null}
    </div>
  )
}
