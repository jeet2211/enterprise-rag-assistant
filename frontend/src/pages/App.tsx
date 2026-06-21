import { useMemo, useState } from 'react'
import { ChatWindow } from '../components/ChatWindow'
import { ErrorToast } from '../components/ErrorToast'
import { Sidebar } from '../components/Sidebar'
import { useChat } from '../hooks/useChat'
import { useDocuments } from '../hooks/useDocuments'
import type { DocumentItem } from '../types'

export function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [activeDocumentId, setActiveDocumentId] = useState<string | null>(null)
  const documents = useDocuments()
  const chat = useChat()

  const activeDocument = useMemo(
    () => documents.documents.find((document) => document.id === activeDocumentId) ?? null,
    [documents.documents, activeDocumentId]
  )

  const combinedError = chat.error ?? documents.error

  async function handleUpload(file: File) {
    await documents.upload(file)
  }

  async function handleDelete(documentId: string) {
    await documents.remove(documentId)
    if (activeDocumentId === documentId) {
      setActiveDocumentId(null)
    }
  }

  function handleDocumentSelect(document: DocumentItem) {
    setActiveDocumentId(document.id)
    setSidebarOpen(false)
  }

  return (
    <div className="min-h-screen bg-[#050816] text-white">
      <div className="fixed inset-0 -z-10 bg-grid-radial opacity-90" />
      <div className="fixed inset-0 -z-20 bg-[radial-gradient(circle_at_top,_rgba(9,18,44,0.8),_transparent_40%),linear-gradient(180deg,_#050816_0%,_#02040a_100%)]" />

      <div className="flex min-h-screen">
        <Sidebar
          documents={documents.documents}
          loading={documents.loading}
          uploading={documents.uploading}
          uploadProgress={documents.uploadProgress}
          onUpload={handleUpload}
          onDelete={handleDelete}
          onSelectDocument={handleDocumentSelect}
          activeDocumentId={activeDocumentId}
          openOnMobile={sidebarOpen}
          onCloseMobile={() => setSidebarOpen(false)}
        />

        {sidebarOpen ? (
          <button
            type="button"
            className="fixed inset-0 z-20 bg-black/60 md:hidden"
            aria-label="Close sidebar"
            onClick={() => setSidebarOpen(false)}
          />
        ) : null}

        <main className="relative z-10 flex min-h-screen flex-1">
          <ChatWindow
            messages={chat.messages}
            sending={chat.sending}
            onSend={chat.sendMessage}
            onSuggestionSelect={chat.sendMessage}
            onClearConversation={chat.clearConversation}
            onToggleSidebar={() => setSidebarOpen((value) => !value)}
            sidebarOpen={sidebarOpen}
          />
        </main>
      </div>

      <ErrorToast message={combinedError} onDismiss={() => {
        chat.clearError()
        documents.clearError()
      }} />

      {activeDocument ? (
        <div className="fixed bottom-4 left-4 z-40 rounded-2xl border border-white/10 bg-slate-950/90 px-4 py-3 text-xs text-slate-300 shadow-glow backdrop-blur">
          Selected document: <span className="font-semibold text-white">{activeDocument.filename}</span>
        </div>
      ) : null}
    </div>
  )
}
