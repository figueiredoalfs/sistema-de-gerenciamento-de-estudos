import client from './client'

export async function listarAlunos() {
  const { data } = await client.get('/mentor/alunos')
  return data
}

export async function progressoAluno(id) {
  const { data } = await client.get(`/mentor/alunos/${id}/progresso`)
  return data
}

export async function resumoAluno(id) {
  const { data } = await client.get(`/mentor/alunos/${id}/resumo`)
  return data
}
