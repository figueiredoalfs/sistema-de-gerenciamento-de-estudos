import client from './client'

export async function getHierarquia() {
  const { data } = await client.get('/topicos/hierarquia')
  return data
}

export async function postBateria(materia, subtopico, acertos, total, fonte) {
  const { data } = await client.post('/bateria', {
    questoes: [{ materia, subtopico, acertos, total, fonte }],
  })
  return data
}
