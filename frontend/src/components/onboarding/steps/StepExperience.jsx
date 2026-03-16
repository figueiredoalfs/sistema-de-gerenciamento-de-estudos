import SelectionCard from '../SelectionCard'

const EXPERIENCE = [
  { value: 'iniciante', label: 'Iniciante', icon: '🌱', description: 'Estou começando agora, nunca estudei para concursos.' },
  { value: 'tempo_de_estudo', label: 'Tenho experiência', icon: '📈', description: 'Já estudo há algum tempo, quero otimizar.' },
]

const DURATIONS = [
  { value: '<1m', label: 'Menos de 1 mês' },
  { value: '1-3m', label: '1 a 3 meses' },
  { value: '3-6m', label: '3 a 6 meses' },
  { value: '>6m', label: 'Mais de 6 meses' },
]

export default function StepExperience({ experiencia, tempoEstudo, onChange }) {
  return (
    <div>
      <h2 className="text-xl font-semibold text-brand-text mb-1">Qual é o seu nível de experiência?</h2>
      <p className="text-brand-muted text-sm mb-6">Vamos calibrar o ritmo e os conteúdos para você.</p>
      <div className="grid grid-cols-1 gap-3 mb-6">
        {EXPERIENCE.map((exp) => (
          <SelectionCard
            key={exp.value}
            label={exp.label}
            description={exp.description}
            icon={exp.icon}
            selected={experiencia === exp.value}
            onClick={() => onChange('experiencia', exp.value)}
          />
        ))}
      </div>

      {experiencia === 'tempo_de_estudo' && (
        <div>
          <p className="text-brand-muted text-sm mb-3">Há quanto tempo você estuda?</p>
          <div className="grid grid-cols-2 gap-3">
            {DURATIONS.map((d) => (
              <button
                key={d.value}
                type="button"
                onClick={() => onChange('tempoEstudo', d.value)}
                className={`border rounded-xl py-3 px-4 text-sm font-medium transition-all duration-300 ${
                  tempoEstudo === d.value
                    ? 'border-emerald-500 bg-emerald-500/10 text-emerald-400'
                    : 'border-brand-border bg-brand-surface text-brand-muted hover:border-emerald-500'
                }`}
              >
                {d.label}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
