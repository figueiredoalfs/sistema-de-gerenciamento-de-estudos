const FEATURES = [
  { value: 'geracao_conteudo', label: 'Geração de Conteúdo', icon: '🤖', description: 'PDFs e explicações geradas por IA para cada tópico.' },
  { value: 'analise_desempenho', label: 'Análise de Desempenho', icon: '📊', description: 'Acompanhe sua evolução por matéria e identifique pontos fracos.' },
  { value: 'cronograma_estudo', label: 'Cronograma de Estudos', icon: '📅', description: 'Planejamento semanal automático adaptado ao seu ritmo.' },
  { value: 'geracao_questoes', label: 'Questões Inteligentes', icon: '✏️', description: 'Questões geradas por IA baseadas nos tópicos do seu edital.' },
]

export default function StepFeatures({ selected, onChange }) {
  function toggle(value) {
    if (selected.includes(value)) {
      onChange(selected.filter((v) => v !== value))
    } else {
      onChange([...selected, value])
    }
  }

  return (
    <div>
      <h2 className="text-xl font-semibold text-brand-text mb-1">Quais recursos você quer usar?</h2>
      <p className="text-brand-muted text-sm mb-6">Selecione um ou mais. Você pode alterar depois.</p>
      <div className="grid grid-cols-1 gap-3">
        {FEATURES.map((f) => {
          const isSelected = selected.includes(f.value)
          return (
            <button
              key={f.value}
              type="button"
              onClick={() => toggle(f.value)}
              className={`w-full text-left border rounded-xl p-5 transition-all duration-300 ${
                isSelected
                  ? 'border-emerald-500 bg-emerald-500/10'
                  : 'border-brand-border bg-brand-surface hover:border-emerald-500 hover:bg-emerald-500/5'
              }`}
            >
              <div className="flex items-center gap-3">
                <span className="text-2xl">{f.icon}</span>
                <div className="flex-1">
                  <p className={`font-semibold ${isSelected ? 'text-emerald-400' : 'text-brand-text'}`}>{f.label}</p>
                  <p className="text-brand-muted text-sm mt-0.5">{f.description}</p>
                </div>
                <div className={`w-5 h-5 rounded border-2 flex-shrink-0 flex items-center justify-center transition-all duration-300 ${
                  isSelected ? 'border-emerald-500 bg-emerald-500' : 'border-brand-border'
                }`}>
                  {isSelected && (
                    <svg viewBox="0 0 12 12" fill="none" className="w-3 h-3">
                      <path d="M2 6l3 3 5-5" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  )}
                </div>
              </div>
            </button>
          )
        })}
      </div>
    </div>
  )
}
