export default function DiagnosticBanner() {
  return (
    <div className="bg-indigo-500/10 border border-indigo-500/40 rounded-2xl p-5">
      <div className="flex items-start gap-4">
        <div className="w-10 h-10 rounded-xl bg-indigo-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
          <svg className="w-5 h-5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
        </div>
        <div>
          <p className="text-indigo-300 font-semibold text-sm">Diagnóstico inicial pendente</p>
          <p className="text-indigo-400/70 text-xs mt-1 leading-relaxed">
            Conclua as tarefas abaixo para calibrar seu plano de estudos. Sua próxima meta semanal será gerada automaticamente após o diagnóstico.
          </p>
        </div>
      </div>
    </div>
  )
}
