import { useCallback, useEffect, useMemo, useState } from 'react'
import { deleteDocument, fetchDocument, fetchDocuments, uploadDocument } from '../api/client'
import type { DocumentDetail, DocumentItem } from '../types'

export function useDocuments() {
  const [documents, setDocuments] = useState<DocumentItem[]>([])
  const [loading, setLoading] = useState(true)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    try {
      setError(null)
      const items = await fetchDocuments()
      setDocuments(items)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load documents')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void refresh()
  }, [refresh])

  useEffect(() => {
    const hasProcessing = documents.some((doc) => doc.status === 'processing')
    if (!hasProcessing) {
      return
    }

    const interval = window.setInterval(() => {
      void refresh()
    }, 3000)

    return () => window.clearInterval(interval)
  }, [documents, refresh])

  const upload = useCallback(
    async (file: File) => {
      setUploading(true)
      setUploadProgress(0)
      setError(null)
      try {
        await uploadDocument(file, setUploadProgress)
        await refresh()
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Upload failed')
        throw err
      } finally {
        setUploading(false)
        setUploadProgress(0)
      }
    },
    [refresh]
  )

  const remove = useCallback(
    async (documentId: string) => {
      setError(null)
      await deleteDocument(documentId)
      await refresh()
    },
    [refresh]
  )

  const getDocument = useCallback(async (documentId: string): Promise<DocumentDetail> => {
    return fetchDocument(documentId)
  }, [])

  const processingCount = useMemo(
    () => documents.filter((doc) => doc.status === 'processing').length,
    [documents]
  )

  return {
    documents,
    loading,
    uploadProgress,
    uploading,
    error,
    processingCount,
    refresh,
    upload,
    remove,
    getDocument,
    clearError: () => setError(null),
  }
}

