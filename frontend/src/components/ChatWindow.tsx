import { FormEvent, useEffect, useRef, useState } from 'react'
import { MessageBubble } from './MessageBubble'
import type { Message } from '../types'

interface ChatWindowProps {
  messages: Message[]
  sending: boolean
  sessionId: string
  selectedDocumentIds: string[]
  onSend: (message: string) => Promise<void>
  onClearConversation: () => void
  onToggleSidebar: () => void
  onToggleDashboard: () => void
  sidebarOpen: boolean
  showDashboard: boolean
}

export function ChatWindow({
  messages,
  sending,
  sessionId,
  selectedDocumentIds,
  onSend,
  onClearConversation,
  onToggleSidebar,
  onToggleDashboard,
  sidebarOpen,
  showDashboard,
}: ChatWindowProps) {
  const [value, setValue] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!value.trim()) return
    const next = value
    setValue('')
    await onSend(next)
  }

  function handleFollowUp(question: string) {
    setValue(question)
  }

  return (
    <section className="flex min-h-screen flex-1 flex-col px-4 py-4 md:px-6 md:py-5">
      {/* Header */}
      <div className="rounded-[2rem] border border-white/10 bg-white/5 p-4 shadow-glow backdrop-blur-xl md:p-5">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.3em] text-cyan-200/80">Chat</p>
            <h1 className="mt-1.5 text-2xl font-semibold text-white md:text-3xl">
              Ask questions grounded in your PDFs
            </h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-300">
              {selectedDocumentIds.length > 0
                ? `Searching within ${selectedDocumentIds.length} selected document${selectedDocumentIds.length > 1 ? 's' : ''}`
                : 'Searching across all documents'}
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={onToggleSidebar}
              className="rounded-full border border-white/10 bg-white/5 px-3 py-2 text-xs text-slate-100 transition hover:bg-white/10 md:hidden"
            >
              {sidebarOpen ? 'Hide docs' : 'Show docs'}
            </button>
            <button
              type="button"
              onClick={onToggleDashboard}
              className={`rounded-full border px-3 py-2 text-xs transition ${
                showDashboard
                  ? 'border-cyan-300/30 bg-cyan-300/10 text-cyan-200'
                  : 'border-white/10 bg-white/5 text-slate-100 hover:bg-white/10'
              }`}
            >
              Dashboard
            </button>
            <button
              type="button"
              onClick={onClearConversation}
              className="rounded-full bg-white px-4 py-2 text-xs font-semibold text-slate-950 transition hover:bg-cyan-100"
            >
              Clear
            </button>
          </div>
        </div>

        {/* Document filter pill */}
        {selectedDocumentIds.length > 0 && (
          <div className="mt-3 flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 rounded-full border border-cyan-300/25 bg-cyan-300/10 px-3 py-1 text-[11px] text-cyan-200">
              <span className="h-1.5 w-1.5 rounded-full bg-cyan-300" />
              Filtered to {selectedDocumentIds.length} doc{selectedDocumentIds.length > 1 ? 's' : ''}
            </span>
          </div>
        )}
      </div>

      {/* Message list */}
      <div className="mt-4 flex min-h-0 flex-1 flex-col rounded-[2rem] border border-white/10 bg-slate-950/60 shadow-glow backdrop-blur-xl">
        <div className="flex-1 overflow-y-auto p-4 md:p-6 scrollbar-thin">
          {messages.length === 0 ? (
            <div className="grid min-h-[400px] place-items-center">
              <div className="max-w-xl rounded-[2rem] border border-dashed border-white/10 bg-white/5 px-6 py-10 text-center">
                <p className="text-sm font-semibold uppercase tracking-[0.3em] text-slate-400">Ready when you are</p>
                <h2 className="mt-3 text-2xl font-semibold text-white">Upload a PDF and ask anything from it</h2>
                <p className="mt-3 text-sm leading-6 text-slate-300">
                  Answers include source citations, confidence scores, and follow-up suggestions so you can verify every claim.
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-5">
              {messages.map((message) => (
                <MessageBubble
                  key={message.id}
                  message={message}
                  sessionId={sessionId}
                  onFollowUp={handleFollowUp}
                  sendingDisabled={sending}
                />
              ))}
              <div ref={bottomRef} />
            </div>
          )}
        </div>

        {/* Input */}
        <div className="border-t border-white/10 p-4 md:p-5">
          <form onSubmit={handleSubmit} className="flex flex-col gap-3 md:flex-row">
            <label className="sr-only" htmlFor="question">
              Ask a question
            </label>
            <input
              id="question"
              value={value}
              onChange={(event) => setValue(event.target.value)}
              placeholder="Ask about a section, compare policies, summarize the document..."
              className="flex-1 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-300/40 focus:bg-white/10"
            />
            <button
              type="submit"
              disabled={sending || !value.trim()}
              className="rounded-2xl bg-gradient-to-r from-cyan-300 to-sky-300 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:brightness-105 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {sending ? 'Sending...' : 'Send'}
            </button>
          </form>
        </div>
      </div>
    </section>
  )
}
