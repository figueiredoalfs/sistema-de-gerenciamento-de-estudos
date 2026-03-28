const FEATURES = [
  {
    value: 'analise_desempenho',
    label: 'Análise de Desempenho',
    icon: '📊',
    description: 'Acompanhar meus acertos, erros e evolução por matéria.',
    ativo: true,
  },
  {
    value: 'cronograma_estudo',
    label: 'Cronograma de Estudos',
    icon: '📅',
    description: 'Sistema monta e gerencia meu plano de estudos automaticamente.',
    ativo: false,
  },
  {
    value: 'geracao_conteudo',
    label: 'Geração de Conteúdo',
    icon: '🤖',
    description: 'PDFs e explicações geradas por IA para cada subtópico.',
    ativo: false,
  },
  {
    value: 'geracao_questoes',
    label: 'Banco de Questões',
    icon: '✏️',
    description: 'Praticar com questões de bancas reais e geradas por IA.',
    ativo: false,
  },
]

export default function StepFeatures({ selected, temPlanoExterno, onChange, onChangePlanoExterno }) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-brand-text mb-1">Como você vai usar o Skolai?</h2>
        <p className="text-brand-muted text-sm mb-4">A Análise de Desempenho já está selecionada — é o núcleo do produto.</p>
        <div className="grid grid-cols-1 gap-3">
          {FEATURES.map((f) => {
            if (!f.ativo) {
              return (
                <div
                  key={f.value}
                  className="w-full text-left border border-brand-border bg-brand-surface/40 rounded-xl p-5 opacity-50 cursor-not-allowed select-none"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{f.icon}</span>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <p className="font-semibold text-brand-muted">{f.label}</p>
                        <span className="text-xs px-1.5 py-0.5 rounded bg-brand-border text-brand-muted shrink-0">Em implementação</span>
                      </div>
                      <p className="text-brand-muted text-sm mt-0.5">{f.description}</p>
                    </div>
                  </div>
                </div>
              )
            }

            const isSelected = selected.includes(f.value)
            return (
              <div
                key={f.value}
                className="w-full text-left border rounded-xl p-5 border-emerald-500 bg-emerald-500/10 cursor-default"
              >
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{f.icon}</span>
                  <div className="flex-1">
                    <p className="font-semibold text-emerald-400">{f.label}</p>
                    <p className="text-brand-muted text-sm mt-0.5">{f.description}</p>
                  </div>
                  <div className="w-5 h-5 rounded border-2 flex-shrink-0 flex items-center justify-center border-emerald-500 bg-emerald-500">
                    <svg viewBox="0 0 12 12" fill="none" className="w-3 h-3">
                      <path d="M2 6l3 3 5-5" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
