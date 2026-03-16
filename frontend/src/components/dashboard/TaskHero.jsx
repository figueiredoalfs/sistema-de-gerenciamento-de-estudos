import { useNavigate } from 'react-router-dom'

const TIPO_CONFIG = {
  teoria:      { label: 'Teoria',      color: 'bg-blue-500/20 text-blue-400 border-blue-500/30' },
  revisao:     { label: 'Revisão',     color: 'bg-purple-500/20 text-purple-400 border-purple-500/30' },
  questionario:{ label: 'Questões',    color: 'bg-amber-500/20 text-amber-400 border-amber-500/30' },
  reforco:     { label: 'Reforço',     color: 'bg-red-500/20 text-red-400 border-red-500/30' },
  study:       { label: 'Estudo',      color: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' },
  questions:   { label: 'Questões',    color: 'bg-amber-500/20 text-amber-400 border-amber-500/30' },
  review:      { label: 'Revisão',     color: 'bg-purple-500/20 text-purple-400 border-purple-500/30' },
  diagnostico: { label: 'Diagnóstico', color: 'bg-indigo-500/20 text-indigo-400 border-indigo-500/30' },
  simulado:    { label: 'Simulado',    color: 'bg-pink-500/20 text-pink-400 border-pink-500/30' },
}

export default function TaskHero({ task, onStart, onComplete }) {
  const navigate = useNavigate()
  if (!task) return null

  const cfg = TIPO_CONFIG[task.tipo] ?? { label: task.tipo, color: 'bg-slate-500/20 text-slate-400 border-slate-500/30' }
  const isInProgress = task.status === 'in_progress'

  async function handleIniciar() {
    await onStart(task.id)
    navigate(`/tarefa/${task.id}`, { state: { task: { ...task, status: 'in_progress' } } })
  }

  function handleContinuar() {
    navigate(`/tarefa/${task.id}`, { state: { task } })
  }

  return (
    <div className="relative overflow-hidden rounded-2xl border border-indigo-500/20 bg-gradient-to-br from-indigo-950 to-emerald-950 p-6">
      {/* Glow de fundo */}
      <div className="absolute inset-0 bg-brand-gradient opacity-5 pointer-events-none" />

      <div className="relative z-10">
        <div className="flex items-start justify-between mb-4">
          <div>
            <p className="text-brand-muted text-xs uppercase tracking-wider mb-1">
              {isInProgress ? '⚡ Em andamento' : '▶ Próxima tarefa'}
            </p>
            <h2 className="text-xl font-bold text-brand-text leading-tight">
              {task.subject_nome ?? task.subject_id ?? 'Matéria'}
            </h2>
            {task.subtopic_nome && (
              <p className="text-brand-muted text-sm mt-0.5">{task.subtopic_nome}</p>
            )}
          </div>
          <span className={`text-xs font-medium px-3 py-1 rounded-full border ${cfg.color}`}>
            {cfg.label}
          </span>
        </div>

        <div className="flex gap-3 mt-6">
          {!isInProgress && (
            <button
              onClick={handleIniciar}
              className="flex-1 bg-brand-gradient text-white font-semibold rounded-xl py-2.5 text-sm transition-all duration-300 hover:opacity-90"
            >
              Iniciar tarefa
            </button>
          )}
          {isInProgress && (
            <>
              <button
                onClick={handleContinuar}
                className="flex-1 bg-brand-gradient text-white font-semibold rounded-xl py-2.5 text-sm transition-all duration-300 hover:opacity-90"
              >
                Continuar →
              </button>
              <button
                onClick={() => onComplete(task.id)}
                className="bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 font-semibold rounded-xl px-4 py-2.5 text-sm transition-all duration-300 hover:bg-emerald-500/30"
              >
                ✓
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
