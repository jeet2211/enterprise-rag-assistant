interface ErrorToastProps {
  message: string | null
  onDismiss: () => void
}

export function ErrorToast({ message, onDismiss }: ErrorToastProps) {
  if (!message) return null

  return (
    <div className="fixed bottom-4 right-4 z-50 max-w-md rounded-2xl border border-rose-400/20 bg-slate-950/95 px-4 py-3 text-sm text-rose-100 shadow-glow backdrop-blur">
      <div className="flex items-start gap-3">
        <div className="mt-1 h-2 w-2 rounded-full bg-rose-300" />
        <div className="flex-1">
          <p className="font-semibold text-white">Something needs attention</p>
          <p className="mt-1 leading-6 text-rose-100/80">{message}</p>
        </div>
        <button type="button" onClick={onDismiss} className="text-rose-100/70 transition hover:text-white">
          ✕
        </button>
      </div>
    </div>
  )
}

