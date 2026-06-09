import type { ChatRequest, ChatResponse, DocumentDetail, DocumentItem, UploadResponse } from '../types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1'

type ProgressHandler = (progress: number) => void

async function parseJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const body = await response.text()
    throw new Error(body || `Request failed with status ${response.status}`)
  }
  return response.json() as Promise<T>
}

export async function fetchDocuments(): Promise<DocumentItem[]> {
  const response = await fetch(`${API_BASE_URL}/documents`)
  return parseJson<DocumentItem[]>(response)
}

export async function fetchDocument(documentId: string): Promise<DocumentDetail> {
  const response = await fetch(`${API_BASE_URL}/documents/${documentId}`)
  return parseJson<DocumentDetail>(response)
}

export async function deleteDocument(documentId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/documents/${documentId}`, { method: 'DELETE' })
  await parseJson(response)
}

export function uploadDocument(file: File, onProgress?: ProgressHandler): Promise<UploadResponse> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    xhr.open('POST', `${API_BASE_URL}/upload`)
    xhr.responseType = 'json'
    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable && onProgress) {
        onProgress(Math.round((event.loaded / event.total) * 100))
      }
    }
    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(xhr.response as UploadResponse)
      } else {
        reject(new Error(xhr.response?.detail ?? xhr.response?.message ?? `Upload failed with status ${xhr.status}`))
      }
    }
    xhr.onerror = () => reject(new Error('Network error during upload'))
    const formData = new FormData()
    formData.append('file', file)
    xhr.send(formData)
  })
}

export async function sendChat(payload: ChatRequest): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  return parseJson<ChatResponse>(response)
}

