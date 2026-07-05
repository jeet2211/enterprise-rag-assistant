import { useCallback, useEffect, useMemo, useState } from 'react'
import { deleteDocument, fetchDocuments, uploadDocument } from '../api/client'
import type { DocumentItem } from '../types'

// Statuses that are still in-flight and should trigger polling
const IN_PROGRESS_STATUSES = new Set([
  'uploaded',
  'extracting_text',
  'chunking',
  'embedding',
  'indexing',
])

export function useDocuments() {
  const [documents, setDocuments] = useState<DocumentItem[]>([])
  const [loading, setLoading] = useState(true)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedDocumentIds, setSelectedDocumentIds] = useState<string[]>([])

  const refresh = useCallback(async () => {
    try {
      setError(null)
      const items = await fetchDocuments()
      setDocuments(items)
      // Clean up selected IDs that no longer exist
      setSelectedDocumentIds((prev) => prev.filter((id) => items.some((doc) => doc.id === id)))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load documents')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void refresh()
  }, [refresh])

  // Poll while any document is still processing
  useEffect(() => {
    const hasInProgress = documents.some((doc) => IN_PROGRESS_STATUSES.has(doc.status))
    if (!hasInProgress) return

    const interval = window.setInterval(() => {
      void refresh()
    }, 2500)

    return () => window.clearInterval(interval)
  }, [documents, refresh])

  const upload = useCallback(
    async (file: File) => {
      setUploading(true)
      setUploadProgress(0)
      setError(null)
      try {
        const result = await uploadDocument(file, setUploadProgress)
        if (result.deduplicated) {
          setError(`"${result.filename}" was already uploaded and indexed. No duplicate processing needed.`)
        }
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
      setSelectedDocumentIds((prev) => prev.filter((id) => id !== documentId))
      await refresh()
    },
    [refresh]
  )

  const toggleDocumentSelection = useCallback((documentId: string) => {
    setSelectedDocumentIds((prev) =>
      prev.includes(documentId) ? prev.filter((id) => id !== documentId) : [...prev, documentId]
    )
  }, [])

  const clearSelection = useCallback(() => setSelectedDocumentIds([]), [])

  const processingCount = useMemo(
    () => documents.filter((doc) => IN_PROGRESS_STATUSES.has(doc.status)).length,
    [documents]
  )

  return {
    documents,
    loading,
    uploadProgress,
    uploading,
    error,
    processingCount,
    selectedDocumentIds,
    refresh,
    upload,
    remove,
    toggleDocumentSelection,
    clearSelection,
    clearError: () => setError(null),
  }
}
