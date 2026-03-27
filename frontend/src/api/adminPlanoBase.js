import client from './client'

export async function listarPlanos({ area, perfil, pendente_revisao } = {}) {
  const params = {}
  if (area) params.area = area
  if (perfil) params.perfil = perfil
  if (pendente_revisao) params.pendente_revisao = true
  const { data } = await client.get('/admin/planos-base', { params })
  return data
}

export async function gerarPlano({ area, perfil }) {
  const { data } = await client.post('/admin/planos-base/gerar', { area, perfil }, { timeout: 60000 })
  return data
}

export async function aprovarPlano(id) {
  const { data } = await client.patch(`/admin/planos-base/${id}`, { revisado_admin: true })
  return data
}

export async function atualizarPlano(id, body) {
  const { data } = await client.patch(`/admin/planos-base/${id}`, body)
  return data
}

export async function deletarPlano(id) {
  await client.delete(`/admin/planos-base/${id}`)
}

export async function criarPlano({ area, perfil, fases = [] }) {
  const { data } = await client.post('/admin/planos-base', { area, perfil, fases })
  return data
}

export async function aplicarPlano(id, modo = 'novos') {
  const { data } = await client.post(`/admin/planos-base/${id}/aplicar`, null, { params: { modo } })
  return data
}

export async function getHierarquiaAdmin() {
  const { data } = await client.get('/admin/topicos/hierarquia')
  return data
}
