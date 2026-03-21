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

export async function sugerirSubtopico(id) {
  const { data } = await client.post(`/admin/questoes/${id}/sugerir-subtopico`)
  return data
}

export async function associarSubtopicos(id, subtopic_ids) {
  const { data } = await client.post(`/admin/questoes-banco/${id}/subtopicos`, { subtopic_ids })
  return data
}

export async function removerSubtopico(questionId, subtopicId) {
  await client.delete(`/admin/questoes-banco/${questionId}/subtopicos/${subtopicId}`)
}

export async function importarQuestoes({ questoes, classificar_ia = true }) {
  const { data } = await client.post(
    '/admin/importar-questoes',
    { questoes, classificar_ia },
    { timeout: 180000 },
  )
  return data
}

export async function extrairQuestoesPdf(file) {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await client.post('/admin/importar-questoes-pdf', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120000, // 2 min — extração de PDF pode ser lenta
  })
  return data
}
