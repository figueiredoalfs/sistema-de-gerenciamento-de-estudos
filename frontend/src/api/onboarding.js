import client from './client'

export async function submitOnboarding(payload) {
  const { data } = await client.post('/onboarding', payload)
  return data
}
