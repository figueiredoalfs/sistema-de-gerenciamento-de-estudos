import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import ProtectedRoute from './components/layout/ProtectedRoute'
import Sidebar from './components/layout/Sidebar'
import Login from './pages/Login'
import Onboarding from './pages/Onboarding'
import Dashboard from './pages/Dashboard'
import AdminImportar from './pages/AdminImportar'
import AdminDashboard from './pages/AdminDashboard'
import AdminQuestoes from './pages/AdminQuestoes'
import AdminTopicos from './pages/AdminTopicos'
import AdminUsuarios from './pages/AdminUsuarios'
import AdminPlanoBase from './pages/AdminPlanoBase'
import AdminPendencias from './pages/AdminPendencias'
import AdminConfig from './pages/AdminConfig'
import AdminConvites from './pages/admin/AdminConvites'
import MentorAlunos from './pages/MentorAlunos'
import TaskView from './pages/TaskView'
import Desempenho from './pages/Desempenho'
import LancarBateria from './pages/LancarBateria'

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
  if (user.role === 'administrador') return <Navigate to="/" replace />
  if (user.role === 'mentor') return <Navigate to="/mentor/alunos" replace />
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
        path="/admin"
        element={
          <ProtectedRoute requireAdmin>
            <AppLayout>
              <AdminDashboard />
            </AppLayout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/admin/questoes"
        element={
          <ProtectedRoute requireAdmin>
            <AppLayout>
              <AdminQuestoes />
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
        path="/admin/topicos"
        element={
          <ProtectedRoute requireAdmin>
            <AppLayout>
              <AdminTopicos />
            </AppLayout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/admin/usuarios"
        element={
          <ProtectedRoute requireAdmin>
            <AppLayout>
              <AdminUsuarios />
            </AppLayout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/admin/planos-base"
        element={
          <ProtectedRoute requireAdmin>
            <AppLayout>
              <AdminPlanoBase />
            </AppLayout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/admin/pendencias"
        element={
          <ProtectedRoute requireAdmin>
            <AppLayout>
              <AdminPendencias />
            </AppLayout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/admin/config"
        element={
          <ProtectedRoute requireAdmin>
            <AppLayout>
              <AdminConfig />
            </AppLayout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/admin/convites"
        element={
          <ProtectedRoute requireAdmin>
            <AppLayout>
              <AdminConvites />
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
        path="/lancar-bateria"
        element={
          <ProtectedRoute>
            <AppLayout>
              <LancarBateria />
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

      <Route
        path="/mentor/alunos"
        element={
          <ProtectedRoute requireMentor>
            <AppLayout>
              <MentorAlunos />
            </AppLayout>
          </ProtectedRoute>
        }
      />

      {/* Redireciona qualquer rota desconhecida */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
