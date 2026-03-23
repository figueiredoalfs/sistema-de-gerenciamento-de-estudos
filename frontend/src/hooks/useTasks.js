import { useCallback, useEffect, useMemo, useState } from 'react'
import { getTodayTasks, updateTaskStatus } from '../api/tasks'
import { getActiveMeta, gerarMeta, iniciarDiagnostico, resetAluno } from '../api/metas'
import { useAuth } from '../context/AuthContext'

export function useTasks() {
  const { user, refreshUser } = useAuth()
  const [tasks, setTasks] = useState([])
  const [meta, setMeta] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [metaError, setMetaError] = useState(null)
  const [resetting, setResetting] = useState(false)

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [tasksData, metaData] = await Promise.all([
        getTodayTasks(),
        getActiveMeta().catch(() => null),
      ])
      const lista = tasksData?.tasks ?? (Array.isArray(tasksData) ? tasksData : [])
      setTasks(lista)
      setMeta(metaData)

      // Auto-iniciar diagnóstico se pendente e sem meta ativa
      if (user?.diagnostico_pendente && !metaData) {
        try {
          const novaMeta = await iniciarDiagnostico()
          setMeta(novaMeta)
          // Buscar tasks da meta diagnóstica
          const novasTasks = await getTodayTasks()
          const novaLista = novasTasks?.tasks ?? (Array.isArray(novasTasks) ? novasTasks : [])
          setTasks(novaLista)
        } catch {
          // Falha silenciosa — admin precisa configurar ciclos/subtópicos
        }
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao carregar tarefas')
    } finally {
      setLoading(false)
    }
  }, [user])

  useEffect(() => {
    if (user) fetchData()
  }, [user, fetchData])

  const heroTask = useMemo(
    () => tasks.find((t) => t.status === 'in_progress') ?? tasks.find((t) => t.status === 'pending') ?? null,
    [tasks]
  )

  const iniciarTask = useCallback(async (taskId) => {
    await updateTaskStatus(taskId, 'in_progress')
    setTasks((prev) => prev.map((t) => (t.id === taskId ? { ...t, status: 'in_progress' } : t)))
  }, [])

  const concluirTask = useCallback(async (taskId) => {
    await updateTaskStatus(taskId, 'completed')
    setMeta((prev) => prev ? { ...prev, tasks_concluidas: prev.tasks_concluidas + 1 } : prev)
    await fetchData()
    // Atualiza diagnostico_pendente no contexto após concluir task diagnóstica
    if (user?.diagnostico_pendente) {
      await refreshUser()
    }
  }, [fetchData, refreshUser, user])

  const criarMeta = useCallback(async () => {
    setMetaError(null)
    try {
      const nova = await gerarMeta()
      setMeta(nova)
      await fetchData()
    } catch (err) {
      const msg = err.response?.data?.detail || 'Erro ao gerar meta. Tente novamente.'
      setMetaError(msg)
    }
  }, [fetchData])

  const resetarDados = useCallback(async () => {
    setResetting(true)
    setMetaError(null)
    try {
      await resetAluno()
      // Atualiza user no contexto — area fica null, frontend redirecionará para /onboarding
      await refreshUser()
      return { redirectToOnboarding: true }
    } catch (err) {
      const msg = err.response?.data?.detail || 'Erro ao resetar dados.'
      setMetaError(msg)
      return { error: msg }
    } finally {
      setResetting(false)
    }
  }, [refreshUser])

  return { tasks, meta, loading, error, metaError, heroTask, iniciarTask, concluirTask, criarMeta, resetarDados, resetting, refetch: fetchData }
}
