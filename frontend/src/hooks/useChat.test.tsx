import { act, renderHook, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useChat } from './useChat'
import { sendChat } from '../api/client'

vi.mock('../api/client', () => ({
  sendChat: vi.fn(),
}))

const sendChatMock = vi.mocked(sendChat)

describe('useChat', () => {
  beforeEach(() => {
    sendChatMock.mockReset()
    sessionStorage.clear()
  })

  it('sends a trimmed question and stores the response', async () => {
    sendChatMock.mockResolvedValue({
      answer: 'Generated answer',
      citations: [
        {
          document_name: 'policy.pdf',
          page_number: 2,
          chunk_preview: 'Relevant excerpt',
        },
      ],
      session_id: 'session-1',
      sources_used: 1,
    })

    const { result } = renderHook(() => useChat())

    await act(async () => {
      await result.current.sendMessage('   What does the policy say?   ')
    })

    await waitFor(() => {
      expect(result.current.messages).toHaveLength(2)
    })

    expect(sendChatMock).toHaveBeenCalledWith({
      question: 'What does the policy say?',
      session_id: result.current.sessionId,
      top_k: 5,
    })
    expect(result.current.messages[0].role).toBe('user')
    expect(result.current.messages[0].content).toBe('What does the policy say?')
    expect(result.current.messages[1].content).toBe('Generated answer')
    expect(result.current.messages[1].citations).toHaveLength(1)
  })

  it('keeps the conversation usable when the backend fails', async () => {
    sendChatMock.mockRejectedValueOnce(new Error('Network down'))

    const { result } = renderHook(() => useChat())

    await act(async () => {
      await result.current.sendMessage('Explain the policy')
    })

    await waitFor(() => {
      expect(result.current.error).toBe('Network down')
    })

    expect(result.current.messages[1].content).toContain('Sorry, I could not answer that.')
    expect(result.current.messages[1].isPending).toBe(false)
  })
})
