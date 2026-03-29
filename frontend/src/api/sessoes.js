import client from './client'

export async function postSessaoEstudo(body) {
  const { data } = await client.post('/sessoes-estudo', body)
  return data
}

export async function listarSessoes(limit = 20) {
  const { data } = await client.get('/sessoes-estudo', { params: { limit } })
  return data
}

export async function putSessaoEstudo(id, body) {
  const { data } = await client.put(`/sessoes-estudo/${id}`, body)
  return data
}
