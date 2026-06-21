import { beforeEach, describe, expect, it, vi } from 'vitest'
import { deleteDocument, fetchDocument, fetchDocuments, sendChat, uploadDocument } from './client'

describe('api client', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('fetches the document list from the backend', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: vi.fn().mockResolvedValue([{ id: 'doc-1', filename: 'report.pdf' }]),
    })
    vi.stubGlobal('fetch', fetchMock)

    const documents = await fetchDocuments()

    expect(fetchMock).toHaveBeenCalledWith('http://localhost:8000/api/v1/documents')
    expect(documents).toEqual([{ id: 'doc-1', filename: 'report.pdf' }])
  })

  it('sends chat requests', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: vi.fn().mockResolvedValue({
        answer: 'hello',
        citations: [],
        session_id: 'session-1',
        sources_used: 0,
      }),
    })
    vi.stubGlobal('fetch', fetchMock)

    const response = await sendChat({ question: 'What is this?', session_id: 'session-1' })

    expect(fetchMock).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/chat',
      expect.objectContaining({
        method: 'POST',
      })
    )
    expect(response.answer).toBe('hello')
  })

  it('deletes a document', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: vi.fn().mockResolvedValue({
        document_id: 'doc-1',
        status: 'deleted',
        message: 'Document deleted successfully.',
      }),
    })
    vi.stubGlobal('fetch', fetchMock)

    await deleteDocument('doc-1')

    expect(fetchMock).toHaveBeenCalledWith('http://localhost:8000/api/v1/documents/doc-1', {
      method: 'DELETE',
    })
  })

  it('uploads a document and reports progress', async () => {
    class FakeXHR {
      responseType = ''
      status = 202
      response = {
        document_id: 'doc-1',
        filename: 'report.pdf',
        status: 'processing',
        message: 'ok',
      }
      upload = {
        onprogress: null as null | ((event: ProgressEvent) => void),
      }
      onload: null | (() => void) = null
      onerror: null | (() => void) = null
      open = vi.fn()
      send = vi.fn(() => {
        this.upload.onprogress?.({ lengthComputable: true, loaded: 50, total: 100 } as ProgressEvent)
        this.onload?.()
      })
    }

    vi.stubGlobal('XMLHttpRequest', FakeXHR as unknown as typeof XMLHttpRequest)

    const progressUpdates: number[] = []
    const result = await uploadDocument(new File(['pdf'], 'report.pdf', { type: 'application/pdf' }), (progress) => {
      progressUpdates.push(progress)
    })

    expect(progressUpdates).toEqual([50])
    expect(result.document_id).toBe('doc-1')
  })
})
