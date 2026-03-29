import client from './client'

export async function getHierarquia() {
  const { data } = await client.get('/topicos/hierarquia')
  return data
}

export async function getHierarquiaCompleta() {
  const { data } = await client.get('/topicos/hierarquia-completa')
  return data
}

export async function getBancas() {
  const { data } = await client.get('/bancas')
  return data // [{ nome: "CESPE/CEBRASPE" }, ...]
}

export async function postBateria(questoes, duracao_min = null) {
  // questoes: [{ materia, subtopico, acertos, total, fonte, banca? }]
  const { data } = await client.post('/bateria', { questoes, duracao_min })
  return data
}

export async function listarBaterias(params = {}) {
  const { data } = await client.get('/baterias', { params })
  return data
}

export async function getBateriaDetail(bateriaId) {
  const { data } = await client.get(`/baterias/${bateriaId}`)
  return data
}

export async function putBateria(bateriaId, body) {
  const { data } = await client.put(`/baterias/${bateriaId}`, body)
  return data
}
