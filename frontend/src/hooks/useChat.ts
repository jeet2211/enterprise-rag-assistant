import { useCallback, useEffect, useMemo, useState } from 'react'
import { sendChatStream } from '../api/client'
import type { Confidence, Message } from '../types'

const SESSION_STORAGE_KEY = 'enterprise-rag-session'
const SESSION_ID_MAX_LENGTH = 36

function createSessionId() {
  return crypto.randomUUID()
}

function readSessionId(): string {
  try {
    const stored = sessionStorage.getItem(SESSION_STORAGE_KEY)
    if (stored && stored.trim().length > 0 && stored.length <= SESSION_ID_MAX_LENGTH) {
      return stored
    }
  } catch {
    // If storage is unavailable, fall through to a fresh session id.
  }
  return createSessionId()
}

function createPendingMessage(): Message {
  return {
    id: crypto.randomUUID(),
    role: 'assistant',
    content: '',
    timestamp: new Date().toISOString(),
    isPending: true,
  }
}

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [sessionId, setSessionId] = useState<string>(() => readSessionId())
  const [sending, setSending] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    try {
      sessionStorage.setItem(SESSION_STORAGE_KEY, sessionId)
    } catch {
      // Ignore storage write failures; the active session id still works in-memory.
    }
  }, [sessionId])

  const clearConversation = useCallback(() => {
    setMessages([])
    const nextSessionId = createSessionId()
    setSessionId(nextSessionId)
    setError(null)
  }, [])

  const sendMessage = useCallback(
    async (question: string, documentIds?: string[]) => {
      const trimmed = question.trim()
      if (!trimmed || sending) return

      const userMessage: Message = {
        id: crypto.randomUUID(),
        role: 'user',
        content: trimmed,
        timestamp: new Date().toISOString(),
      }
      const pendingMessage = createPendingMessage()

      setMessages((current) => [...current, userMessage, pendingMessage])
      setSending(true)
      setError(null)

      try {
        const response = await sendChatStream(
          {
            question: trimmed,
            session_id: sessionId,
            top_k: 5,
            document_ids: documentIds && documentIds.length > 0 ? documentIds : null,
          },
          {
            onToken: (text) => {
              if (!text) return
              setMessages((current) =>
                current.map((message) =>
                  message.id === pendingMessage.id
                    ? { ...message, content: `${message.content}${text}` }
                    : message
                )
              )
            },
            onReplace: (text) => {
              setMessages((current) =>
                current.map((message) =>
                  message.id === pendingMessage.id ? { ...message, content: text } : message
                )
              )
            },
            onTrace: (data) => {
              setMessages((current) =>
                current.map((message) =>
                  message.id === pendingMessage.id
                    ? {
                        ...message,
                        confidence: data.confidence as Confidence,
                        trace_id: data.trace_id,
                      }
                    : message
                )
              )
            },
          }
        )

        setMessages((current) =>
          current.map((message) =>
            message.id === pendingMessage.id
              ? {
                  ...message,
                  content: response.answer,
                  citations: response.citations,
                  confidence: response.confidence as Confidence,
                  evidence_status: response.evidence_status,
                  answer_style: response.answer_style,
                  trace_id: response.trace_id,
                  follow_up_questions: response.follow_up_questions,
                  latency_ms: response.latency_ms,
                  isPending: false,
                }
              : message
          )
        )
      } catch (err) {
        const errMessage = err instanceof Error ? err.message : 'Failed to send message'
        setError(errMessage)
        setMessages((current) =>
          current.map((entry) =>
            entry.id === pendingMessage.id
              ? {
                  ...entry,
                  content: `Sorry, I could not answer that. ${errMessage}`,
                  confidence: 'not_found' as Confidence,
                  isPending: false,
                }
              : entry
          )
        )
      } finally {
        setSending(false)
      }
    },
    [sending, sessionId]
  )

  const assistantCount = useMemo(
    () => messages.filter((message) => message.role === 'assistant').length,
    [messages]
  )

  return {
    messages,
    sending,
    error,
    sessionId,
    assistantCount,
    sendMessage,
    clearConversation,
    clearError: () => setError(null),
  }
}
