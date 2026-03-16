import client from './client'

export async function getTodayTasks() {
  const { data } = await client.get('/tasks/today')
  return data.tasks ?? data // TasksTodayResponse tem { daily_limit, tasks: [...] }
}

export async function updateTaskStatus(taskId, status) {
  const { data } = await client.patch(`/tasks/${taskId}/status`, { status })
  return data
}
