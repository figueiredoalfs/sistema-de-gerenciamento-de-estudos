import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getHierarquia, postBateria } from '../api/bateria'

const FONTES = [
  { value: 'qconcursos', label: 'QConcursos' },
  { value: 'tec', label: 'TEC Concursos' },
  { value: 'prova_anterior_mesma_banca', label: 'Prova anterior — mesma banca' },
  { value: 'prova_anterior_outra_banca', label: 'Prova anterior — outra banca' },
  { value: 'simulado', label: 'Simulado' },
  { value: 'manual', label: 'Manual' },
]

function Campo({ label, children }) {
  return (
    <div className="space-y-1.5">
      <label className="text-xs font-medium text-brand-muted uppercase tracking-wide">{label}</label>
      {children}
    </div>
  )
}

const selectCls =
  'w-full bg-brand-surface border border-brand-border rounded-xl px-3 py-2.5 text-sm text-brand-text focus:outline-none focus:border-indigo-500 transition-colors disabled:opacity-50'

const inputCls =
  'w-full bg-brand-surface border border-brand-border rounded-xl px-3 py-2.5 text-sm text-brand-text focus:outline-none focus:border-indigo-500 transition-colors'

export default function LancarBateria() {
  const [hierarquia, setHierarquia] = useState([])
  const [loadingHier, setLoadingHier] = useState(true)

  const [materia, setMateria] = useState('')
  const [subtopico, setSubtopico] = useState('')
  const [acertos, setAcertos] = useState('')
  const [total, setTotal] = useState('')
  const [fonte, setFonte] = useState('qconcursos')

  const [enviando, setEnviando] = useState(false)
  const [sucesso, setSucesso] = useState(null)
  const [erro, setErro] = useState(null)

  useEffect(() => {
    getHierarquia()
      .then(res => setHierarquia(Array.isArray(res) ? res : []))
      .catch(() => setErro('Erro ao carregar matérias. Verifique se o servidor está rodando.'))
      .finally(() => setLoadingHier(false))
  }, [])

  const subtopicos = hierarquia.find(m => m.nome === materia)?.subtopicos ?? []

  function handleMateriaChange(e) {
    setMateria(e.target.value)
    setSubtopico('')
  }

  function resetForm() {
    setMateria('')
    setSubtopico('')
    setAcertos('')
    setTotal('')
    setFonte('qconcursos')
    setSucesso(null)
    setErro(null)
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setErro(null)
    setSucesso(null)

    const ac = parseInt(acertos, 10)
    const tot = parseInt(total, 10)

    if (!materia) return setErro('Selecione a matéria.')
    if (isNaN(ac) || ac < 0) return setErro('Acertos inválido.')
    if (isNaN(tot) || tot <= 0) return setErro('Total deve ser maior que zero.')
    if (ac > tot) return setErro('Acertos não pode ser maior que o total.')

    setEnviando(true)
    try {
      const res = await postBateria(materia, subtopico || null, ac, tot, fonte)
      setSucesso(res.mensagem)
    } catch {
      setErro('Erro ao salvar. Tente novamente.')
    } finally {
      setEnviando(false)
    }
  }

  if (loadingHier) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-8 h-8 rounded-full border-2 border-brand-border border-t-indigo-500 animate-spin" />
      </div>
    )
  }

  return (
    <div className="max-w-lg mx-auto px-4 py-8 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-brand-text">Lançar bateria</h1>
        <p className="text-brand-muted text-sm mt-1">
          Registre questões feitas fora do sistema e veja o impacto no seu desempenho.
        </p>
      </div>

      {sucesso ? (
        <div className="bg-brand-card border border-brand-border rounded-2xl p-6 space-y-4">
          <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl px-4 py-3 text-emerald-400 text-sm">
            {sucesso}
          </div>
          <div className="flex gap-3">
            <button
              onClick={resetForm}
              className="flex-1 bg-indigo-500 hover:bg-indigo-600 text-white text-sm font-medium rounded-xl py-2.5 transition-colors"
            >
              Lançar outra
            </button>
            <Link
              to="/desempenho"
              className="flex-1 text-center bg-brand-surface border border-brand-border hover:border-indigo-500/40 text-brand-text text-sm font-medium rounded-xl py-2.5 transition-colors"
            >
              Ver desempenho
            </Link>
          </div>
        </div>
      ) : (
        <form
          onSubmit={handleSubmit}
          className="bg-brand-card border border-brand-border rounded-2xl p-6 space-y-5"
        >
          {erro && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3 text-red-400 text-sm">
              {erro}
            </div>
          )}

          <Campo label="Matéria">
            <select
              value={materia}
              onChange={handleMateriaChange}
              className={selectCls}
            >
              <option value="">Selecione a matéria</option>
              {hierarquia.map(m => (
                <option key={m.id} value={m.nome}>{m.nome}</option>
              ))}
            </select>
          </Campo>

          <Campo label="Subtópico (opcional)">
            <select
              value={subtopico}
              onChange={e => setSubtopico(e.target.value)}
              disabled={!materia || subtopicos.length === 0}
              className={selectCls}
            >
              <option value="">Todos / Geral</option>
              {subtopicos.map(s => (
                <option key={s.id} value={s.nome}>{s.nome}</option>
              ))}
            </select>
          </Campo>

          <div className="grid grid-cols-2 gap-4">
            <Campo label="Acertos">
              <input
                type="number"
                min="0"
                value={acertos}
                onChange={e => setAcertos(e.target.value)}
                placeholder="Ex: 7"
                className={inputCls}
              />
            </Campo>
            <Campo label="Total de questões">
              <input
                type="number"
                min="1"
                value={total}
                onChange={e => setTotal(e.target.value)}
                placeholder="Ex: 10"
                className={inputCls}
              />
            </Campo>
          </div>

          <Campo label="Fonte">
            <select value={fonte} onChange={e => setFonte(e.target.value)} className={selectCls}>
              {FONTES.map(f => (
                <option key={f.value} value={f.value}>{f.label}</option>
              ))}
            </select>
          </Campo>

          {acertos !== '' && total !== '' && parseInt(total, 10) > 0 && (
            <p className="text-xs text-brand-muted text-right">
              Aproveitamento:{' '}
              <span className="font-semibold text-brand-text">
                {((parseInt(acertos, 10) / parseInt(total, 10)) * 100).toFixed(1)}%
              </span>
            </p>
          )}

          <button
            type="submit"
            disabled={enviando}
            className="w-full bg-indigo-500 hover:bg-indigo-600 disabled:opacity-50 text-white text-sm font-medium rounded-xl py-2.5 transition-colors"
          >
            {enviando ? 'Salvando…' : 'Salvar bateria'}
          </button>
        </form>
      )}
    </div>
  )
}
