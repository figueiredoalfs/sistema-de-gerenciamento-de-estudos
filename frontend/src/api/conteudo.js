import client from './client'

export const getVideos = (taskCode) =>
  client.get(`/task-conteudo/${taskCode}/videos`).then(r => r.data)

export const buscarVideosIA = (taskCode) =>
  client.post(`/task-conteudo/${taskCode}/videos/buscar`).then(r => r.data)

export const avaliarVideo = (videoId, nota) =>
  client.post(`/task-videos/${videoId}/avaliar`, { nota }).then(r => r.data)

export const gerarPdf = (taskCode) =>
  client.post(`/task-conteudo/${taskCode}/gerar-pdf`, {}, { timeout: 30000 }).then(r => r.data)
