import client from './client'

export async function getDesempenho(params = {}) {
  const { data } = await client.get('/desempenho', { params })
  return data
}

export async function getEvolucao() {
  const { data } = await client.get('/desempenho/evolucao')
  return data
}
