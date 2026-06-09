import { FormEvent, useState } from 'react'
import { MessageBubble } from './MessageBubble'
import type { Message } from '../types'

interface ChatWindowProps {
  messages: Message[]
  sending: boolean
  onSend: (message: string) => Promise<void>
  onClearConversation: () => void
  onToggleSidebar: () => void
  sidebarOpen: boolean
}

export function ChatWindow({
  messages,
  sending,
  onSend,
  onClearConversation,
  onToggleSidebar,
  sidebarOpen,
}: ChatWindowProps) {
  const [value, setValue] = useState('')

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!value.trim()) return
    const next = value
    setValue('')
    await onSend(next)
  }

  return (
    <section className="flex min-h-screen flex-1 flex-col px-4 py-4 md:px-6 md:py-5">
      <div className="rounded-[2rem] border border-white/10 bg-white/5 p-4 shadow-glow backdrop-blur-xl md:p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.3em] text-cyan-200/80">Chat</p>
            <h1 className="mt-2 text-3xl font-semibold text-white md:text-4xl">Ask questions grounded in your PDFs</h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-300 md:text-base">
              Use the sidebar to upload documents, then ask for summaries, comparisons, or details.
            </p>
          </div>

          <div className="flex gap-2">
            <button
              type="button"
              onClick={onToggleSidebar}
              className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-100 md:hidden"
            >
              {sidebarOpen ? 'Hide docs' : 'Show docs'}
            </button>
            <button
              type="button"
              onClick={onClearConversation}
              className="rounded-full bg-white px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-100"
            >
              Clear conversation
            </button>
          </div>
        </div>
      </div>

      <div className="mt-4 flex min-h-0 flex-1 flex-col rounded-[2rem] border border-white/10 bg-slate-950/60 shadow-glow backdrop-blur-xl">
        <div className="flex-1 overflow-y-auto p-4 md:p-6">
          {messages.length === 0 ? (
            <div className="grid min-h-full place-items-center">
              <div className="max-w-xl rounded-[2rem] border border-dashed border-white/10 bg-white/5 px-6 py-10 text-center">
                <p className="text-sm font-semibold uppercase tracking-[0.3em] text-slate-400">Ready when you are</p>
                <h2 className="mt-3 text-2xl font-semibold text-white">Upload a PDF and ask anything from it</h2>
                <p className="mt-3 text-sm leading-6 text-slate-300">
                  Answers will include source citations so you can verify every claim.
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((message) => (
                <MessageBubble key={message.id} message={message} />
              ))}
            </div>
          )}
        </div>

        <div className="border-t border-white/10 p-4 md:p-6">
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
              className="rounded-2xl bg-gradient-to-r from-cyan-300 to-sky-300 px-5 py-3 font-semibold text-slate-950 transition hover:brightness-105 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {sending ? 'Sending...' : 'Send'}
            </button>
          </form>
        </div>
      </div>
    </section>
  )
}

