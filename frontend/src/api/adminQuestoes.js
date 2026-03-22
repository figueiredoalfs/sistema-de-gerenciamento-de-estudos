import client from './client'

export async function listarMateriasPorArea(areaId) {
  const { data } = await client.get('/admin/materias-por-area', { params: { area_id: areaId } })
  return data
}

export async function listarQuestoes({ materia, subtopico, banca, ano, area_id, page = 1, per_page = 20 } = {}) {
  const params = { page, per_page }
  if (materia) params.materia = materia
  if (subtopico) params.subtopico = subtopico
  if (banca) params.banca = banca
  if (ano) params.ano = ano
  if (area_id) params.area_id = area_id
  const res = await client.get('/admin/questoes', { params })
  return {
    questoes: res.data,
    totalFiltro: parseInt(res.headers['x-total-filtered'] || '0', 10),
    totalBanco: parseInt(res.headers['x-total-bank'] || '0', 10),
  }
}

export async function editarQuestao(id, payload) {
  const { data } = await client.patch(`/admin/questoes/${id}`, payload)
  return data
}

export async function deletarQuestao(id) {
  await client.delete(`/admin/questoes/${id}`)
}

export async function sugerirSubtopico(id) {
  const { data } = await client.post(`/admin/questoes/${id}/sugerir-subtopico`, {}, { timeout: 60000 })
  return data
}

export async function associarSubtopicos(id, subtopic_ids) {
  const { data } = await client.post(`/admin/questoes-banco/${id}/subtopicos`, { subtopic_ids })
  return data
}

export async function removerSubtopico(questionId, subtopicId) {
  await client.delete(`/admin/questoes-banco/${questionId}/subtopicos/${subtopicId}`)
}

export async function importarQuestoes({ questoes, classificar_subtopicos = false, classificar_areas = false }) {
  const { data } = await client.post(
    '/admin/importar-questoes',
    { questoes, classificar_subtopicos, classificar_areas },
    { timeout: 600000 },
  )
  return data
}

export async function listarAreas() {
  const { data } = await client.get('/admin/areas')
  return data
}

export async function sugerirArea(id) {
  const { data } = await client.post(`/admin/questoes/${id}/sugerir-areas`, {}, { timeout: 60000 })
  return data
}

export async function associarAreas(id, area_ids) {
  const { data } = await client.post(`/admin/questoes-banco/${id}/areas`, { area_ids })
  return data
}

export async function removerArea(questionId, areaId) {
  await client.delete(`/admin/questoes-banco/${questionId}/areas/${areaId}`)
}

export async function parsearTecPdf(file) {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await client.post('/admin/importar-tec', formData, {
    timeout: 60000,
    headers: { 'Content-Type': undefined },
  })
  return data
}

export async function importarTecQuestoes(questoes) {
  const { data } = await client.post('/admin/importar-tec-confirmar', { questoes }, { timeout: 120000 })
  return data
}

export async function parsearTecPdfV2(file) {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await client.post('/admin/importar-questoes-tec', formData, {
    timeout: 60000,
    headers: { 'Content-Type': undefined },
  })
  return data
}

export async function extrairQuestoesPdf(file) {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await client.post('/admin/importar-questoes-pdf', formData, {
    timeout: 300000,
    headers: { 'Content-Type': undefined },
  })
  return data
}

export async function listarPendencias() {
  const { data } = await client.get('/admin/materias-pendentes')
  return data
}

export async function resolverMateria(id, body) {
  const { data } = await client.post(`/admin/materias-pendentes/${id}/resolver-materia`, body)
  return data
}

export async function resolverBanca(id, body) {
  const { data } = await client.post(`/admin/materias-pendentes/${id}/resolver-banca`, body)
  return data
}

export async function reclassificarPendencias() {
  const { data } = await client.post('/admin/reclassificar')
  return data
}

export async function resolverMateriaLote(body) {
  const { data } = await client.post('/admin/materias-pendentes/resolver-materia-lote', body)
  return data
}

export async function resolverBancaLote(body) {
  const { data } = await client.post('/admin/materias-pendentes/resolver-banca-lote', body)
  return data
}
