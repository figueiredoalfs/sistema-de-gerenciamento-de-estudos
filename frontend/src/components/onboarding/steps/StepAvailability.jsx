const HORAS_OPTIONS = [
  { value: 1, label: '1 hora' },
  { value: 2, label: '2 horas' },
  { value: 3, label: '3 horas' },
  { value: 4, label: '4 horas' },
  { value: 5, label: '5 horas ou mais' },
]

const DIAS_OPTIONS = [
  { value: 3, label: '3 dias' },
  { value: 4, label: '4 dias' },
  { value: 5, label: '5 dias' },
  { value: 6, label: '6 dias' },
  { value: 7, label: 'Todos os dias' },
]

export default function StepAvailability({ horasPorDia, diasPorSemana, onChange }) {
  return (
    <div>
      <h2 className="text-xl font-semibold text-brand-text mb-1">Qual é a sua disponibilidade?</h2>
      <p className="text-brand-muted text-sm mb-6">
        Usamos isso para calcular quantas atividades gerar por semana.
      </p>

      <div className="mb-6">
        <p className="text-sm font-medium text-brand-muted mb-3">Horas de estudo por dia</p>
        <div className="grid grid-cols-3 gap-2 sm:grid-cols-5">
          {HORAS_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              type="button"
              onClick={() => onChange('horasPorDia', opt.value)}
              className={`border rounded-xl py-3 px-2 text-sm font-medium text-center transition-all duration-300 ${
                horasPorDia === opt.value
                  ? 'border-brand-primary bg-brand-primary/10 text-brand-primary'
                  : 'border-brand-border bg-brand-surface text-brand-muted hover:border-brand-primary'
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      <div>
        <p className="text-sm font-medium text-brand-muted mb-3">Dias por semana</p>
        <div className="grid grid-cols-3 gap-2 sm:grid-cols-5">
          {DIAS_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              type="button"
              onClick={() => onChange('diasPorSemana', opt.value)}
              className={`border rounded-xl py-3 px-2 text-sm font-medium text-center transition-all duration-300 ${
                diasPorSemana === opt.value
                  ? 'border-brand-primary bg-brand-primary/10 text-brand-primary'
                  : 'border-brand-border bg-brand-surface text-brand-muted hover:border-brand-primary'
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
