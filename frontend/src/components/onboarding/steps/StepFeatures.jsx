const FEATURES = [
  {
    value: 'cronograma_estudo',
    label: 'Cronograma de Estudos',
    icon: '📅',
    description: 'Sistema monta e gerencia meu plano de estudos automaticamente.',
  },
  {
    value: 'analise_desempenho',
    label: 'Análise de Desempenho',
    icon: '📊',
    description: 'Acompanhar meus acertos, erros e evolução por matéria.',
  },
  {
    value: 'geracao_conteudo',
    label: 'Geração de Conteúdo',
    icon: '🤖',
    description: 'PDFs e explicações geradas por IA para cada subtópico.',
  },
  {
    value: 'geracao_questoes',
    label: 'Banco de Questões',
    icon: '✏️',
    description: 'Praticar com questões de bancas reais e geradas por IA.',
  },
]

export default function StepFeatures({ selected, temPlanoExterno, onChange, onChangePlanoExterno }) {
  const temCronograma = selected.includes('cronograma_estudo')

  function toggle(value) {
    if (selected.includes(value)) {
      onChange(selected.filter((v) => v !== value))
    } else {
      onChange([...selected, value])
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-brand-text mb-1">Como você vai usar o Skolai?</h2>
        <p className="text-brand-muted text-sm mb-4">Selecione um ou mais. A interface se adapta à sua escolha.</p>
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

      {/* Pergunta adicional quando cronograma NÃO selecionado */}
      {!temCronograma && selected.length > 0 && (
        <div className="border border-brand-border rounded-xl p-5 bg-brand-surface/40">
          <p className="text-sm font-medium text-brand-text mb-3">
            Você já tem um plano de estudos?
          </p>
          <div className="flex gap-3">
            {[
              { value: true,  label: 'Sim', desc: 'Mentor, outra plataforma ou plano próprio' },
              { value: false, label: 'Não', desc: 'Só quero acompanhar meu desempenho' },
            ].map((op) => (
              <button
                key={String(op.value)}
                type="button"
                onClick={() => onChangePlanoExterno(op.value)}
                className={`flex-1 text-left border rounded-xl p-4 transition-all duration-300 ${
                  temPlanoExterno === op.value
                    ? 'border-indigo-500 bg-indigo-500/10'
                    : 'border-brand-border bg-brand-surface hover:border-indigo-400'
                }`}
              >
                <p className={`font-semibold text-sm ${temPlanoExterno === op.value ? 'text-indigo-400' : 'text-brand-text'}`}>{op.label}</p>
                <p className="text-brand-muted text-xs mt-0.5">{op.desc}</p>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
