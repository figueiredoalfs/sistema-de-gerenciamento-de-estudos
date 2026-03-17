import client from './client'

export async function listarTodosTopicos() {
  const { data } = await client.get('/admin/topicos', { params: { apenas_ativos: false } })
  return data
}

export async function criarTopico(body) {
  const { data } = await client.post('/admin/topicos', body)
  return data
}

export async function editarTopico(id, body) {
  const { data } = await client.patch(`/admin/topicos/${id}`, body)
  return data
}

export async function desativarTopico(id) {
  await client.delete(`/admin/topicos/${id}`)
}

export async function questoesPorSubtopico() {
  const { data } = await client.get('/admin/topicos/questoes-por-subtopico')
  return data
}
