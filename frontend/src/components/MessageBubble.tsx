import { useCallback, useState } from 'react'
import { submitFeedback } from '../api/client'
import { CitationCard } from './CitationCard'
import { ConfidenceBadge } from './ConfidenceBadge'
import { FollowUpChips } from './FollowUpChips'
import { LoadingDots } from './LoadingDots'
import type { Confidence, Message } from '../types'

interface MessageBubbleProps {
  message: Message
  sessionId: string
  onFollowUp?: (question: string) => void
  sendingDisabled?: boolean
}

export function MessageBubble({ message, sessionId, onFollowUp, sendingDisabled }: MessageBubbleProps) {
  const isUser = message.role === 'user'
  const [feedbackSent, setFeedbackSent] = useState<'good' | 'bad' | null>(null)
  const [feedbackPending, setFeedbackPending] = useState(false)

  const handleFeedback = useCallback(
    async (rating: 'good' | 'bad') => {
      if (feedbackSent || feedbackPending) return
      setFeedbackPending(true)
      try {
        await submitFeedback({
          message_id: message.id,
          session_id: sessionId,
          rating,
        })
        setFeedbackSent(rating)
      } catch {
        // silently fail — don't interrupt UX for feedback errors
      } finally {
        setFeedbackPending(false)
      }
    },
    [feedbackSent, feedbackPending, message.id, sessionId]
  )

  const confidence = message.confidence as Confidence | undefined

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[88%] rounded-3xl px-5 py-4 shadow-glow ${
          isUser
            ? 'bg-gradient-to-br from-cyan-400/20 to-sky-500/20 border border-cyan-300/20 text-white'
            : 'border border-white/10 bg-slate-950/70 text-slate-100'
        }`}
      >
        {/* Header row */}
        <div className="flex flex-wrap items-center gap-2 text-xs uppercase tracking-[0.25em] text-slate-400">
          <span>{isUser ? 'You' : 'Assistant'}</span>
          <span>•</span>
          <span>{new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
          {!isUser && confidence && !message.isPending && (
            <ConfidenceBadge confidence={confidence} />
          )}
        </div>

        {/* Message content */}
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

        {/* Citations */}
        {message.citations && message.citations.length > 0 ? (
          <div className="mt-4 grid gap-2">
            {message.citations.map((citation, index) => (
              <CitationCard
                key={`${citation.document_name}-${citation.page_number}-${index}`}
                citation={citation}
                index={index}
              />
            ))}
          </div>
        ) : null}

        {/* Follow-up chips */}
        {!isUser && !message.isPending && message.follow_up_questions && message.follow_up_questions.length > 0 && (
          <FollowUpChips
            questions={message.follow_up_questions}
            onSelect={onFollowUp ?? (() => {})}
            disabled={sendingDisabled}
          />
        )}

        {/* Feedback buttons — only for assistant messages that have been delivered */}
        {!isUser && !message.isPending && (
          <div className="mt-4 flex items-center justify-between gap-3">
            {message.latency_ms ? (
              <span className="text-[10px] text-slate-600">{message.latency_ms.toFixed(0)}ms</span>
            ) : <span />}
            <div className="flex items-center gap-2">
              {feedbackSent ? (
                <span className="text-[10px] text-slate-400">
                  Thanks for the feedback {feedbackSent === 'good' ? '👍' : '👎'}
                </span>
              ) : (
                <>
                  <button
                    type="button"
                    onClick={() => void handleFeedback('good')}
                    disabled={feedbackPending}
                    title="Good answer"
                    className="rounded-full border border-white/10 px-2.5 py-1 text-xs text-slate-300 transition hover:border-emerald-400/30 hover:bg-emerald-400/10 hover:text-emerald-300 disabled:opacity-50"
                  >
                    👍
                  </button>
                  <button
                    type="button"
                    onClick={() => void handleFeedback('bad')}
                    disabled={feedbackPending}
                    title="Bad answer"
                    className="rounded-full border border-white/10 px-2.5 py-1 text-xs text-slate-300 transition hover:border-rose-400/30 hover:bg-rose-400/10 hover:text-rose-300 disabled:opacity-50"
                  >
                    👎
                  </button>
                </>
              )}
            </div>
          </div>
        )}

        {/* Trace ID (debug) */}
        {!isUser && message.trace_id && (
          <p className="mt-2 text-[9px] font-mono text-slate-700 select-all" title="Request trace ID">
            trace: {message.trace_id}
          </p>
        )}
      </div>
    </div>
  )
}
