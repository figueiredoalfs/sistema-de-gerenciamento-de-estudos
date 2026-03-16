export default function SelectionCard({ label, description, icon, selected, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`
        w-full text-left border rounded-xl p-5 transition-all duration-300 cursor-pointer
        ${selected
          ? 'border-emerald-500 bg-emerald-500/10 shadow-emerald-500/10 shadow-md'
          : 'border-brand-border bg-brand-surface hover:border-emerald-500 hover:bg-emerald-500/5'
        }
      `}
    >
      <div className="flex items-start gap-3">
        {icon && <span className="text-2xl">{icon}</span>}
        <div>
          <p className={`font-semibold ${selected ? 'text-emerald-400' : 'text-brand-text'}`}>{label}</p>
          {description && <p className="text-brand-muted text-sm mt-0.5">{description}</p>}
        </div>
        {selected && (
          <div className="ml-auto flex-shrink-0 w-5 h-5 rounded-full bg-emerald-500 flex items-center justify-center">
            <svg viewBox="0 0 12 12" fill="none" className="w-3 h-3">
              <path d="M2 6l3 3 5-5" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
        )}
      </div>
    </button>
  )
}
