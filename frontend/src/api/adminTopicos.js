import client from './client'

export async function listarTodosTopicos() {
  const { data } = await client.get('/admin/topicos', { params: { apenas_ativos: false } })
  return data
}

export async function listarMaterias() {
  const { data } = await client.get('/admin/topicos', { params: { nivel: 0, apenas_ativos: true } })
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

export async function hierarquiaTopicos() {
  const { data } = await client.get('/admin/topicos/hierarquia')
  return data
}

export async function listarAreasSubtopico(id) {
  const { data } = await client.get(`/admin/topicos/${id}/areas`)
  return data
}

export async function salvarAreaSubtopico(id, body) {
  // body: { area, peso, complexidade }
  const { data } = await client.patch(`/admin/topicos/${id}/area`, body)
  return data
}

// ─── Bancas ───────────────────────────────────────────────────────────────────

export async function listarBancas(apenasAtivas = true) {
  const { data } = await client.get('/admin/bancas', { params: { apenas_ativas: apenasAtivas } })
  return data
}

export async function criarBanca(nome) {
  const { data } = await client.post('/admin/bancas', { nome })
  return data
}

export async function editarBanca(id, body) {
  const { data } = await client.patch(`/admin/bancas/${id}`, body)
  return data
}

export async function desativarBanca(id) {
  await client.delete(`/admin/bancas/${id}`)
}
