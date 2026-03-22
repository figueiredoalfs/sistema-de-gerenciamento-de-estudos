export default function WeeklyProgressBar({ meta }) {
  if (!meta) return null

  const total = meta.tasks_meta ?? 0
  const done = meta.tasks_concluidas ?? 0
  const pct = total > 0 ? Math.round((done / total) * 100) : 0

  return (
    <div className="bg-brand-card border border-brand-border rounded-2xl p-5">
      <div className="flex items-center justify-between mb-3">
        <div>
          <p className="text-brand-muted text-xs uppercase tracking-wider">
            {meta.numero_semana === 0 ? 'Diagnóstico' : 'Meta Semanal'}
          </p>
          <p className="text-brand-text font-semibold mt-0.5">
            {done} <span className="text-brand-muted font-normal">de</span> {total} tarefas
          </p>
        </div>
        <div className="text-right">
          <span className="text-2xl font-bold gradient-text">{pct}%</span>
        </div>
      </div>
      <div className="h-2.5 bg-brand-surface rounded-full overflow-hidden">
        <div
          className="h-full bg-brand-gradient rounded-full transition-all duration-500"
          style={{ width: `${pct}%` }}
        />
      </div>
      <p className="text-brand-muted text-xs mt-2">
        {meta.numero_semana === 0
          ? 'Diagnóstico inicial'
          : `Meta ${String(meta.numero_semana).padStart(2, '0')}`}
      </p>
    </div>
  )
}
