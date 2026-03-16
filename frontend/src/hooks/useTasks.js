import { useCallback, useEffect, useMemo, useState } from 'react'
import { getTodayTasks, updateTaskStatus } from '../api/tasks'
import { getActiveMeta, gerarMeta } from '../api/metas'
import { useAuth } from '../context/AuthContext'

export function useTasks() {
  const { user } = useAuth()
  const [tasks, setTasks] = useState([])
  const [meta, setMeta] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [tasksData, metaData] = await Promise.all([
        getTodayTasks(),
        getActiveMeta().catch(() => null),
      ])
      setTasks(Array.isArray(tasksData) ? tasksData : [])
      setMeta(metaData)
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao carregar tarefas')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (user) fetchData()
  }, [user, fetchData])

  const dailyLimit = useMemo(() => Math.max(1, Math.floor(user?.horas_por_dia ?? 3)), [user])

  const dailyTasks = useMemo(
    () => tasks.slice(0, dailyLimit),
    [tasks, dailyLimit]
  )

  const heroTask = useMemo(
    () => dailyTasks.find((t) => t.status === 'in_progress') ?? dailyTasks.find((t) => t.status === 'pending') ?? null,
    [dailyTasks]
  )

  const iniciarTask = useCallback(async (taskId) => {
    await updateTaskStatus(taskId, 'in_progress')
    setTasks((prev) => prev.map((t) => (t.id === taskId ? { ...t, status: 'in_progress' } : t)))
  }, [])

  const concluirTask = useCallback(async (taskId) => {
    await updateTaskStatus(taskId, 'completed')
    setTasks((prev) => prev.map((t) => (t.id === taskId ? { ...t, status: 'completed' } : t)))
    setMeta((prev) => prev ? { ...prev, tasks_concluidas: prev.tasks_concluidas + 1 } : prev)
  }, [])

  const criarMeta = useCallback(async () => {
    const nova = await gerarMeta()
    setMeta(nova)
    await fetchData()
  }, [fetchData])

  return { tasks: dailyTasks, allTasks: tasks, meta, loading, error, heroTask, iniciarTask, concluirTask, criarMeta, refetch: fetchData }
}
