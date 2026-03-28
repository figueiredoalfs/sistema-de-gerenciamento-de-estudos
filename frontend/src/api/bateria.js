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

export async function postBateria(questoes) {
  // questoes: [{ materia, subtopico, acertos, total, fonte, banca? }]
  const { data } = await client.post('/bateria', { questoes })
  return data
}

export async function listarBaterias(params = {}) {
  const { data } = await client.get('/baterias', { params })
  return data
}
