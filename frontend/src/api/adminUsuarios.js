import client from './client'

export async function listarUsuarios() {
  const { data } = await client.get('/admin/usuarios')
  return data
}

export async function atualizarUsuario(id, body) {
  const { data } = await client.patch(`/admin/usuarios/${id}`, body)
  return data
}

export async function atribuirMentor(id, mentor_id) {
  const { data } = await client.patch(`/admin/usuarios/${id}/mentor`, { mentor_id })
  return data
}

export async function progressoUsuario(id) {
  const { data } = await client.get(`/admin/usuarios/${id}/progresso`)
  return data
}

export async function criarUsuario(body) {
  const { data } = await client.post('/admin/usuarios', body)
  return data
}
