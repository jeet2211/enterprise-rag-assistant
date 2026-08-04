import { useEffect, useState } from 'react'
import { ChatWindow } from '../components/ChatWindow'
import { ErrorToast } from '../components/ErrorToast'
import { MonitoringPage } from '../components/MonitoringPage'
import { Sidebar } from '../components/Sidebar'
import { useChat } from '../hooks/useChat'
import { useDocuments } from '../hooks/useDocuments'
import { AuthProvider, useAuth } from '../hooks/useAuth'
import { AuthGuard } from '../components/AuthGuard'
import { LoginPage } from './LoginPage'
import { SignupPage } from './SignupPage'
import { setAccessToken } from '../api/client'

type AppRoute = 'app' | 'monitoring'

function getRoute(): AppRoute {
  return window.location.pathname.startsWith('/monitoring') ? 'monitoring' : 'app'
}

function AppContent() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [authView, setAuthView] = useState<'login' | 'signup'>('login')
  const [route, setRoute] = useState<AppRoute>(() => getRoute())

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

  useEffect(() => {
    const onPopState = () => setRoute(getRoute())
    window.addEventListener('popstate', onPopState)
    return () => window.removeEventListener('popstate', onPopState)
  }, [])

  function navigate(path: string) {
    if (window.location.pathname === path) return
    window.history.pushState({}, '', path)
    setRoute(getRoute())
  }

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
    if (documents.selectedDocumentIds.length === 0) {
      documents.clearError()
      chat.clearError()
      return
    }
    await chat.sendMessage(question, documents.selectedDocumentIds)
  }

  function handleNewChat() {
    chat.clearConversation()
    documents.clearSelection()
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
      {route === 'monitoring' ? (
        <div className="min-h-screen bg-[#050816] text-white">
          <div className="fixed inset-0 -z-10 bg-grid-radial opacity-90" />
          <div className="fixed inset-0 -z-20 bg-[radial-gradient(circle_at_top,_rgba(9,18,44,0.8),_transparent_40%),linear-gradient(180deg,_#050816_0%,_#02040a_100%)]" />
          <MonitoringPage onBack={() => navigate('/')} />
        </div>
      ) : (
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
            sessions={chat.sessions}
            activeSessionId={chat.sessionId}
            onSelectSession={chat.loadSession}
            onDeleteSession={chat.removeSession}
            onNewChat={handleNewChat}
            loadingSessions={chat.loadingSessions}
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
              <ChatWindow
                messages={chat.messages}
                sending={chat.sending}
                sessionId={chat.sessionId}
                selectedDocumentIds={documents.selectedDocumentIds}
                onSend={handleSend}
                onClearConversation={chat.clearConversation}
                onToggleSidebar={() => setSidebarOpen((v) => !v)}
                onOpenMonitoring={() => navigate('/monitoring')}
                onLogout={logout}
                sidebarOpen={sidebarOpen}
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
      )}
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
