import { useEffect, useState } from 'react'
import { getConfigs, getModelosIA, upsertConfig } from '../api/adminConfig'

function Spinner() {
  return (
    <div className="flex items-center justify-center py-12">
      <div className="w-6 h-6 rounded-full border-2 border-brand-border border-t-indigo-500 animate-spin" />
    </div>
  )
}

export default function AdminConfig() {
  const [configs, setConfigs] = useState([])
  const [modelos, setModelos] = useState([])
  const [loading, setLoading] = useState(true)
  const [salvando, setSalvando] = useState(false)
  const [mensagem, setMensagem] = useState(null)

  // Estado local para edição
  const [modeloIA, setModeloIA] = useState('')

  useEffect(() => {
    Promise.allSettled([getConfigs(), getModelosIA()])
      .then(([cfgsResult, modsResult]) => {
        if (modsResult.status === 'fulfilled') {
          setModelos(modsResult.value)
        }
        if (cfgsResult.status === 'fulfilled') {
          const cfgs = cfgsResult.value
          setConfigs(cfgs)
          const cfg = cfgs.find(c => c.chave === 'modelo_ia')
          setModeloIA(cfg?.valor || 'gemini-1.5-flash')
        } else {
          setMensagem({ tipo: 'erro', texto: 'Erro ao carregar configurações do sistema.' })
        }
        if (modsResult.status === 'rejected') {
          setMensagem({ tipo: 'erro', texto: 'Erro ao carregar lista de modelos de IA.' })
        }
      })
      .finally(() => setLoading(false))
  }, [])

  async function handleSalvarModelo() {
    setSalvando(true)
    setMensagem(null)
    try {
      await upsertConfig('modelo_ia', modeloIA, 'Modelo de IA Gemini utilizado nas operações da plataforma')
      setMensagem({ tipo: 'ok', texto: 'Modelo de IA atualizado com sucesso.' })
    } catch {
      setMensagem({ tipo: 'erro', texto: 'Erro ao salvar. Tente novamente.' })
    } finally {
      setSalvando(false)
    }
  }

  if (loading) return <Spinner />

  const modeloAtual = modelos.find(m => m.value === modeloIA)

  return (
    <div className="p-6 max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-brand-text">Configurações do Sistema</h1>
        <p className="text-brand-muted text-sm mt-1">Ajuste parâmetros globais da plataforma Skolai.</p>
      </div>

      {mensagem && (
        <div className={`rounded-xl px-4 py-3 text-sm border ${
          mensagem.tipo === 'ok'
            ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
            : 'bg-red-500/10 border-red-500/20 text-red-400'
        }`}>
          {mensagem.texto}
        </div>
      )}

      {/* Card: Modelo de IA */}
      <div className="bg-brand-card border border-brand-border rounded-2xl p-6 space-y-4">
        <div>
          <h2 className="text-sm font-semibold text-brand-text">Modelo de IA</h2>
          <p className="text-xs text-brand-muted mt-0.5">
            Define qual modelo Gemini é utilizado em todas as operações de IA da plataforma
            (geração de conteúdo, planos, classificação de questões, etc).
          </p>
        </div>

        <div className="space-y-1.5">
          <label className="text-xs font-medium text-brand-muted uppercase tracking-wide">Modelo ativo</label>
          <select
            value={modeloIA}
            onChange={e => setModeloIA(e.target.value)}
            className="w-full bg-brand-surface border border-brand-border rounded-xl px-3 py-2.5 text-sm text-brand-text focus:outline-none focus:border-indigo-500 transition-colors"
          >
            {modelos.map(m => (
              <option key={m.value} value={m.value}>{m.label}</option>
            ))}
          </select>
        </div>

        {modeloAtual && (
          <div className="bg-brand-surface border border-brand-border rounded-xl px-4 py-3">
            <p className="text-xs text-brand-muted">
              <span className="font-semibold text-brand-text">Selecionado:</span> {modeloAtual.label}
            </p>
            {modeloIA.includes('2.5') && (
              <p className="text-xs text-amber-400 mt-1">
                ⚠️ Este modelo é mais caro — use apenas se a qualidade for insuficiente nos outros.
              </p>
            )}
          </div>
        )}

        <button
          onClick={handleSalvarModelo}
          disabled={salvando}
          className="px-5 py-2 bg-indigo-500 hover:bg-indigo-600 disabled:opacity-50 text-white text-sm font-medium rounded-xl transition-colors"
        >
          {salvando ? 'Salvando…' : 'Salvar modelo'}
        </button>
      </div>

      {/* Todas as configs (read-only view) */}
      {configs.length > 0 && (
        <div className="bg-brand-card border border-brand-border rounded-2xl overflow-hidden">
          <div className="px-5 py-4 border-b border-brand-border">
            <h2 className="text-sm font-semibold text-brand-text">Todas as configurações</h2>
          </div>
          <div className="divide-y divide-brand-border">
            {configs.map(c => (
              <div key={c.chave} className="px-5 py-3 flex items-center justify-between gap-4">
                <div>
                  <p className="text-xs font-mono text-indigo-400">{c.chave}</p>
                  {c.descricao && <p className="text-xs text-brand-muted mt-0.5">{c.descricao}</p>}
                </div>
                <span className="text-xs font-semibold text-brand-text shrink-0">{c.valor}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
