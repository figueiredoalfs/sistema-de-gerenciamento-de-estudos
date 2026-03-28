import { useEffect, useState } from 'react'
import { getHierarquiaCompleta } from '../api/bateria'
import { postSessaoEstudo } from '../api/sessoes'

const inputCls = 'w-full bg-brand-surface border border-brand-border rounded-xl px-3 py-2.5 text-sm text-brand-text focus:outline-none focus:border-indigo-500 transition-colors disabled:opacity-50'
const selectCls = inputCls

function Campo({ label, children }) {
  return (
    <div className="space-y-1.5">
      <label className="text-xs font-medium text-brand-muted uppercase tracking-wide">{label}</label>
      {children}
    </div>
  )
}

function hoje() {
  return new Date().toISOString().split('T')[0]
}

export default function RegistrarEstudo() {
  const [hierarquia, setHierarquia] = useState([])
  const [loadingHier, setLoadingHier] = useState(true)
  const [errHier, setErrHier] = useState(null)

  const [materia, setMateria] = useState('')
  const [modulo, setModulo] = useState('')
  const [subtopico, setSubtopico] = useState('')
  const [tipo, setTipo] = useState('teoria')
  const [data, setData] = useState(hoje())
  const [duracao, setDuracao] = useState('')

  const [enviando, setEnviando] = useState(false)
  const [sucesso, setSucesso] = useState(null)
  const [erro, setErro] = useState(null)

  useEffect(() => {
    getHierarquiaCompleta()
      .then(setHierarquia)
      .catch(() => setErrHier('Não foi possível carregar as matérias.'))
      .finally(() => setLoadingHier(false))
  }, [])

  const materiaObj = hierarquia.find((m) => m.id === materia) || null
  const modulos = materiaObj?.modulos || []
  const moduloObj = modulos.find((m) => m.id === modulo) || null
  const subtopicos = moduloObj?.subtopicos || []

  async function handleSalvar(e) {
    e.preventDefault()
    setErro(null)
    setSucesso(null)
    setEnviando(true)
    try {
      await postSessaoEstudo({
        subtopico_id: subtopico || modulo || null,
        tipo,
        data,
        duracao_min: duracao ? parseInt(duracao, 10) : null,
      })
      setSucesso(`Sessão de ${tipo === 'teoria' ? 'teoria' : 'questões'} registrada!`)
      setSubtopico('')
      setModulo('')
      setDuracao('')
    } catch {
      setErro('Erro ao registrar sessão. Tente novamente.')
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="max-w-lg mx-auto px-4 py-8 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-brand-text">Registrar Estudo</h1>
        <p className="text-brand-muted text-sm mt-1">Registre uma sessão de teoria ou prática</p>
      </div>

      {errHier && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3 text-red-400 text-sm">{errHier}</div>
      )}

      <form onSubmit={handleSalvar} className="bg-brand-card border border-brand-border rounded-2xl p-6 space-y-5">
        <Campo label="Matéria">
          <select className={selectCls} value={materia} onChange={(e) => { setMateria(e.target.value); setModulo(''); setSubtopico('') }} disabled={loadingHier}>
            <option value="">Selecione a matéria</option>
            {hierarquia.map((m) => <option key={m.id} value={m.id}>{m.nome}</option>)}
          </select>
        </Campo>

        <Campo label="Módulo (opcional)">
          <select className={selectCls} value={modulo} onChange={(e) => { setModulo(e.target.value); setSubtopico('') }} disabled={!materia || modulos.length === 0}>
            <option value="">Selecione o módulo</option>
            {modulos.map((m) => <option key={m.id} value={m.id}>{m.nome}</option>)}
          </select>
        </Campo>

        <Campo label="Subtópico (opcional)">
          <select className={selectCls} value={subtopico} onChange={(e) => setSubtopico(e.target.value)} disabled={!modulo || subtopicos.length === 0}>
            <option value="">Selecione o subtópico</option>
            {subtopicos.map((s) => <option key={s.id} value={s.id}>{s.nome}</option>)}
          </select>
        </Campo>

        <Campo label="Tipo de estudo">
          <select className={selectCls} value={tipo} onChange={(e) => setTipo(e.target.value)}>
            <option value="teoria">Teoria / Leitura</option>
            <option value="questoes">Resolução de questões</option>
          </select>
        </Campo>

        <Campo label="Data">
          <input
            type="date"
            className={inputCls}
            value={data}
            onChange={(e) => setData(e.target.value)}
            max={hoje()}
            required
          />
        </Campo>

        <Campo label="Duração (minutos, opcional)">
          <input
            type="number"
            className={inputCls}
            placeholder="Ex: 45"
            value={duracao}
            onChange={(e) => setDuracao(e.target.value)}
            min="1"
            max="480"
          />
        </Campo>

        {sucesso && (
          <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl px-4 py-3 text-emerald-400 text-sm">
            {sucesso}
          </div>
        )}
        {erro && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3 text-red-400 text-sm">{erro}</div>
        )}

        <button
          type="submit"
          disabled={enviando || !data}
          className="w-full py-3 bg-brand-gradient text-white rounded-xl font-semibold text-sm hover:opacity-90 transition-all duration-300 disabled:opacity-50"
        >
          {enviando ? 'Salvando...' : 'Registrar sessão'}
        </button>
      </form>
    </div>
  )
}
