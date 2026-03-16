import SelectionCard from '../SelectionCard'

const PHASES = [
  {
    value: 'pre_edital',
    label: 'Pré-edital',
    icon: '📚',
    description: 'Ainda não saiu o edital. Quero me preparar com antecedência.',
  },
  {
    value: 'pos_edital',
    label: 'Pós-edital',
    icon: '🎯',
    description: 'O edital já saiu. Preciso focar nos tópicos cobrados.',
  },
]

export default function StepPhase({ value, onChange }) {
  return (
    <div>
      <h2 className="text-xl font-semibold text-brand-text mb-1">Em qual fase você está?</h2>
      <p className="text-brand-muted text-sm mb-6">Isso define como priorizamos os conteúdos para você.</p>
      <div className="grid grid-cols-1 gap-3">
        {PHASES.map((phase) => (
          <SelectionCard
            key={phase.value}
            label={phase.label}
            description={phase.description}
            icon={phase.icon}
            selected={value === phase.value}
            onClick={() => onChange(phase.value)}
          />
        ))}
      </div>
    </div>
  )
}
