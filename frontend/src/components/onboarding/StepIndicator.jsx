const STEPS = ['Área', 'Fase', 'Experiência', 'Funcionalidades']

export default function StepIndicator({ currentStep }) {
  return (
    <div className="flex items-center justify-center gap-0 mb-10">
      {STEPS.map((label, i) => {
        const index = i + 1
        const done = index < currentStep
        const active = index === currentStep
        return (
          <div key={label} className="flex items-center">
            <div className="flex flex-col items-center">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold transition-all duration-300 ${
                  done
                    ? 'bg-emerald-500 text-white'
                    : active
                    ? 'bg-brand-gradient text-white shadow-lg shadow-indigo-500/20'
                    : 'bg-brand-card border border-brand-border text-brand-muted'
                }`}
              >
                {done ? (
                  <svg viewBox="0 0 12 12" fill="none" className="w-3.5 h-3.5">
                    <path d="M2 6l3 3 5-5" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                ) : (
                  index
                )}
              </div>
              <span className={`text-xs mt-1 ${active ? 'text-brand-text' : 'text-brand-muted'}`}>{label}</span>
            </div>
            {i < STEPS.length - 1 && (
              <div className={`w-16 h-px mx-1 mb-5 transition-all duration-300 ${done ? 'bg-emerald-500' : 'bg-brand-border'}`} />
            )}
          </div>
        )
      })}
    </div>
  )
}
