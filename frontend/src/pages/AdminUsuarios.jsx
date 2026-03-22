import { useEffect, useMemo, useState } from 'react'
import { listarUsuarios, atualizarUsuario, atribuirMentor, progressoUsuario, criarUsuario, resetSenhaUsuario } from '../api/adminUsuarios'

const ROLE_LABEL = {
  administrador: { label: 'Admin', cls: 'bg-purple-500/20 text-purple-300 border-purple-500/30' },
  mentor: { label: 'Mentor', cls: 'bg-blue-500/20 text-blue-300 border-blue-500/30' },
  estudante: { label: 'Aluno', cls: 'bg-brand-surface text-brand-muted border-brand-border' },
}

function RoleBadge({ role }) {
  const { label, cls } = ROLE_LABEL[role] ?? { label: role, cls: 'bg-brand-surface text-brand-muted border-brand-border' }
  return (
    <span className={`text-xs font-medium px-2 py-0.5 rounded border ${cls}`}>{label}</span>
  )
}

const AREAS_OPCOES = ['fiscal', 'eaof_com', 'eaof_svm', 'cfoe_com', 'juridica', 'policial', 'ti', 'saude', 'outro']
const ROLES_OPCOES = ['estudante', 'mentor', 'administrador']
const NIVEIS_DESAFIO = ['conservador', 'moderado', 'agressivo']

function ModalEditarUsuario({ usuario, onClose, onSalvo }) {
  const [form, setForm] = useState({
    nome: usuario.nome,
    email: usuario.email,
    area: usuario.area ?? '',
    role: usuario.role,
    horas_por_dia: String(usuario.horas_por_dia ?? 3),
    dias_por_semana: String(usuario.dias_por_semana ?? 5),
    nivel_desafio: usuario.nivel_desafio ?? 'moderado',
    ativo: usuario.ativo,
  })
  const [loading, setLoading] = useState(false)
  const [erro, setErro] = useState('')

  function set(field, value) { setForm((f) => ({ ...f, [field]: value })) }

  async function salvar(e) {
    e.preventDefault()
    setErro('')
    setLoading(true)
    try {
      const body = {
        nome: form.nome.trim(),
        email: form.email.trim(),
        area: form.area || null,
        role: form.role,
        horas_por_dia: parseFloat(form.horas_por_dia) || 3,
        dias_por_semana: parseFloat(form.dias_por_semana) || 5,
        nivel_desafio: form.nivel_desafio,
        ativo: form.ativo,
      }
      const atualizado = await atualizarUsuario(usuario.id, body)
      onSalvo(atualizado)
      onClose()
    } catch (err) {
      setErro(err.response?.data?.detail || 'Erro ao salvar.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div className="bg-brand-card border border-brand-border rounded-xl p-6 w-full max-w-lg space-y-4 shadow-xl max-h-[90vh] overflow-y-auto">
        <h2 className="text-lg font-semibold text-brand-text">Editar usuário</h2>
        <form onSubmit={salvar} className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div className="col-span-2">
              <label className="text-xs text-brand-muted block mb-1">Nome</label>
              <input required value={form.nome} onChange={(e) => set('nome', e.target.value)}
                className="w-full bg-brand-surface border border-brand-border rounded-lg px-3 py-2 text-brand-text text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500" />
            </div>
            <div className="col-span-2">
              <label className="text-xs text-brand-muted block mb-1">E-mail</label>
              <input required type="email" value={form.email} onChange={(e) => set('email', e.target.value)}
                className="w-full bg-brand-surface border border-brand-border rounded-lg px-3 py-2 text-brand-text text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500" />
            </div>
            <div>
              <label className="text-xs text-brand-muted block mb-1">Área</label>
              <select value={form.area} onChange={(e) => set('area', e.target.value)}
                className="w-full bg-brand-surface border border-brand-border rounded-lg px-3 py-2 text-brand-text text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500">
                <option value="">— Sem área —</option>
                {AREAS_OPCOES.map((a) => <option key={a} value={a}>{a}</option>)}
              </select>
            </div>
            <div>
              <label className="text-xs text-brand-muted block mb-1">Perfil</label>
              <select value={form.role} onChange={(e) => set('role', e.target.value)}
                className="w-full bg-brand-surface border border-brand-border rounded-lg px-3 py-2 text-brand-text text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500">
                {ROLES_OPCOES.map((r) => <option key={r} value={r}>{r}</option>)}
              </select>
            </div>
            <div>
              <label className="text-xs text-brand-muted block mb-1">Horas/dia</label>
              <input type="number" step="0.5" min="0.5" max="24" value={form.horas_por_dia} onChange={(e) => set('horas_por_dia', e.target.value)}
                className="w-full bg-brand-surface border border-brand-border rounded-lg px-3 py-2 text-brand-text text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500" />
            </div>
            <div>
              <label className="text-xs text-brand-muted block mb-1">Dias/semana</label>
              <input type="number" step="1" min="1" max="7" value={form.dias_por_semana} onChange={(e) => set('dias_por_semana', e.target.value)}
                className="w-full bg-brand-surface border border-brand-border rounded-lg px-3 py-2 text-brand-text text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500" />
            </div>
            <div>
              <label className="text-xs text-brand-muted block mb-1">Nível de desafio</label>
              <select value={form.nivel_desafio} onChange={(e) => set('nivel_desafio', e.target.value)}
                className="w-full bg-brand-surface border border-brand-border rounded-lg px-3 py-2 text-brand-text text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500">
                {NIVEIS_DESAFIO.map((n) => <option key={n} value={n}>{n}</option>)}
              </select>
            </div>
            <div className="flex items-center gap-2 pt-4">
              <button type="button" onClick={() => set('ativo', !form.ativo)}
                className={`w-9 h-5 rounded-full transition-colors relative flex-shrink-0 ${form.ativo ? 'bg-indigo-500' : 'bg-brand-border'}`}>
                <span className={`absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform ${form.ativo ? 'translate-x-4' : 'translate-x-0.5'}`} />
              </button>
              <span className="text-sm text-brand-muted">{form.ativo ? 'Ativo' : 'Inativo'}</span>
            </div>
          </div>
          {erro && <p className="text-red-400 text-sm">{erro}</p>}
          <div className="flex gap-2 justify-end pt-2">
            <button type="button" onClick={onClose}
              className="px-4 py-2 text-sm text-brand-muted hover:text-brand-text border border-brand-border rounded-lg transition-colors">
              Cancelar
            </button>
            <button type="submit" disabled={loading}
              className="px-4 py-2 text-sm bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors disabled:opacity-50">
              {loading ? 'Salvando...' : 'Salvar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

function ModalResetSenha({ usuario, onClose }) {
  const [senha, setSenha] = useState(null)
  const [loading, setLoading] = useState(false)
  const [erro, setErro] = useState('')

  async function confirmar() {
    setLoading(true)
    setErro('')
    try {
      const res = await resetSenhaUsuario(usuario.id)
      setSenha(res.senha_temporaria)
    } catch (err) {
      setErro(err.response?.data?.detail || 'Erro ao redefinir senha.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-brand-card border border-brand-border rounded-xl p-6 w-full max-w-sm space-y-4 shadow-xl">
        <h2 className="text-lg font-semibold text-brand-text">Redefinir senha</h2>
        <p className="text-brand-muted text-sm">{usuario.nome} — {usuario.email}</p>

        {!senha ? (
          <>
            <p className="text-sm text-brand-muted">Isso irá gerar uma senha temporária para o usuário. Ele deve trocá-la no primeiro acesso.</p>
            {erro && <p className="text-red-400 text-sm">{erro}</p>}
            <div className="flex gap-2 justify-end pt-2">
              <button onClick={onClose}
                className="px-4 py-2 text-sm text-brand-muted hover:text-brand-text border border-brand-border rounded-lg transition-colors">
                Cancelar
              </button>
              <button onClick={confirmar} disabled={loading}
                className="px-4 py-2 text-sm bg-yellow-600 hover:bg-yellow-500 text-white rounded-lg transition-colors disabled:opacity-50">
                {loading ? 'Gerando...' : 'Gerar senha'}
              </button>
            </div>
          </>
        ) : (
          <>
            <div className="bg-brand-surface border border-brand-border rounded-lg px-4 py-3 text-center">
              <p className="text-xs text-brand-muted mb-1">Senha temporária</p>
              <p className="text-2xl font-mono font-bold text-indigo-400 tracking-widest">{senha}</p>
            </div>
            <p className="text-xs text-brand-muted">Copie e envie ao usuário. Esta senha não será exibida novamente.</p>
            <div className="flex justify-end">
              <button onClick={onClose}
                className="px-4 py-2 text-sm bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors">
                Fechar
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

function ModalCriarUsuario({ onClose, onCriado }) {
  const [form, setForm] = useState({ nome: '', email: '', password: '', role: 'estudante' })
  const [loading, setLoading] = useState(false)
  const [erro, setErro] = useState('')

  function set(field, value) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  async function salvar(e) {
    e.preventDefault()
    setErro('')
    setLoading(true)
    try {
      const novo = await criarUsuario(form)
      onCriado(novo)
      onClose()
    } catch (err) {
      setErro(err.response?.data?.detail || 'Erro ao criar usuário.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-brand-card border border-brand-border rounded-xl p-6 w-full max-w-md space-y-4 shadow-xl">
        <h2 className="text-lg font-semibold text-brand-text">Criar usuário</h2>

        <form onSubmit={salvar} className="space-y-3">
          <div>
            <label className="text-xs text-brand-muted block mb-1">Nome</label>
            <input
              required
              value={form.nome}
              onChange={(e) => set('nome', e.target.value)}
              className="w-full bg-brand-surface border border-brand-border rounded-lg px-3 py-2 text-brand-text text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="text-xs text-brand-muted block mb-1">E-mail</label>
            <input
              required
              type="email"
              value={form.email}
              onChange={(e) => set('email', e.target.value)}
              className="w-full bg-brand-surface border border-brand-border rounded-lg px-3 py-2 text-brand-text text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="text-xs text-brand-muted block mb-1">Senha</label>
            <input
              required
              type="password"
              value={form.password}
              onChange={(e) => set('password', e.target.value)}
              className="w-full bg-brand-surface border border-brand-border rounded-lg px-3 py-2 text-brand-text text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="text-xs text-brand-muted block mb-1">Perfil</label>
            <select
              value={form.role}
              onChange={(e) => set('role', e.target.value)}
              className="w-full bg-brand-surface border border-brand-border rounded-lg px-3 py-2 text-brand-text text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              <option value="estudante">Aluno</option>
              <option value="mentor">Mentor</option>
              <option value="administrador">Admin</option>
            </select>
          </div>

          {erro && <p className="text-red-400 text-sm">{erro}</p>}

          <div className="flex gap-2 justify-end pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm text-brand-muted hover:text-brand-text border border-brand-border rounded-lg transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 text-sm bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors disabled:opacity-50"
            >
              {loading ? 'Criando...' : 'Criar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

function ModalMentor({ usuario, mentores, onClose, onSave }) {
  const [mentorId, setMentorId] = useState(usuario.mentor_id ?? '')
  const [loading, setLoading] = useState(false)

  async function salvar() {
    setLoading(true)
    try {
      await onSave(usuario.id, mentorId || null)
      onClose()
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-brand-card border border-brand-border rounded-xl p-6 w-full max-w-md space-y-4 shadow-xl">
        <h2 className="text-lg font-semibold text-brand-text">Atribuir mentor</h2>
        <p className="text-brand-muted text-sm">{usuario.nome} — {usuario.email}</p>

        <div className="space-y-1">
          <label className="text-xs text-brand-muted">Mentor</label>
          <select
            value={mentorId}
            onChange={(e) => setMentorId(e.target.value)}
            className="w-full bg-brand-surface border border-brand-border rounded-lg px-3 py-2 text-brand-text text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            <option value="">— Sem mentor —</option>
            {mentores.map((m) => (
              <option key={m.id} value={m.id}>{m.nome}</option>
            ))}
          </select>
        </div>

        <div className="flex gap-2 justify-end pt-2">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm text-brand-muted hover:text-brand-text border border-brand-border rounded-lg transition-colors"
          >
            Cancelar
          </button>
          <button
            onClick={salvar}
            disabled={loading}
            className="px-4 py-2 text-sm bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors disabled:opacity-50"
          >
            {loading ? 'Salvando...' : 'Salvar'}
          </button>
        </div>
      </div>
    </div>
  )
}

function ModalProgresso({ usuario, onClose }) {
  const [dados, setDados] = useState(null)
  const [loading, setLoading] = useState(true)
  const [erro, setErro] = useState('')

  useEffect(() => {
    progressoUsuario(usuario.id)
      .then(setDados)
      .catch(() => setErro('Erro ao carregar progresso.'))
      .finally(() => setLoading(false))
  }, [usuario.id])

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-brand-card border border-brand-border rounded-xl p-6 w-full max-w-2xl mx-4 space-y-4 shadow-xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-brand-text">Progresso</h2>
            <p className="text-brand-muted text-sm">{usuario.nome} — {usuario.email}</p>
          </div>
          <button onClick={onClose} className="text-brand-muted hover:text-brand-text">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {loading && <p className="text-brand-muted text-sm">Carregando…</p>}
        {erro && <p className="text-red-400 text-sm">{erro}</p>}

        {dados && (
          <>
            <div className="grid grid-cols-3 gap-3">
              <div className="bg-brand-surface border border-brand-border rounded-lg px-4 py-3 text-center">
                <p className="text-2xl font-bold text-brand-text">{dados.total_questoes}</p>
                <p className="text-xs text-brand-muted mt-0.5">questões respondidas</p>
              </div>
              <div className="bg-brand-surface border border-brand-border rounded-lg px-4 py-3 text-center">
                <p className={`text-2xl font-bold ${dados.perc_geral >= 70 ? 'text-emerald-400' : dados.perc_geral >= 50 ? 'text-yellow-400' : 'text-red-400'}`}>
                  {dados.perc_geral}%
                </p>
                <p className="text-xs text-brand-muted mt-0.5">de acertos (geral)</p>
              </div>
              <div className="bg-brand-surface border border-brand-border rounded-lg px-4 py-3 text-center">
                <p className="text-2xl font-bold text-brand-text">{dados.total_sessoes}</p>
                <p className="text-xs text-brand-muted mt-0.5">sessões de estudo</p>
              </div>
            </div>

            {dados.por_materia.length > 0 ? (
              <div className="bg-brand-surface border border-brand-border rounded-xl overflow-hidden">
                <table className="w-full text-sm">
                  <thead className="border-b border-brand-border">
                    <tr>
                      <th className="text-left px-4 py-2 text-brand-muted font-medium text-xs">Matéria</th>
                      <th className="text-right px-4 py-2 text-brand-muted font-medium text-xs">Respondidas</th>
                      <th className="text-right px-4 py-2 text-brand-muted font-medium text-xs">Acertos</th>
                      <th className="text-right px-4 py-2 text-brand-muted font-medium text-xs">%</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-brand-border">
                    {dados.por_materia.map((m) => (
                      <tr key={m.materia}>
                        <td className="px-4 py-2 text-brand-text truncate max-w-xs">{m.materia}</td>
                        <td className="px-4 py-2 text-right text-brand-muted">{m.realizadas}</td>
                        <td className="px-4 py-2 text-right text-brand-muted">{m.acertos}</td>
                        <td className="px-4 py-2 text-right">
                          <span className={`font-semibold ${m.perc >= 70 ? 'text-emerald-400' : m.perc >= 50 ? 'text-yellow-400' : 'text-red-400'}`}>
                            {m.perc}%
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-brand-muted text-sm italic">Nenhuma questão respondida ainda.</p>
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default function AdminUsuarios() {
  const [usuarios, setUsuarios] = useState([])
  const [loading, setLoading] = useState(true)
  const [erro, setErro] = useState(null)
  const [busca, setBusca] = useState('')
  const [filtroRole, setFiltroRole] = useState('todos')
  const [filtroAtivo, setFiltroAtivo] = useState('todos')
  const [modalMentor, setModalMentor] = useState(null)
  const [modalProgresso, setModalProgresso] = useState(null)
  const [toggling, setToggling] = useState(null)
  const [modalCriar, setModalCriar] = useState(false)
  const [modalEditar, setModalEditar] = useState(null)
  const [modalReset, setModalReset] = useState(null)

  useEffect(() => {
    listarUsuarios()
      .then(setUsuarios)
      .catch(() => setErro('Erro ao carregar usuários.'))
      .finally(() => setLoading(false))
  }, [])

  const mentores = useMemo(
    () => usuarios.filter((u) => u.role === 'mentor' && u.ativo),
    [usuarios]
  )

  const filtrados = useMemo(() => {
    const buscaLow = busca.toLowerCase()
    return usuarios.filter((u) => {
      if (busca && !u.nome.toLowerCase().includes(buscaLow) && !u.email.toLowerCase().includes(buscaLow)) return false
      if (filtroRole !== 'todos' && u.role !== filtroRole) return false
      if (filtroAtivo === 'ativo' && !u.ativo) return false
      if (filtroAtivo === 'inativo' && u.ativo) return false
      return true
    })
  }, [usuarios, busca, filtroRole, filtroAtivo])

  async function toggleAtivo(usuario) {
    setToggling(usuario.id)
    try {
      const atualizado = await atualizarUsuario(usuario.id, { ativo: !usuario.ativo })
      setUsuarios((prev) => prev.map((u) => (u.id === atualizado.id ? atualizado : u)))
    } catch (err) {
      alert(err.response?.data?.detail || 'Erro ao alterar status do usuário.')
    } finally {
      setToggling(null)
    }
  }

  async function salvarMentor(usuarioId, mentorId) {
    const atualizado = await atribuirMentor(usuarioId, mentorId)
    setUsuarios((prev) => prev.map((u) => (u.id === atualizado.id ? atualizado : u)))
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (erro) {
    return <div className="p-6 text-red-400">{erro}</div>
  }

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      {modalCriar && (
        <ModalCriarUsuario
          onClose={() => setModalCriar(false)}
          onCriado={(novo) => setUsuarios((prev) => [novo, ...prev])}
        />
      )}
      {modalEditar && (
        <ModalEditarUsuario
          usuario={modalEditar}
          onClose={() => setModalEditar(null)}
          onSalvo={(atualizado) => setUsuarios((prev) => prev.map((u) => u.id === atualizado.id ? atualizado : u))}
        />
      )}
      {modalReset && (
        <ModalResetSenha usuario={modalReset} onClose={() => setModalReset(null)} />
      )}
      {modalMentor && (
        <ModalMentor
          usuario={modalMentor}
          mentores={mentores}
          onClose={() => setModalMentor(null)}
          onSave={salvarMentor}
        />
      )}
      {modalProgresso && (
        <ModalProgresso usuario={modalProgresso} onClose={() => setModalProgresso(null)} />
      )}

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-brand-text">Usuários</h1>
          <p className="text-brand-muted text-sm mt-1">{usuarios.length} usuários cadastrados</p>
        </div>
        <button
          onClick={() => setModalCriar(true)}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-lg transition-colors"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Novo usuário
        </button>
      </div>

      {/* Filtros */}
      <div className="flex flex-wrap gap-3">
        <input
          type="text"
          placeholder="Buscar por nome ou e-mail…"
          value={busca}
          onChange={(e) => setBusca(e.target.value)}
          className="flex-1 min-w-48 bg-brand-surface border border-brand-border rounded-lg px-3 py-2 text-brand-text text-sm placeholder-brand-muted focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
        <select
          value={filtroRole}
          onChange={(e) => setFiltroRole(e.target.value)}
          className="bg-brand-surface border border-brand-border rounded-lg px-3 py-2 text-brand-text text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500"
        >
          <option value="todos">Todos os perfis</option>
          <option value="estudante">Aluno</option>
          <option value="mentor">Mentor</option>
          <option value="administrador">Admin</option>
        </select>
        <select
          value={filtroAtivo}
          onChange={(e) => setFiltroAtivo(e.target.value)}
          className="bg-brand-surface border border-brand-border rounded-lg px-3 py-2 text-brand-text text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500"
        >
          <option value="todos">Todos</option>
          <option value="ativo">Ativos</option>
          <option value="inativo">Inativos</option>
        </select>
      </div>

      {/* Tabela */}
      <div className="bg-brand-card border border-brand-border rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-brand-border text-brand-muted text-xs uppercase tracking-wide">
              <th className="text-left px-4 py-3">Usuário</th>
              <th className="text-left px-4 py-3">Perfil</th>
              <th className="text-left px-4 py-3 hidden md:table-cell">Área</th>
              <th className="text-left px-4 py-3 hidden lg:table-cell">Mentor</th>
              <th className="text-left px-4 py-3 hidden lg:table-cell">Desde</th>
              <th className="text-left px-4 py-3">Status</th>
              <th className="text-right px-4 py-3">Ações</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-brand-border">
            {filtrados.length === 0 && (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-brand-muted">
                  Nenhum usuário encontrado.
                </td>
              </tr>
            )}
            {filtrados.map((u) => {
              const mentor = usuarios.find((m) => m.id === u.mentor_id)
              return (
                <tr
                  key={u.id}
                  className={`transition-colors hover:bg-brand-surface/50 ${!u.ativo ? 'opacity-60' : ''}`}
                >
                  <td className="px-4 py-3">
                    <div className="font-medium text-brand-text">{u.nome}</div>
                    <div className="text-brand-muted text-xs">{u.email}</div>
                  </td>
                  <td className="px-4 py-3">
                    <RoleBadge role={u.role} />
                  </td>
                  <td className="px-4 py-3 hidden md:table-cell text-brand-muted">
                    {u.area ?? '—'}
                  </td>
                  <td className="px-4 py-3 hidden lg:table-cell text-brand-muted">
                    {mentor ? mentor.nome : '—'}
                  </td>
                  <td className="px-4 py-3 hidden lg:table-cell text-brand-muted">
                    {new Date(u.created_at).toLocaleDateString('pt-BR')}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-0.5 rounded border ${u.ativo ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-red-500/10 text-red-400 border-red-500/20'}`}>
                      {u.ativo ? 'Ativo' : 'Inativo'}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center justify-end gap-1">
                      <button title="Editar" onClick={() => setModalEditar(u)}
                        className="text-brand-muted hover:text-indigo-400 transition-colors p-1.5 rounded hover:bg-indigo-500/10">
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                            d="M15.232 5.232l3.536 3.536M9 13l6.5-6.5a2 2 0 012.828 2.828L11.828 15.828A2 2 0 0111 16.414V18h1.586a2 2 0 001.414-.586L18 14" />
                        </svg>
                      </button>
                      <button title="Redefinir senha" onClick={() => setModalReset(u)}
                        className="text-brand-muted hover:text-yellow-400 transition-colors p-1.5 rounded hover:bg-yellow-500/10">
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                            d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                        </svg>
                      </button>
                      <button title="Ver progresso" onClick={() => setModalProgresso(u)}
                        className="text-brand-muted hover:text-sky-400 transition-colors p-1.5 rounded hover:bg-sky-500/10">
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                            d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                      </button>
                      {u.role === 'estudante' && (
                        <button title="Atribuir mentor" onClick={() => setModalMentor(u)}
                          className="text-brand-muted hover:text-indigo-400 transition-colors p-1.5 rounded hover:bg-indigo-500/10">
                          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                              d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0" />
                          </svg>
                        </button>
                      )}
                      <button title={u.ativo ? 'Desativar' : 'Ativar'} onClick={() => toggleAtivo(u)}
                        disabled={toggling === u.id}
                        className={`transition-colors px-2 py-1 rounded text-xs font-medium disabled:opacity-40 ${u.ativo ? 'text-red-400 hover:bg-red-400/10 border border-red-400/30' : 'text-emerald-400 hover:bg-emerald-400/10 border border-emerald-400/30 !opacity-100'}`}>
                        {toggling === u.id
                          ? <div className="w-3 h-3 border border-current border-t-transparent rounded-full animate-spin" />
                          : u.ativo ? 'Desativar' : 'Ativar'}
                      </button>
                    </div>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      <p className="text-xs text-brand-muted text-right">
        {filtrados.length} de {usuarios.length} usuários
      </p>
    </div>
  )
}
