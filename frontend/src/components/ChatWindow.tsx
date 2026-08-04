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
  onOpenMonitoring: () => void
  onLogout: () => void
  sidebarOpen: boolean
}

export function ChatWindow({
  messages,
  sending,
  sessionId,
  selectedDocumentIds,
  onSend,
  onClearConversation,
  onToggleSidebar,
  onOpenMonitoring,
  onLogout,
  sidebarOpen,
}: ChatWindowProps) {
  const [value, setValue] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)
  const hasSelectedDocuments = selectedDocumentIds.length > 0

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!value.trim()) return
    if (!hasSelectedDocuments) return
    const next = value
    setValue('')
    await onSend(next)
  }

  function handleFollowUp(question: string) {
    setValue(question)
  }

  return (
    <section className="flex min-h-screen flex-1 flex-col px-4 py-4 md:px-6 md:py-5">
      <div className="border-b border-white/10 pb-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 className="text-lg font-semibold text-white md:text-xl">Chat</h1>
            <p className="mt-1 text-sm text-slate-400">
              {hasSelectedDocuments
                ? `Searching within ${selectedDocumentIds.length} selected document${selectedDocumentIds.length > 1 ? 's' : ''}`
                : 'Select a document from the Library before asking a question'}
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={onToggleSidebar}
              className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-xs text-slate-100 transition hover:bg-white/10 md:hidden"
            >
              {sidebarOpen ? 'Hide docs' : 'Show docs'}
            </button>
            <button
              type="button"
              onClick={onOpenMonitoring}
              className="rounded-lg border border-cyan-300/25 bg-cyan-300/10 px-3 py-2 text-xs text-cyan-200 transition hover:bg-cyan-300/15"
            >
              Monitoring
            </button>
            <button
              type="button"
              onClick={onClearConversation}
              className="rounded-lg bg-white px-4 py-2 text-xs font-semibold text-slate-950 transition hover:bg-cyan-100"
            >
              Clear
            </button>
            <button
              type="button"
              onClick={onLogout}
              className="rounded-lg border border-rose-300/20 bg-rose-300/10 px-3 py-2 text-xs text-rose-100 transition hover:bg-rose-300/15"
            >
              Sign Out
            </button>
          </div>
        </div>

        {hasSelectedDocuments ? (
          <div className="mt-3 flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 rounded-lg border border-cyan-300/25 bg-cyan-300/10 px-3 py-1 text-[11px] text-cyan-200">
              <span className="h-1.5 w-1.5 rounded-full bg-cyan-300" />
              Filtered to {selectedDocumentIds.length} doc{selectedDocumentIds.length > 1 ? 's' : ''}
            </span>
          </div>
        ) : (
          <div className="mt-3 rounded-xl border border-amber-300/20 bg-amber-300/10 px-3 py-2 text-xs text-amber-100">
            Choose at least one document in the Library to enable chat.
          </div>
        )}
      </div>

      <div className="flex min-h-0 flex-1 flex-col">
        <div className="flex-1 overflow-y-auto py-4 md:py-6 scrollbar-thin">
          {messages.length === 0 ? (
            <div className="grid min-h-[400px] place-items-center">
              <div className="max-w-lg text-center">
                <h2 className="text-xl font-semibold text-white">
                  {hasSelectedDocuments ? 'Ask a question about the selected document' : 'Select a document to start'}
                </h2>
                <p className="mt-2 text-sm text-slate-400">
                  {hasSelectedDocuments
                    ? 'Type your own question below. Answers will use only selected documents.'
                    : 'Open Documents in the left panel and choose the PDF you want to chat with.'}
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

        <div className="border-t border-white/10 py-4 md:py-5">
          <form onSubmit={handleSubmit} className="flex flex-col gap-3 md:flex-row">
            <label className="sr-only" htmlFor="question">
              Ask a question
            </label>
            <input
              id="question"
              value={value}
              onChange={(event) => setValue(event.target.value)}
              placeholder={
                hasSelectedDocuments
                  ? 'Ask about the selected document...'
                  : 'Select at least one document first...'
              }
              disabled={!hasSelectedDocuments}
              className="flex-1 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-300/40 focus:bg-white/10"
            />
            <button
              type="submit"
              disabled={sending || !value.trim() || !hasSelectedDocuments}
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
