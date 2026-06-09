export function LoadingDots() {
  return (
    <span className="inline-flex items-center gap-1 text-slate-300">
      <span className="h-2 w-2 animate-bounce rounded-full bg-cyan-300 [animation-delay:-0.2s]" />
      <span className="h-2 w-2 animate-bounce rounded-full bg-cyan-300 [animation-delay:-0.1s]" />
      <span className="h-2 w-2 animate-bounce rounded-full bg-cyan-300" />
    </span>
  )
}

