import SelectionCard from '../SelectionCard'

const AREAS = [
  { value: 'fiscal', label: 'Fiscal / Tributária', icon: '🏛️', description: 'Auditoria Fiscal, Receita Federal, SEFAZ...' },
  { value: 'juridica', label: 'Jurídica', icon: '⚖️', description: 'MP, Defensoria, Advocacia, Tribunais...' },
  { value: 'policial', label: 'Policial / Segurança', icon: '🛡️', description: 'Polícia Federal, Civil, Militar, PRF...' },
  { value: 'ti', label: 'Tecnologia da Informação', icon: '💻', description: 'Analista de TI, ANAC, BACEN, TCU...' },
  { value: 'saude', label: 'Saúde', icon: '🏥', description: 'ANVISA, ANS, concursos da área de saúde...' },
  { value: 'outro', label: 'Outro', icon: '📋', description: 'Outras áreas e concursos gerais' },
]

export default function StepArea({ value, onChange }) {
  return (
    <div>
      <h2 className="text-xl font-semibold text-brand-text mb-1">Qual é a sua área de concurso?</h2>
      <p className="text-brand-muted text-sm mb-6">Vamos personalizar seu conteúdo com base na sua área.</p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {AREAS.map((area) => (
          <SelectionCard
            key={area.value}
            label={area.label}
            description={area.description}
            icon={area.icon}
            selected={value === area.value}
            onClick={() => onChange(area.value)}
          />
        ))}
      </div>
    </div>
  )
}
