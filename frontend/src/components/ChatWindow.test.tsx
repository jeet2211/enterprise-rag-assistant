import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { ChatWindow } from './ChatWindow'

describe('ChatWindow', () => {
  it('submits trimmed questions and clears the input', async () => {
    const onSend = vi.fn().mockResolvedValue(undefined)

    render(
      <ChatWindow
        messages={[]}
        sending={false}
        onSend={onSend}
        onSuggestionSelect={vi.fn()}
        onClearConversation={vi.fn()}
        onToggleSidebar={vi.fn()}
        sidebarOpen={false}
      />
    )

    const input = screen.getByPlaceholderText(/ask about a section/i)
    fireEvent.change(input, { target: { value: '  Summarize page 2  ' } })
    fireEvent.submit(screen.getByRole('button', { name: /send/i }).closest('form') as HTMLFormElement)

    expect(onSend).toHaveBeenCalledWith('  Summarize page 2  ')
    expect((input as HTMLInputElement).value).toBe('')
  })

  it('clears the conversation when requested', () => {
    const onClearConversation = vi.fn()

    render(
      <ChatWindow
        messages={[]}
        sending={false}
        onSend={vi.fn()}
        onSuggestionSelect={vi.fn()}
        onClearConversation={onClearConversation}
        onToggleSidebar={vi.fn()}
        sidebarOpen={false}
      />
    )

    fireEvent.click(screen.getByRole('button', { name: /clear conversation/i }))

    expect(onClearConversation).toHaveBeenCalled()
  })

  it('renders and sends suggested follow-up questions', async () => {
    const onSuggestionSelect = vi.fn().mockResolvedValue(undefined)

    render(
      <ChatWindow
        messages={[
          {
            id: 'msg-1',
            role: 'assistant',
            content: 'Generated answer',
            suggestedQuestions: ['Summarize the key ideas from policy.pdf page 5.'],
            timestamp: new Date().toISOString(),
          },
        ]}
        sending={false}
        onSend={vi.fn()}
        onSuggestionSelect={onSuggestionSelect}
        onClearConversation={vi.fn()}
        onToggleSidebar={vi.fn()}
        sidebarOpen={false}
      />
    )

    fireEvent.click(screen.getByRole('button', { name: /summarize the key ideas/i }))

    expect(onSuggestionSelect).toHaveBeenCalledWith('Summarize the key ideas from policy.pdf page 5.')
  })
})
