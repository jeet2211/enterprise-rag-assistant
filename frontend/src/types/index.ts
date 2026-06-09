export interface DocumentItem {
  id: string
  filename: string
  page_count: number
  status: 'processing' | 'ready' | 'failed'
  uploaded_at: string
  file_size_bytes: number
}

export interface DocumentDetail extends DocumentItem {
  error_msg?: string | null
  updated_at: string
}

export interface Citation {
  document_name: string
  page_number: number
  chunk_preview: string
}

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  citations?: Citation[]
  timestamp: string
  isPending?: boolean
}

export interface ChatRequest {
  question: string
  session_id: string
  top_k?: number
}

export interface ChatResponse {
  answer: string
  citations: Citation[]
  session_id: string
  sources_used: number
}

export interface UploadResponse {
  document_id: string
  filename: string
  status: string
  message: string
}

