import { CitationCard } from './CitationCard'
import { LoadingDots } from './LoadingDots'
import type { Message } from '../types'

interface MessageBubbleProps {
  message: Message
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[85%] rounded-3xl px-5 py-4 shadow-glow ${
          isUser
            ? 'bg-gradient-to-br from-cyan-400/20 to-sky-500/20 border border-cyan-300/20 text-white'
            : 'border border-white/10 bg-slate-950/70 text-slate-100'
        }`}
      >
        <div className="flex items-center gap-2 text-xs uppercase tracking-[0.25em] text-slate-400">
          <span>{isUser ? 'You' : 'Assistant'}</span>
          <span>•</span>
          <span>{new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
        </div>
        <div className="mt-3 whitespace-pre-wrap text-[15px] leading-7">
          {message.isPending ? (
            <span className="inline-flex items-center gap-2">
              <LoadingDots />
              <span className="text-slate-300">Generating answer</span>
            </span>
          ) : (
            message.content
          )}
        </div>
        {message.citations && message.citations.length > 0 ? (
          <div className="mt-4 grid gap-3">
            {message.citations.map((citation, index) => (
              <CitationCard key={`${citation.document_name}-${citation.page_number}-${index}`} citation={citation} index={index} />
            ))}
          </div>
        ) : null}
      </div>
    </div>
  )
}

