import { useState } from 'react'
import { gerarPdf } from '../../api/conteudo'

export default function PdfPanel({ taskCode }) {
  const [pdf, setPdf] = useState(null)
  const [loading, setLoading] = useState(false)
  const [erro, setErro] = useState(null)

  async function handleGerar() {
    setLoading(true)
    setErro(null)
    try {
      const res = await gerarPdf(taskCode)
      setPdf(res.conteudo_pdf)
    } catch {
      setErro('Erro ao gerar material. Verifique se a IA está configurada e tente novamente.')
    } finally {
      setLoading(false)
    }
  }

  if (pdf) return (
    <div className="space-y-3">
      <div className="bg-brand-card border border-brand-border rounded-xl p-5 max-h-[32rem] overflow-y-auto">
        <pre className="text-brand-text text-sm whitespace-pre-wrap font-sans leading-relaxed">{pdf}</pre>
      </div>
      <button
        onClick={handleGerar}
        disabled={loading}
        className="w-full py-2 text-xs text-brand-muted hover:text-brand-text border border-brand-border rounded-xl transition-all disabled:opacity-50"
      >
        {loading ? 'Gerando...' : '↺ Regenerar material'}
      </button>
    </div>
  )

  return (
    <div className="bg-brand-card border border-brand-border rounded-xl p-8 text-center space-y-4">
      {loading ? (
        <>
          <div className="w-10 h-10 rounded-full border-2 border-brand-border border-t-indigo-500 animate-spin mx-auto" />
          <p className="text-brand-muted text-sm">Gerando material com IA...</p>
          <p className="text-brand-muted text-xs">Pode levar até 30 segundos.</p>
        </>
      ) : (
        <>
          <div className="text-3xl">📄</div>
          <p className="text-brand-text font-medium text-sm">Material de estudo</p>
          <p className="text-brand-muted text-xs">
            A IA gera um resumo completo do conteúdo desta tarefa.
          </p>
          {erro && <p className="text-red-400 text-xs">{erro}</p>}
          <button
            onClick={handleGerar}
            className="px-5 py-2.5 bg-brand-gradient text-white text-sm font-semibold rounded-xl hover:opacity-90 transition-all"
          >
            Gerar material de estudo
          </button>
        </>
      )}
    </div>
  )
}
