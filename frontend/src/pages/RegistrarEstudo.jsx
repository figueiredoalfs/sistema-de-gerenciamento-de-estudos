import { useEffect, useState } from 'react'
import { getHierarquiaCompleta } from '../api/bateria'
import { postSessaoEstudo, listarSessoes, putSessaoEstudo } from '../api/sessoes'

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

const TIPO_LABEL = { teoria: 'Teoria / Leitura', revisão: 'Revisão' }

let _nextId = 1
function newSubRow() { return { id: _nextId++, subtopico: '' } }
function newGroup() { return { id: _nextId++, materia: '', modulo: '', subtopicos: [newSubRow()] } }

function ModalEditar({ sessao, onClose, onSaved }) {
  const [tipo, setTipo] = useState(sessao.tipo || 'teoria')
  const [data, setData] = useState(sessao.data || hoje())
  const [duracao, setDuracao] = useState(sessao.duracao_min != null ? String(sessao.duracao_min) : '')
  const [salvando, setSalvando] = useState(false)
  const [erro, setErro] = useState(null)

  async function handleSalvar(e) {
    e.preventDefault()
    setErro(null)
    setSalvando(true)
    try {
      const updated = await putSessaoEstudo(sessao.id, {
        tipo,
        data,
        duracao_min: duracao ? parseInt(duracao, 10) : null,
      })
      onSaved(updated)
    } catch (err) {
      setErro(err.response?.data?.detail || err.message || 'Erro ao salvar.')
    } finally {
      setSalvando(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div className="bg-brand-card border border-brand-border rounded-2xl p-6 w-full max-w-sm space-y-5 shadow-2xl">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-brand-text">Editar Sessão</h2>
          <button onClick={onClose} className="text-brand-muted hover:text-brand-text text-xl leading-none">×</button>
        </div>

        <form onSubmit={handleSalvar} className="space-y-4">
          <Campo label="Tipo de estudo">
            <select className={selectCls} value={tipo} onChange={e => setTipo(e.target.value)}>
              <option value="teoria">Teoria / Leitura</option>
              <option value="revisão">Revisão</option>
            </select>
          </Campo>

          <Campo label="Data">
            <input type="date" className={inputCls} value={data} onChange={e => setData(e.target.value)} max={hoje()} required />
          </Campo>

          <Campo label="Duração (minutos, opcional)">
            <input type="number" className={inputCls} placeholder="Ex: 45" value={duracao} onChange={e => setDuracao(e.target.value)} min="1" max="480" />
          </Campo>

          {erro && <p className="text-red-400 text-sm">{erro}</p>}

          <div className="flex gap-3 pt-1">
            <button type="button" onClick={onClose} className="flex-1 py-2.5 border border-brand-border rounded-xl text-brand-muted text-sm hover:text-brand-text transition-colors">
              Cancelar
            </button>
            <button type="submit" disabled={salvando} className="flex-1 py-2.5 bg-brand-gradient text-white rounded-xl font-semibold text-sm hover:opacity-90 transition-all disabled:opacity-50">
              {salvando ? 'Salvando...' : 'Salvar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default function RegistrarEstudo() {
  const [hierarquia, setHierarquia] = useState([])
  const [loadingHier, setLoadingHier] = useState(true)
  const [errHier, setErrHier] = useState(null)

  const [groups, setGroups] = useState([newGroup()])
  const [tipo, setTipo] = useState('teoria')
  const [data, setData] = useState(hoje())
  const [duracao, setDuracao] = useState('')

  const [enviando, setEnviando] = useState(false)
  const [sucesso, setSucesso] = useState(null)
  const [erro, setErro] = useState(null)

  const [historico, setHistorico] = useState([])
  const [editando, setEditando] = useState(null)

  useEffect(() => {
    getHierarquiaCompleta()
      .then(data => setHierarquia(Array.isArray(data) ? data : []))
      .catch(() => setErrHier('Não foi possível carregar as matérias.'))
      .finally(() => setLoadingHier(false))
    listarSessoes(20).then(s => setHistorico(Array.isArray(s) ? s : []))
  }, [])

  function updateGroup(gid, field, value) {
    setGroups(prev => prev.map(g => {
      if (g.id !== gid) return g
      const updated = { ...g, [field]: value }
      if (field === 'materia') { updated.modulo = ''; updated.subtopicos = [newSubRow()] }
      if (field === 'modulo') { updated.subtopicos = updated.subtopicos.map(s => ({ ...s, subtopico: '' })) }
      return updated
    }))
  }

  function updateSubRow(gid, sid, value) {
    setGroups(prev => prev.map(g => {
      if (g.id !== gid) return g
      return { ...g, subtopicos: g.subtopicos.map(s => s.id === sid ? { ...s, subtopico: value } : s) }
    }))
  }

  function addSubRow(gid) {
    setGroups(prev => prev.map(g => g.id === gid ? { ...g, subtopicos: [...g.subtopicos, newSubRow()] } : g))
  }

  function removeSubRow(gid, sid) {
    setGroups(prev => prev.map(g => {
      if (g.id !== gid) return g
      return { ...g, subtopicos: g.subtopicos.filter(s => s.id !== sid) }
    }))
  }

  function addGroup() { setGroups(prev => [...prev, newGroup()]) }
  function removeGroup(gid) { setGroups(prev => prev.filter(g => g.id !== gid)) }

  async function handleSalvar(e) {
    e.preventDefault()
    setErro(null)
    setSucesso(null)
    setEnviando(true)
    try {
      let count = 0
      for (const g of groups) {
        for (const s of g.subtopicos) {
          await postSessaoEstudo({
            subtopico_id: s.subtopico || g.modulo || null,
            tipo,
            data,
            duracao_min: duracao ? parseInt(duracao, 10) : null,
          })
          count++
        }
      }
      setSucesso(`${count} sessão(ões) registrada(s)!`)
      setGroups([newGroup()])
      setDuracao('')
      listarSessoes(20).then(s => setHistorico(Array.isArray(s) ? s : []))
    } catch (err) {
      setErro(err.response?.data?.detail || err.message || 'Erro ao registrar sessão.')
    } finally {
      setEnviando(false)
    }
  }

  function handleSaved(updated) {
    setHistorico(prev => prev.map(s => s.id === updated.id ? updated : s))
    setEditando(null)
  }

  return (
    <div className="max-w-lg mx-auto px-4 py-8 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-brand-text">Registrar Estudo</h1>
        <p className="text-brand-muted text-sm mt-1">Registre uma sessão de teoria ou revisão</p>
      </div>

      {errHier && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3 text-red-400 text-sm">{errHier}</div>
      )}

      <form onSubmit={handleSalvar} className="bg-brand-card border border-brand-border rounded-2xl p-6 space-y-5">
        <div className="space-y-3">
          {groups.map((group, gIdx) => {
            const materiaObj = hierarquia.find(m => m.id === group.materia) || null
            const modulos = materiaObj?.modulos || []
            const moduloObj = modulos.find(m => m.id === group.modulo) || null
            const subtopicosDisp = moduloObj?.subtopicos || []

            return (
              <div key={group.id} className="border border-brand-border rounded-xl p-4 space-y-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-semibold text-brand-muted uppercase tracking-wide">Matéria {gIdx + 1}</span>
                  {groups.length > 1 && (
                    <button type="button" onClick={() => removeGroup(group.id)} className="text-brand-muted hover:text-red-400 transition-colors text-sm px-1">×</button>
                  )}
                </div>

                <Campo label="Matéria">
                  <select className={selectCls} value={group.materia} onChange={e => updateGroup(group.id, 'materia', e.target.value)} disabled={loadingHier}>
                    <option value="">Selecione a matéria</option>
                    {hierarquia.map(m => <option key={m.id} value={m.id}>{m.nome}</option>)}
                  </select>
                </Campo>

                <Campo label="Módulo (opcional)">
                  <select className={selectCls} value={group.modulo} onChange={e => updateGroup(group.id, 'modulo', e.target.value)} disabled={!group.materia || modulos.length === 0}>
                    <option value="">Selecione o módulo</option>
                    {modulos.map(m => <option key={m.id} value={m.id}>{m.nome}</option>)}
                  </select>
                </Campo>

                <div className="space-y-2">
                  {group.subtopicos.map((sub, sIdx) => (
                    <div key={sub.id} className="bg-brand-surface rounded-lg p-3">
                      <div className="flex items-center gap-2">
                        <div className="flex-1">
                          <select
                            className={selectCls}
                            value={sub.subtopico}
                            onChange={e => updateSubRow(group.id, sub.id, e.target.value)}
                            disabled={!group.modulo || subtopicosDisp.length === 0}
                          >
                            <option value="">{sIdx === 0 ? 'Subtópico (opcional)' : `Subtópico ${sIdx + 1}`}</option>
                            {subtopicosDisp.map(s => <option key={s.id} value={s.id}>{s.nome}</option>)}
                          </select>
                        </div>
                        {group.subtopicos.length > 1 && (
                          <button type="button" onClick={() => removeSubRow(group.id, sub.id)} className="text-brand-muted hover:text-red-400 transition-colors text-sm px-1 flex-shrink-0">×</button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>

                <button
                  type="button"
                  onClick={() => addSubRow(group.id)}
                  disabled={!group.modulo}
                  className="w-full py-1.5 border border-dashed border-brand-border rounded-lg text-brand-muted text-xs hover:text-brand-text hover:border-indigo-400 transition-colors disabled:opacity-40"
                >
                  ＋ Subtópico
                </button>
              </div>
            )
          })}
        </div>

        <button
          type="button"
          onClick={addGroup}
          className="w-full py-2 border border-dashed border-brand-border rounded-xl text-brand-muted text-sm hover:text-brand-text hover:border-indigo-500 transition-colors"
        >
          ＋ Adicionar matéria
        </button>

        <Campo label="Tipo de estudo">
          <select className={selectCls} value={tipo} onChange={e => setTipo(e.target.value)}>
            <option value="teoria">Teoria / Leitura</option>
            <option value="revisão">Revisão</option>
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

      {historico.length > 0 && (
        <div className="bg-brand-card border border-brand-border rounded-2xl overflow-hidden">
          <div className="px-5 py-4 border-b border-brand-border">
            <h2 className="text-sm font-semibold text-brand-text">Histórico</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-brand-border text-xs text-brand-muted">
                  <th className="text-left px-5 py-3">Data</th>
                  <th className="text-left px-5 py-3">Tipo</th>
                  <th className="text-right px-5 py-3">Duração</th>
                  <th className="text-right px-5 py-3"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-brand-border">
                {historico.map(s => (
                  <tr key={s.id} className="hover:bg-brand-surface/40 transition-colors">
                    <td className="px-5 py-3 text-brand-muted">{new Date(s.data + 'T12:00:00').toLocaleDateString('pt-BR')}</td>
                    <td className="px-5 py-3 text-brand-text capitalize">{TIPO_LABEL[s.tipo] || s.tipo}</td>
                    <td className="px-5 py-3 text-right text-brand-muted">{s.duracao_min != null ? `${s.duracao_min} min` : '—'}</td>
                    <td className="px-5 py-3 text-right">
                      <button
                        onClick={() => setEditando(s)}
                        className="text-brand-muted hover:text-indigo-400 transition-colors text-base leading-none"
                        title="Editar"
                      >
                        ✏
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {editando && (
        <ModalEditar
          sessao={editando}
          onClose={() => setEditando(null)}
          onSaved={handleSaved}
        />
      )}
    </div>
  )
}
