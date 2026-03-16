import { useAuth } from '../context/AuthContext'
import { useTasks } from '../hooks/useTasks'
import WeeklyProgressBar from '../components/dashboard/WeeklyProgressBar'
import DiagnosticBanner from '../components/dashboard/DiagnosticBanner'
import TaskHero from '../components/dashboard/TaskHero'
import VerticalTimeline from '../components/dashboard/VerticalTimeline'

function Spinner() {
  return (
    <div className="flex items-center justify-center py-20">
      <div className="w-8 h-8 rounded-full border-2 border-brand-border border-t-indigo-500 animate-spin" />
    </div>
  )
}

function AdminHub() {
  const { user } = useAuth()
  return (
    <div className="max-w-2xl mx-auto px-4 py-8 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-brand-text">
          Olá, <span className="gradient-text">{user?.nome?.split(' ')[0]}</span>
        </h1>
        <p className="text-brand-muted text-sm mt-1">Painel de administração — use o menu lateral para navegar.</p>
      </div>
    </div>
  )
}

export default function Dashboard() {
  const { user } = useAuth()
  const { tasks, meta, loading, error, heroTask, iniciarTask, concluirTask, criarMeta } = useTasks()

  if (user?.role === 'administrador' || user?.role === 'mentor') return <AdminHub />

  if (loading) return <Spinner />

  const semMeta = !meta || meta.status === 'encerrada'

  return (
    <div className="max-w-2xl mx-auto px-4 py-8 space-y-6">
      {/* Saudação */}
      <div>
        <h1 className="text-2xl font-bold text-brand-text">
          Olá, <span className="gradient-text">{user?.nome?.split(' ')[0]}</span> 👋
        </h1>
        <p className="text-brand-muted text-sm mt-1">Veja o que você tem para hoje</p>
      </div>

      {/* Banner de diagnóstico */}
      {user?.diagnostico_pendente && <DiagnosticBanner />}

      {/* Progresso semanal */}
      {meta && <WeeklyProgressBar meta={meta} />}

      {/* Estado: sem meta */}
      {semMeta && (
        <div className="bg-brand-card border border-brand-border rounded-2xl p-8 text-center">
          <div className="w-14 h-14 rounded-2xl bg-brand-gradient/10 border border-indigo-500/20 flex items-center justify-center mx-auto mb-4">
            <svg className="w-7 h-7 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
          </div>
          <p className="text-brand-text font-semibold">Nenhuma meta ativa</p>
          <p className="text-brand-muted text-sm mt-1 mb-6">Gere sua meta semanal para começar a estudar.</p>
          <button
            onClick={criarMeta}
            className="px-6 py-2.5 bg-brand-gradient text-white rounded-xl font-semibold text-sm hover:opacity-90 transition-all duration-300"
          >
            Gerar meta semanal
          </button>
        </div>
      )}

      {/* Erro */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3 text-red-400 text-sm">
          {error}
        </div>
      )}

      {/* Task Hero */}
      {heroTask && (
        <TaskHero task={heroTask} onStart={iniciarTask} onComplete={concluirTask} />
      )}

      {/* Timeline */}
      {tasks.length > 0 && (
        <VerticalTimeline
          tasks={tasks}
          heroTask={heroTask}
          onStart={iniciarTask}
          onComplete={concluirTask}
        />
      )}

      {/* Todas concluídas */}
      {!semMeta && tasks.length > 0 && tasks.every((t) => t.status === 'completed') && (
        <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-2xl p-6 text-center">
          <p className="text-2xl mb-2">🎉</p>
          <p className="text-emerald-400 font-semibold">Todas as tarefas de hoje concluídas!</p>
          <p className="text-brand-muted text-sm mt-1">Volte amanhã para continuar sua jornada.</p>
        </div>
      )}
    </div>
  )
}
