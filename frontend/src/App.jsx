import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import ProtectedRoute from './components/layout/ProtectedRoute'
import Sidebar from './components/layout/Sidebar'
import Login from './pages/Login'
import Onboarding from './pages/Onboarding'
import Dashboard from './pages/Dashboard'
import AdminImportar from './pages/AdminImportar'
import TaskView from './pages/TaskView'
import Desempenho from './pages/Desempenho'

function AppLayout({ children }) {
  return (
    <div className="flex min-h-screen bg-brand-bg">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">{children}</main>
    </div>
  )
}

function OnboardingGuard({ children }) {
  const { user, loading } = useAuth()
  if (loading) return null
  if (!user) return <Navigate to="/login" replace />
  if (user.role === 'administrador' || user.role === 'mentor') return <Navigate to="/" replace />
  if (user.area) return <Navigate to="/" replace />
  return children
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />

      <Route
        path="/onboarding"
        element={
          <OnboardingGuard>
            <Onboarding />
          </OnboardingGuard>
        }
      />

      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AppLayout>
              <Dashboard />
            </AppLayout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/admin/importar"
        element={
          <ProtectedRoute requireAdmin>
            <AppLayout>
              <AdminImportar />
            </AppLayout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/desempenho"
        element={
          <ProtectedRoute>
            <AppLayout>
              <Desempenho />
            </AppLayout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/tarefa/:taskId"
        element={
          <ProtectedRoute>
            <AppLayout>
              <TaskView />
            </AppLayout>
          </ProtectedRoute>
        }
      />

      {/* Redireciona qualquer rota desconhecida */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
