import client from './client'

export async function getConfigs() {
  const { data } = await client.get('/admin/config')
  return data
}

export async function getModelosIA() {
  const { data } = await client.get('/admin/config/modelos-ia')
  return data
}

export async function upsertConfig(chave, valor, descricao) {
  const { data } = await client.put(`/admin/config/${chave}`, { valor, descricao })
  return data
}
