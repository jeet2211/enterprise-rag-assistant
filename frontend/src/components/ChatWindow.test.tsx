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
        onClearConversation={onClearConversation}
        onToggleSidebar={vi.fn()}
        sidebarOpen={false}
      />
    )

    fireEvent.click(screen.getByRole('button', { name: /clear conversation/i }))

    expect(onClearConversation).toHaveBeenCalled()
  })
})
