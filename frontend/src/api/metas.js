import client from './client'

export async function getActiveMeta() {
  // /metas/active retorna stats resumidos; /metas retorna a lista completa
  // Usamos /metas e filtramos a aberta para ter numero_semana e dados completos
  const { data } = await client.get('/metas')
  const aberta = data.metas?.find((m) => m.status === 'aberta') ?? null
  return aberta
}

export async function gerarMeta() {
  const { data } = await client.post('/metas/gerar', {})
  return data
}

export async function getMetas() {
  const { data } = await client.get('/metas')
  return data
}

export async function resetAluno() {
  const { data } = await client.post('/dev/reset-aluno')
  return data
}
