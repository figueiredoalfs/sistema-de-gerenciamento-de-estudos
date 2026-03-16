import client from './client'

export async function importarLote(questoes) {
  const res = await client.post('/questoes/lote', questoes)
  return res.data
}

export async function listarTopicos(nivel) {
  const params = nivel !== undefined ? { nivel } : {}
  const res = await client.get('/admin/topicos', { params })
  return res.data
}
