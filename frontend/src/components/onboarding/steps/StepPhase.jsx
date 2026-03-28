import SelectionCard from '../SelectionCard'

export default function StepPhase({ value, onChange }) {
  return (
    <div>
      <h2 className="text-xl font-semibold text-brand-text mb-1">Em qual fase você está?</h2>
      <p className="text-brand-muted text-sm mb-6">Isso define como priorizamos os conteúdos para você.</p>
      <div className="grid grid-cols-1 gap-3">
        <SelectionCard
          label="Pré-edital"
          description="Ainda não saiu o edital. Quero me preparar com antecedência."
          icon="📚"
          selected={value === 'pre_edital'}
          onClick={() => onChange('pre_edital')}
        />
        <div className="w-full text-left border border-brand-border bg-brand-surface/40 rounded-xl p-5 opacity-50 cursor-not-allowed select-none">
          <div className="flex items-start gap-3">
            <span className="text-2xl">🎯</span>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <p className="font-semibold text-brand-muted">Pós-edital</p>
                <span className="text-xs px-1.5 py-0.5 rounded bg-brand-border text-brand-muted shrink-0">Em implementação</span>
              </div>
              <p className="text-brand-muted text-sm mt-0.5">O edital já saiu. Preciso focar nos tópicos cobrados.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
