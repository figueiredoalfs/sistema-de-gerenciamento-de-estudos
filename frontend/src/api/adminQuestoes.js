import client from './client'

export async function listarQuestoes({ materia, subtopico, page = 1, per_page = 20 } = {}) {
  const params = { page, per_page }
  if (materia) params.materia = materia
  if (subtopico) params.subtopico = subtopico
  const { data } = await client.get('/admin/questoes', { params })
  return data
}

export async function editarQuestao(id, payload) {
  const { data } = await client.patch(`/admin/questoes/${id}`, payload)
  return data
}

export async function deletarQuestao(id) {
  await client.delete(`/admin/questoes/${id}`)
}

export async function importarQuestoes({ questoes }) {
  const { data } = await client.post(
    '/admin/importar-questoes',
    { questoes },
    { timeout: 180000 }, // 3 min — classificação IA é síncrona por questão
  )
  return data
}
