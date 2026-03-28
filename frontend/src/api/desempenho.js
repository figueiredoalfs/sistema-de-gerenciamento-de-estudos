import client from './client'

export async function getDesempenho(params = {}) {
  const { data } = await client.get('/desempenho', { params })
  return data
}

export async function getEvolucao() {
  const { data } = await client.get('/desempenho/evolucao')
  return data
}

export async function getResumo() {
  const { data } = await client.get('/desempenho/resumo')
  return data
}

export async function getSubtopicosCriticos(limit = 10) {
  const { data } = await client.get('/desempenho/subtopicos-criticos', { params: { limit } })
  return data
}

export async function getSugestoesRevisao() {
  const { data } = await client.get('/desempenho/sugestoes-revisao')
  return data
}

export async function getPorMateria(params = {}) {
  const { data } = await client.get('/desempenho/por-materia', { params })
  return data
}

export async function getHeatmapSubtopicos(params = {}) {
  const { data } = await client.get('/desempenho/heatmap-subtopicos', { params })
  return data
}

export async function getVolumeSemanal() {
  const { data } = await client.get('/desempenho/volume-semanal')
  return data
}

export async function getConsistencia() {
  const { data } = await client.get('/desempenho/consistencia')
  return data
}

export async function getPorBanca() {
  const { data } = await client.get('/desempenho/por-banca')
  return data
}

export async function getPorBancoQuestoes() {
  const { data } = await client.get('/desempenho/por-banco-questoes')
  return data
}
