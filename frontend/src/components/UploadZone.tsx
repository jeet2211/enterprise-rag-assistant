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
      className={`rounded-2xl border border-dashed px-3 py-3 transition ${
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
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.28em] text-cyan-200/80">Upload PDF</p>
          <p className="mt-1 text-xs text-slate-400">Add a PDF to the library.</p>
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

      <div className="mt-3">
        <div className="h-1.5 overflow-hidden rounded-full bg-white/10">
          <div
            className="h-full rounded-full bg-gradient-to-r from-cyan-300 via-sky-300 to-amber-300 transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
        <div className="mt-2 flex items-center justify-between text-xs text-slate-400">
          <span>{uploading ? 'Uploading and processing...' : 'PDF only'}</span>
          <span>{progress}%</span>
        </div>
      </div>

      {localError ? <p className="mt-3 text-sm text-rose-300">{localError}</p> : null}
    </div>
  )
}
