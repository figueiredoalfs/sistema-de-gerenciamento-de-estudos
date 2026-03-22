import client from './client'

export async function listarNotificacoes({ lida } = {}) {
  const params = {}
  if (lida !== undefined) params.lida = lida
  const { data } = await client.get('/admin/notificacoes', { params })
  return data
}

export async function marcarNotificacaoLida(id) {
  const { data } = await client.patch(`/admin/notificacoes/${id}/marcar-lida`)
  return data
}

export async function deletarNotificacao(id) {
  await client.delete(`/admin/notificacoes/${id}`)
}
