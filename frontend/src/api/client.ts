import type {
  ChatRequest,
  ChatResponse,
  DocumentDetail,
  DocumentItem,
  FeedbackRequest,
  HealthStats,
  UploadResponse,
} from '../types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1'

import { refreshToken } from './auth';

let accessToken: string | null = null;
export function setAccessToken(token: string | null): void { accessToken = token; }

async function authFetch(input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
  const options = init || {};
  const headers = new Headers(options.headers);
  if (accessToken) {
    headers.set('Authorization', `Bearer ${accessToken}`);
  }
  options.headers = headers;

  let response = await fetch(input, options);
  
  if (response.status === 401) {
    const tokens = await refreshToken();
    if (tokens) {
      setAccessToken(tokens.access_token);
      headers.set('Authorization', `Bearer ${tokens.access_token}`);
      response = await fetch(input, options);
    } else {
      window.dispatchEvent(new Event('auth:logout'));
    }
  }
  return response;
}

type ProgressHandler = (progress: number) => void

async function parseJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const body = await response.text()
    let detail = body
    try {
      const parsed = JSON.parse(body)
      detail = parsed?.detail ?? parsed?.message ?? body
    } catch {
      // body was not JSON
    }
    throw new Error(detail || `Request failed with status ${response.status}`)
  }
  return response.json() as Promise<T>
}

export async function fetchDocuments(): Promise<DocumentItem[]> {
  const response = await authFetch(`${API_BASE_URL}/documents`)
  return parseJson<DocumentItem[]>(response)
}

export async function fetchDocument(documentId: string): Promise<DocumentDetail> {
  const response = await authFetch(`${API_BASE_URL}/documents/${documentId}`)
  return parseJson<DocumentDetail>(response)
}

type DocumentStatusResponse = { id: string; status: string; error_msg?: string | null }

export async function fetchDocumentStatus(documentId: string): Promise<DocumentStatusResponse> {
  const response = await authFetch(`${API_BASE_URL}/documents/${documentId}/status`)
  return parseJson(response)
}

export async function deleteDocument(documentId: string): Promise<void> {
  const response = await authFetch(`${API_BASE_URL}/documents/${documentId}`, { method: 'DELETE' })
  await parseJson(response)
}

export function uploadDocument(file: File, onProgress?: ProgressHandler): Promise<UploadResponse> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    xhr.open('POST', `${API_BASE_URL}/upload`)
    if (accessToken) {
      xhr.setRequestHeader('Authorization', `Bearer ${accessToken}`)
    }
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
  const response = await authFetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  return parseJson<ChatResponse>(response)
}

interface ChatStreamHandlers {
  onToken: (text: string) => void
  onReplace?: (text: string) => void
  onTrace?: (data: Partial<ChatResponse>) => void
}

function parseSseBlock(block: string): { event: string; data: unknown } | null {
  let event = 'message'
  const dataLines: string[] = []
  for (const line of block.split('\n')) {
    if (line.startsWith('event:')) {
      event = line.slice('event:'.length).trim()
    } else if (line.startsWith('data:')) {
      dataLines.push(line.slice('data:'.length).trimStart())
    }
  }
  if (dataLines.length === 0) return null
  return { event, data: JSON.parse(dataLines.join('\n')) }
}

export async function sendChatStream(payload: ChatRequest, handlers: ChatStreamHandlers): Promise<ChatResponse> {
  const response = await authFetch(`${API_BASE_URL}/chat/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'text/event-stream' },
    body: JSON.stringify(payload),
  })

  if (!response.ok || !response.body) {
    return sendChat(payload)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  let finalResponse: ChatResponse | null = null

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const blocks = buffer.split('\n\n')
    buffer = blocks.pop() ?? ''

    for (const block of blocks) {
      const parsed = parseSseBlock(block.trim())
      if (!parsed) continue

      if (parsed.event === 'token') {
        handlers.onToken((parsed.data as { text?: string }).text ?? '')
      } else if (parsed.event === 'replace') {
        handlers.onReplace?.((parsed.data as { text?: string }).text ?? '')
      } else if (parsed.event === 'trace') {
        handlers.onTrace?.(parsed.data as Partial<ChatResponse>)
      } else if (parsed.event === 'final') {
        finalResponse = parsed.data as ChatResponse
      } else if (parsed.event === 'error') {
        throw new Error((parsed.data as { detail?: string }).detail ?? 'Streaming chat failed')
      }
    }
  }

  if (!finalResponse) {
    throw new Error('Streaming chat ended without a final response')
  }
  return finalResponse
}

export async function submitFeedback(payload: FeedbackRequest): Promise<void> {
  const response = await authFetch(`${API_BASE_URL}/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  await parseJson(response)
}

export async function fetchHealth(): Promise<HealthStats> {
  const response = await authFetch(`${API_BASE_URL}/health`)
  return parseJson<HealthStats>(response)
}
