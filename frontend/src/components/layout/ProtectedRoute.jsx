import { Navigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

export default function ProtectedRoute({ children, requireAdmin }) {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen bg-brand-bg flex items-center justify-center">
        <div className="w-8 h-8 rounded-full border-2 border-brand-border border-t-indigo-500 animate-spin" />
      </div>
    )
  }

  if (!user) return <Navigate to="/login" replace />
  if (requireAdmin && user.role !== 'administrador') return <Navigate to="/" replace />
  // Estudante sem área → forçar onboarding
  if (user.role === 'estudante' && !user.area) return <Navigate to="/onboarding" replace />

  return children
}
