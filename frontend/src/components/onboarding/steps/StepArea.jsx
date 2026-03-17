import SelectionCard from '../SelectionCard'

const AREAS = [
  { value: 'fiscal', label: 'Fiscal / Tributária', icon: '🏛️', description: 'Auditoria Fiscal, Receita Federal, SEFAZ...', ativo: true },
  { value: 'juridica', label: 'Jurídica', icon: '⚖️', description: 'MP, Defensoria, Advocacia, Tribunais...', ativo: false },
  { value: 'policial', label: 'Policial / Segurança', icon: '🛡️', description: 'Polícia Federal, Civil, Militar, PRF...', ativo: false },
  { value: 'ti', label: 'Tecnologia da Informação', icon: '💻', description: 'Analista de TI, ANAC, BACEN, TCU...', ativo: false },
  { value: 'saude', label: 'Saúde', icon: '🏥', description: 'ANVISA, ANS, concursos da área de saúde...', ativo: false },
  { value: 'outro', label: 'Outro', icon: '📋', description: 'Outras áreas e concursos gerais', ativo: false },
]

export default function StepArea({ value, onChange }) {
  return (
    <div>
      <h2 className="text-xl font-semibold text-brand-text mb-1">Qual é a sua área de concurso?</h2>
      <p className="text-brand-muted text-sm mb-6">Vamos personalizar seu conteúdo com base na sua área.</p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {AREAS.map((area) =>
          area.ativo ? (
            <SelectionCard
              key={area.value}
              label={area.label}
              description={area.description}
              icon={area.icon}
              selected={value === area.value}
              onClick={() => onChange(area.value)}
            />
          ) : (
            <div
              key={area.value}
              className="w-full text-left border border-brand-border bg-brand-surface/40 rounded-xl p-5 opacity-50 cursor-not-allowed select-none"
            >
              <div className="flex items-start gap-3">
                <span className="text-2xl">{area.icon}</span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="font-semibold text-brand-muted">{area.label}</p>
                    <span className="text-xs px-1.5 py-0.5 rounded bg-brand-border text-brand-muted shrink-0">Em breve</span>
                  </div>
                  <p className="text-brand-muted text-sm mt-0.5">{area.description}</p>
                </div>
              </div>
            </div>
          )
        )}
      </div>
    </div>
  )
}
