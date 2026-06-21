import { act, renderHook, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useDocuments } from './useDocuments'
import { deleteDocument, fetchDocument, fetchDocuments, uploadDocument } from '../api/client'

vi.mock('../api/client', () => ({
  deleteDocument: vi.fn(),
  fetchDocument: vi.fn(),
  fetchDocuments: vi.fn(),
  uploadDocument: vi.fn(),
}))

const fetchDocumentsMock = vi.mocked(fetchDocuments)
const uploadDocumentMock = vi.mocked(uploadDocument)
const deleteDocumentMock = vi.mocked(deleteDocument)
const fetchDocumentMock = vi.mocked(fetchDocument)

describe('useDocuments', () => {
  beforeEach(() => {
    fetchDocumentsMock.mockReset()
    uploadDocumentMock.mockReset()
    deleteDocumentMock.mockReset()
    fetchDocumentMock.mockReset()
    sessionStorage.clear()
  })

  it('loads, uploads, and refreshes the document list', async () => {
    const initialDocuments = [
      {
        id: 'doc-1',
        filename: 'report.pdf',
        page_count: 0,
        status: 'processing' as const,
        uploaded_at: '2024-01-01T00:00:00.000Z',
        file_size_bytes: 1024,
      },
    ]
    const refreshedDocuments = [
      {
        id: 'doc-1',
        filename: 'report.pdf',
        page_count: 12,
        status: 'ready' as const,
        uploaded_at: '2024-01-01T00:00:00.000Z',
        file_size_bytes: 1024,
      },
    ]

    fetchDocumentsMock.mockResolvedValueOnce(initialDocuments).mockResolvedValueOnce(refreshedDocuments)
    uploadDocumentMock.mockImplementation(async (_file, onProgress) => {
      onProgress?.(100)
      return {
        document_id: 'doc-2',
        filename: 'manual.pdf',
        status: 'processing',
        message: 'queued',
      }
    })

    const { result } = renderHook(() => useDocuments())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })
    expect(result.current.documents).toEqual(initialDocuments)

    await act(async () => {
      await result.current.upload(new File(['pdf'], 'manual.pdf', { type: 'application/pdf' }))
    })

    expect(uploadDocumentMock).toHaveBeenCalledTimes(1)
    expect(result.current.documents).toEqual(refreshedDocuments)
    expect(result.current.uploading).toBe(false)
    expect(result.current.uploadProgress).toBe(0)
  })

  it('deletes a document and refreshes the list', async () => {
    const initialDocuments = [
      {
        id: 'doc-1',
        filename: 'report.pdf',
        page_count: 12,
        status: 'ready' as const,
        uploaded_at: '2024-01-01T00:00:00.000Z',
        file_size_bytes: 1024,
      },
    ]

    fetchDocumentsMock.mockResolvedValueOnce(initialDocuments).mockResolvedValueOnce([])
    deleteDocumentMock.mockResolvedValue(undefined)

    const { result } = renderHook(() => useDocuments())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    await act(async () => {
      await result.current.remove('doc-1')
    })

    expect(deleteDocumentMock).toHaveBeenCalledWith('doc-1')
    expect(result.current.documents).toEqual([])
  })
})
