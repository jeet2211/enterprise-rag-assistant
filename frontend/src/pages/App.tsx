import { useState } from 'react'
import { ChatWindow } from '../components/ChatWindow'
import { Dashboard } from '../components/Dashboard'
import { ErrorToast } from '../components/ErrorToast'
import { Sidebar } from '../components/Sidebar'
import { useChat } from '../hooks/useChat'
import { useDocuments } from '../hooks/useDocuments'

export function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [showDashboard, setShowDashboard] = useState(false)

  const documents = useDocuments()
  const chat = useChat()

  const combinedError = chat.error ?? documents.error

  async function handleUpload(file: File) {
    await documents.upload(file)
  }

  async function handleDelete(documentId: string) {
    await documents.remove(documentId)
  }

  async function handleSend(question: string) {
    await chat.sendMessage(question, documents.selectedDocumentIds)
  }

  return (
    <div className="min-h-screen bg-[#050816] text-white">
      {/* Background */}
      <div className="fixed inset-0 -z-10 bg-grid-radial opacity-90" />
      <div className="fixed inset-0 -z-20 bg-[radial-gradient(circle_at_top,_rgba(9,18,44,0.8),_transparent_40%),linear-gradient(180deg,_#050816_0%,_#02040a_100%)]" />

      <div className="flex min-h-screen">
        {/* Sidebar */}
        <Sidebar
          documents={documents.documents}
          loading={documents.loading}
          uploading={documents.uploading}
          uploadProgress={documents.uploadProgress}
          selectedDocumentIds={documents.selectedDocumentIds}
          onUpload={handleUpload}
          onDelete={handleDelete}
          onToggleDocumentSelection={documents.toggleDocumentSelection}
          onClearSelection={documents.clearSelection}
          openOnMobile={sidebarOpen}
          onCloseMobile={() => setSidebarOpen(false)}
        />

        {/* Mobile sidebar overlay */}
        {sidebarOpen ? (
          <button
            type="button"
            className="fixed inset-0 z-20 bg-black/60 md:hidden"
            aria-label="Close sidebar"
            onClick={() => setSidebarOpen(false)}
          />
        ) : null}

        {/* Main content */}
        <main className="relative z-10 flex min-h-screen flex-1 flex-col">
          {/* Dashboard panel */}
          {showDashboard && (
            <div className="px-4 pt-4 md:px-6 md:pt-5">
              <Dashboard onClose={() => setShowDashboard(false)} />
            </div>
          )}

          <ChatWindow
            messages={chat.messages}
            sending={chat.sending}
            sessionId={chat.sessionId}
            selectedDocumentIds={documents.selectedDocumentIds}
            onSend={handleSend}
            onClearConversation={chat.clearConversation}
            onToggleSidebar={() => setSidebarOpen((v) => !v)}
            onToggleDashboard={() => setShowDashboard((v) => !v)}
            sidebarOpen={sidebarOpen}
            showDashboard={showDashboard}
          />
        </main>
      </div>

      <ErrorToast
        message={combinedError}
        onDismiss={() => {
          chat.clearError()
          documents.clearError()
        }}
      />
    </div>
  )
}
