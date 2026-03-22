import client from './client'

export async function login(email, senha) {
  const form = new URLSearchParams()
  form.append('username', email)
  form.append('password', senha)
  const { data } = await client.post('/auth/login', form, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  return data // { access_token, role, nome }
}

export async function getMe() {
  const { data } = await client.get('/auth/me')
  return data
}

export async function updateMe(payload) {
  const { data } = await client.patch('/auth/me', payload)
  return data
}

export async function register(payload) {
  const { data } = await client.post('/auth/register', payload)
  return data
}

export async function refreshAccessToken(refreshToken) {
  const { data } = await client.post('/auth/refresh', { refresh_token: refreshToken })
  return data // { access_token, refresh_token, role, nome }
}
