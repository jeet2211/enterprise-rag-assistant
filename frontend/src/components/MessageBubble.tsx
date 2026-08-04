import { useCallback, useState } from 'react'
import { submitFeedback } from '../api/client'
import { CitationCard } from './CitationCard'
import { LoadingDots } from './LoadingDots'
import type { Message } from '../types'

interface MessageBubbleProps {
  message: Message
  sessionId: string
  onFollowUp?: (question: string) => void
  sendingDisabled?: boolean
}

interface Token {
  type: 'text' | 'bold' | 'citation'
  text: string
  index: number
}

// Custom light-weight parser for bold text and brackets citations
function parseInlineTokens(text: string, citations: any[] = []): Token[] {
  const tokens: Token[] = []
  // Regex matches:
  // 1) Bold: \*\*(.*?)\*\*
  // 2) Simple bracket citation: \[(Source\s+)?(\d+)\]
  // 3) Legacy file citation: \[(.*?),\s*p\.(\d+)\]
  const regex = /(\*\*(.*?)\*\*|\[(?:Source\s+)?(\d+)\]|\[([^\]]+?),\s*p\.(\d+)\])/g
  
  let lastIndex = 0
  let match: RegExpExecArray | null

  while ((match = regex.exec(text)) !== null) {
    const matchIndex = match.index
    
    if (matchIndex > lastIndex) {
      tokens.push({
        type: 'text',
        text: text.slice(lastIndex, matchIndex),
        index: -1,
      })
    }

    const fullMatch = match[0]
    
    if (fullMatch.startsWith('**')) {
      tokens.push({
        type: 'bold',
        text: match[2],
        index: -1,
      })
    } else if (match[3]) {
      const citationIdx = parseInt(match[3], 10) - 1
      tokens.push({
        type: 'citation',
        text: fullMatch,
        index: citationIdx >= 0 ? citationIdx : 0,
      })
    } else if (match[4]) {
      // Legacy citation resolution (matching document name and/or page number)
      const docName = match[4].toLowerCase()
      const pageNum = parseInt(match[5], 10)
      
      let resolvedIdx = citations.findIndex(
        (c) => c.page_number === pageNum && 
               (c.document_name.toLowerCase().includes(docName) || docName.includes(c.document_name.toLowerCase()))
      )
      if (resolvedIdx === -1) {
        resolvedIdx = citations.findIndex((c) => c.page_number === pageNum)
      }
      if (resolvedIdx === -1) {
        resolvedIdx = 0
      }
      
      tokens.push({
        type: 'citation',
        text: fullMatch,
        index: resolvedIdx,
      })
    }

    lastIndex = regex.lastIndex
  }

  if (lastIndex < text.length) {
    tokens.push({
      type: 'text',
      text: text.slice(lastIndex),
      index: -1,
    })
  }

  return tokens
}

function FormattedMessage({
  content,
  citations = [],
  onCitationClick,
}: {
  content: string
  citations?: any[]
  onCitationClick: (index: number) => void
}) {
  const lines = content.split('\n')

  return (
    <div className="space-y-3">
      {lines.map((line, lineIdx) => {
        const trimmed = line.trim()
        if (!trimmed) {
          return <div key={lineIdx} className="h-1.5" />
        }

        // Detect list structures
        const listMatch = trimmed.match(/^(\d+)\.\s+(.*)$/)
        const bulletMatch = trimmed.match(/^[*+-]\s+(.*)$/)

        let innerContent = trimmed
        let isListItem = false
        let listPrefix = ''

        if (listMatch) {
          isListItem = true
          listPrefix = `${listMatch[1]}. `
          innerContent = listMatch[2]
        } else if (bulletMatch) {
          isListItem = true
          listPrefix = '• '
          innerContent = bulletMatch[1]
        }

        const tokens = parseInlineTokens(innerContent, citations)

        const renderedLine = (
          <>
            {tokens.map((token, tokIdx) => {
              if (token.type === 'bold') {
                return (
                  <strong key={tokIdx} className="font-bold text-white">
                    {token.text}
                  </strong>
                )
              }
              if (token.type === 'citation') {
                return (
                  <button
                    key={tokIdx}
                    type="button"
                    onClick={() => onCitationClick(token.index)}
                    className="mx-0.5 inline-flex items-center rounded border border-white/10 px-1 text-[10px] font-medium text-cyan-200/80 transition hover:border-cyan-300/30 hover:text-cyan-100"
                    title={`View Source ${token.index + 1}`}
                  >
                    {token.index + 1}
                  </button>
                )
              }
              return <span key={tokIdx}>{token.text}</span>
            })}
          </>
        )

        if (isListItem) {
          return (
            <div key={lineIdx} className="flex items-start gap-2 text-[15px] leading-7">
              <span className="min-w-5 text-slate-400 select-none">{listPrefix}</span>
              <span className="flex-1">{renderedLine}</span>
            </div>
          )
        }

        return (
          <p key={lineIdx} className="text-[15px] leading-7 text-slate-200">
            {renderedLine}
          </p>
        )
      })}
    </div>
  )
}

export function MessageBubble({ message, sessionId, onFollowUp, sendingDisabled }: MessageBubbleProps) {
  const isUser = message.role === 'user'
  const [feedbackSent, setFeedbackSent] = useState<'good' | 'bad' | null>(null)
  const [feedbackPending, setFeedbackPending] = useState(false)
  const [sourcesOpen, setSourcesOpen] = useState(false)
  const [highlightedCitationIndex, setHighlightedCitationIndex] = useState<number | null>(null)

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
        // silently fail
      } finally {
        setFeedbackPending(false)
      }
    },
    [feedbackSent, feedbackPending, message.id, sessionId]
  )

  const handleCitationClick = useCallback((index: number) => {
    setSourcesOpen(true)
    setHighlightedCitationIndex(index)
    // Scroll and clear highlight after brief delay
    setTimeout(() => {
      const el = document.getElementById(`citation-card-${index}`)
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
      }
    }, 100)
  }, [])

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[92%] ${
          isUser
            ? 'rounded-2xl border border-cyan-300/20 bg-cyan-300/10 px-4 py-3 text-white'
            : 'px-1 py-2 text-slate-100'
        }`}
      >
        {isUser ? (
          <div className="mb-1 text-[11px] text-cyan-100/70">
            You · {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>
        ) : null}

        <div>
          {message.isPending ? (
            <span className="inline-flex items-center gap-2 text-sm text-slate-300">
              <LoadingDots />
              <span>Thinking...</span>
            </span>
          ) : (
            <FormattedMessage
              content={message.content}
              citations={message.citations}
              onCitationClick={handleCitationClick}
            />
          )}
        </div>

        {!isUser && message.citations && message.citations.length > 0 ? (
          <div className="mt-3">
            <button
              type="button"
              onClick={() => setSourcesOpen((prev) => !prev)}
              className="text-xs text-slate-400 transition hover:text-cyan-200"
            >
              {sourcesOpen ? 'Hide sources' : `Sources (${message.citations.length})`}
            </button>
            {sourcesOpen && (
              <div className="mt-2 grid gap-2">
                {message.citations.map((citation, index) => (
                  <CitationCard
                    key={`${citation.document_name}-${citation.page_number}-${index}`}
                    citation={citation}
                    index={index}
                    highlighted={highlightedCitationIndex === index}
                  />
                ))}
              </div>
            )}
          </div>
        ) : null}

        {!isUser && !message.isPending && (
          <div className="mt-3 flex items-center gap-3 text-xs text-slate-500">
            {message.latency_ms ? (
              <span>{message.latency_ms.toFixed(0)}ms</span>
            ) : (
              null
            )}
            <div className="flex items-center gap-1">
              {feedbackSent ? (
                <span>Feedback saved</span>
              ) : (
                <>
                  <button
                    type="button"
                    onClick={() => void handleFeedback('good')}
                    disabled={feedbackPending}
                    title="Good answer"
                    className="px-1 text-slate-500 transition hover:text-emerald-300 disabled:opacity-50"
                  >
                    Good
                  </button>
                  <span>·</span>
                  <button
                    type="button"
                    onClick={() => void handleFeedback('bad')}
                    disabled={feedbackPending}
                    title="Bad answer"
                    className="px-1 text-slate-500 transition hover:text-rose-300 disabled:opacity-50"
                  >
                    Bad
                  </button>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
