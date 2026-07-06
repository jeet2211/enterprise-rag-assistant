export type DocumentStatus =
  | 'uploaded'
  | 'extracting_text'
  | 'chunking'
  | 'embedding'
  | 'indexing'
  | 'ready'
  | 'failed'

export interface DocumentItem {
  id: string
  filename: string
  page_count: number
  chunk_count: number
  status: DocumentStatus
  uploaded_at: string
  file_size_bytes: number
}

export interface DocumentDetail extends DocumentItem {
  file_hash?: string | null
  error_msg?: string | null
  updated_at: string
}

export type Confidence = 'high' | 'medium' | 'low' | 'not_found'
export type EvidenceStatus = 'exact' | 'partial' | 'not_found'
export type AnswerStyle = 'supported' | 'refused'

export interface Citation {
  document_name: string
  page_number: number
  chunk_preview: string
  token_count?: number
  doc_id?: string
  distance?: number
  section_title?: string
}

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  citations?: Citation[]
  confidence?: Confidence
  evidence_status?: EvidenceStatus
  answer_style?: AnswerStyle
  trace_id?: string
  follow_up_questions?: string[]
  latency_ms?: number
  timestamp: string
  isPending?: boolean
}

export interface ChatRequest {
  question: string
  session_id: string
  top_k?: number
  document_ids?: string[] | null
}

export interface ChatResponse {
  answer: string
  citations: Citation[]
  session_id: string
  sources_used: number
  confidence: Confidence
  evidence_status: EvidenceStatus
  answer_style: AnswerStyle
  trace_id: string
  follow_up_questions: string[]
  latency_ms: number
}

export interface UploadResponse {
  document_id: string
  filename: string
  status: string
  message: string
  deduplicated: boolean
}

export interface FeedbackRequest {
  message_id: string
  session_id: string
  rating: 'good' | 'bad'
  reason?: string | null
}

export interface HealthStats {
  status: string
  chromadb: string
  gemini: string
  uptime_seconds: number
  total_documents: number
  ready_documents: number
  failed_documents: number
  processing_documents: number
  total_chunks: number
}
