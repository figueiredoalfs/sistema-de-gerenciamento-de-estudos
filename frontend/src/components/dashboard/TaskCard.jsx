const TIPO_CONFIG = {
  teoria:       { label: 'Teoria',      color: 'bg-blue-500/20 text-blue-400' },
  revisao:      { label: 'Revisão',     color: 'bg-purple-500/20 text-purple-400' },
  questionario: { label: 'Questões',    color: 'bg-amber-500/20 text-amber-400' },
  reforco:      { label: 'Reforço',     color: 'bg-red-500/20 text-red-400' },
  study:        { label: 'Estudo',      color: 'bg-emerald-500/20 text-emerald-400' },
  questions:    { label: 'Questões',    color: 'bg-amber-500/20 text-amber-400' },
  review:       { label: 'Revisão',     color: 'bg-purple-500/20 text-purple-400' },
  diagnostico:  { label: 'Diagnóstico', color: 'bg-indigo-500/20 text-indigo-400' },
  simulado:     { label: 'Simulado',    color: 'bg-pink-500/20 text-pink-400' },
}

const STATUS_ICON = {
  pending:     { icon: '○', color: 'text-brand-muted' },
  in_progress: { icon: '◉', color: 'text-indigo-400' },
  completed:   { icon: '●', color: 'text-emerald-400' },
}

export default function TaskCard({ task, onStart, onComplete, isHero }) {
  if (isHero) return null // Hero já exibida separadamente

  const cfg = TIPO_CONFIG[task.tipo] ?? { label: task.tipo, color: 'bg-slate-500/20 text-slate-400' }
  const status = STATUS_ICON[task.status] ?? STATUS_ICON.pending
  const done = task.status === 'completed'

  return (
    <div className={`flex gap-4 transition-all duration-300 ${done ? 'opacity-50' : ''}`}>
      {/* Conector da timeline */}
      <div className="flex flex-col items-center">
        <span className={`text-lg font-bold ${status.color} transition-all duration-300`}>{status.icon}</span>
        <div className="w-px flex-1 bg-brand-border mt-1" />
      </div>

      {/* Card */}
      <div className="flex-1 bg-brand-card border border-brand-border rounded-xl p-4 mb-4 hover:border-slate-600 transition-all duration-300">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <p className="text-brand-text font-medium text-sm">
              {task.subject_nome ?? task.subject_id ?? 'Matéria'}
            </p>
            {task.subtopic_nome && (
              <p className="text-brand-muted text-xs mt-0.5">{task.subtopic_nome}</p>
            )}
          </div>
          <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${cfg.color} ml-3 flex-shrink-0`}>
            {cfg.label}
          </span>
        </div>

        {!done && (
          <div className="flex gap-2 mt-3">
            {task.status === 'pending' && (
              <button
                onClick={() => onStart(task.id)}
                className="text-xs px-3 py-1.5 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 hover:bg-indigo-500/20 transition-all duration-300"
              >
                Iniciar
              </button>
            )}
            {task.status === 'in_progress' && (
              <button
                onClick={() => onComplete(task.id)}
                className="text-xs px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 hover:bg-emerald-500/20 transition-all duration-300"
              >
                Concluir
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
