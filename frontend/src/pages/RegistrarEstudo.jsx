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

let _nextId = 1
function newRow() { return { id: _nextId++, materia: '', modulo: '', subtopico: '' } }

export default function RegistrarEstudo() {
  const [hierarquia, setHierarquia] = useState([])
  const [loadingHier, setLoadingHier] = useState(true)
  const [errHier, setErrHier] = useState(null)

  const [rows, setRows] = useState([newRow()])
  const [tipo, setTipo] = useState('teoria')
  const [data, setData] = useState(hoje())
  const [duracao, setDuracao] = useState('')

  const [enviando, setEnviando] = useState(false)
  const [sucesso, setSucesso] = useState(null)
  const [erro, setErro] = useState(null)

  useEffect(() => {
    getHierarquiaCompleta()
      .then(data => setHierarquia(Array.isArray(data) ? data : []))
      .catch(() => setErrHier('Não foi possível carregar as matérias.'))
      .finally(() => setLoadingHier(false))
  }, [])

  function updateRow(id, field, value) {
    setRows(prev => prev.map(r => {
      if (r.id !== id) return r
      const updated = { ...r, [field]: value }
      if (field === 'materia') { updated.modulo = ''; updated.subtopico = '' }
      if (field === 'modulo') { updated.subtopico = '' }
      return updated
    }))
  }

  function addRow() { setRows(prev => [...prev, newRow()]) }
  function removeRow(id) { setRows(prev => prev.filter(r => r.id !== id)) }

  async function handleSalvar(e) {
    e.preventDefault()
    setErro(null)
    setSucesso(null)
    setEnviando(true)
    try {
      for (const row of rows) {
        await postSessaoEstudo({
          subtopico_id: row.subtopico || row.modulo || null,
          tipo,
          data,
          duracao_min: duracao ? parseInt(duracao, 10) : null,
        })
      }
      setSucesso(`${rows.length} sessão(ões) registrada(s)!`)
      setRows([newRow()])
      setDuracao('')
    } catch (err) {
      setErro(err.response?.data?.detail || err.message || 'Erro ao registrar sessão.')
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
        <div className="space-y-3">
          {rows.map((row, idx) => {
            const materiaObj = hierarquia.find(m => m.id === row.materia) || null
            const modulos = materiaObj?.modulos || []
            const moduloObj = modulos.find(m => m.id === row.modulo) || null
            const subtopicos = moduloObj?.subtopicos || []

            return (
              <div key={row.id} className="border border-brand-border rounded-xl p-4 space-y-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-semibold text-brand-muted uppercase tracking-wide">Matéria {idx + 1}</span>
                  {rows.length > 1 && (
                    <button type="button" onClick={() => removeRow(row.id)} className="text-brand-muted hover:text-red-400 transition-colors text-sm px-1">×</button>
                  )}
                </div>

                <Campo label="Matéria">
                  <select className={selectCls} value={row.materia} onChange={e => updateRow(row.id, 'materia', e.target.value)} disabled={loadingHier}>
                    <option value="">Selecione a matéria</option>
                    {hierarquia.map(m => <option key={m.id} value={m.id}>{m.nome}</option>)}
                  </select>
                </Campo>

                <Campo label="Módulo (opcional)">
                  <select className={selectCls} value={row.modulo} onChange={e => updateRow(row.id, 'modulo', e.target.value)} disabled={!row.materia || modulos.length === 0}>
                    <option value="">Selecione o módulo</option>
                    {modulos.map(m => <option key={m.id} value={m.id}>{m.nome}</option>)}
                  </select>
                </Campo>

                <Campo label="Subtópico (opcional)">
                  <select className={selectCls} value={row.subtopico} onChange={e => updateRow(row.id, 'subtopico', e.target.value)} disabled={!row.modulo || subtopicos.length === 0}>
                    <option value="">Selecione o subtópico</option>
                    {subtopicos.map(s => <option key={s.id} value={s.id}>{s.nome}</option>)}
                  </select>
                </Campo>
              </div>
            )
          })}
        </div>

        <button
          type="button"
          onClick={addRow}
          className="w-full py-2 border border-dashed border-brand-border rounded-xl text-brand-muted text-sm hover:text-brand-text hover:border-indigo-500 transition-colors"
        >
          ＋ Adicionar matéria
        </button>

        <Campo label="Tipo de estudo">
          <select className={selectCls} value={tipo} onChange={e => setTipo(e.target.value)}>
            <option value="teoria">Teoria / Leitura</option>
            <option value="questoes">Resolução de questões</option>
          </select>
        </Campo>

        <Campo label="Data">
          <input
            type="date"
            className={inputCls}
            value={data}
            onChange={e => setData(e.target.value)}
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
            onChange={e => setDuracao(e.target.value)}
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
