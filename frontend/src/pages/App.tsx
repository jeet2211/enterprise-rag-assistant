import { useEffect, useState } from 'react'
import { ChatWindow } from '../components/ChatWindow'
import { Dashboard } from '../components/Dashboard'
import { ErrorToast } from '../components/ErrorToast'
import { Sidebar } from '../components/Sidebar'
import { useChat } from '../hooks/useChat'
import { useDocuments } from '../hooks/useDocuments'
import { AuthProvider, useAuth } from '../hooks/useAuth'
import { AuthGuard } from '../components/AuthGuard'
import { LoginPage } from './LoginPage'
import { SignupPage } from './SignupPage'
import { setAccessToken } from '../api/client'

function AppContent() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [showDashboard, setShowDashboard] = useState(false)
  const [authView, setAuthView] = useState<'login' | 'signup'>('login')

  const { logout, token } = useAuth()
  const authReady = Boolean(token)

  // Keep the API client in sync with the current access token.
  // This runs whenever the token changes (login / logout / refresh).
  useEffect(() => {
    setAccessToken(token)
  }, [token])

  // Listen for the global auth:logout event dispatched by the 401 interceptor
  // in client.ts when a token refresh fails. Reset to login view.
  useEffect(() => {
    const handler = () => { logout() }
    window.addEventListener('auth:logout', handler)
    return () => window.removeEventListener('auth:logout', handler)
  }, [logout])

  const documents = useDocuments({ enabled: authReady })
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
    <AuthGuard
      fallback={
        authView === 'login' ? (
          <LoginPage onSuccess={() => setAuthView('login')} onSwitchToSignup={() => setAuthView('signup')} />
        ) : (
          <SignupPage onSuccess={() => setAuthView('login')} onSwitchToLogin={() => setAuthView('login')} />
        )
      }
    >
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
            {/* Header / Logout button */}
            <div className="absolute top-4 right-4 z-50">
              <button
                onClick={logout}
                className="px-4 py-2 bg-white/5 hover:bg-white/10 text-slate-300 hover:text-white rounded-xl text-sm font-medium transition-all border border-white/10 flex items-center gap-2"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                Sign Out
              </button>
            </div>

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
    </AuthGuard>
  )
}

export function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}
