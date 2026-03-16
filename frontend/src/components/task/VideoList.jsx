import { useEffect, useState } from 'react'
import { getVideos, buscarVideosIA, avaliarVideo } from '../../api/conteudo'

function StarRating({ videoId, mediaAtual, onAvaliado }) {
  const [notaLocal, setNotaLocal] = useState(0)
  const [hover, setHover] = useState(0)
  const [avaliado, setAvaliado] = useState(false)

  async function handleAvaliar(n) {
    setNotaLocal(n)
    setAvaliado(true)
    try {
      const res = await avaliarVideo(videoId, n)
      onAvaliado(videoId, res.avaliacao_media)
    } catch {
      setAvaliado(false)
    }
  }

  const estrelaAtiva = hover || notaLocal || Math.round(mediaAtual ?? 0)

  return (
    <div className="flex items-center gap-0.5 mt-2">
      {[1, 2, 3, 4, 5].map(n => (
        <button
          key={n}
          disabled={avaliado}
          onClick={() => handleAvaliar(n)}
          onMouseEnter={() => setHover(n)}
          onMouseLeave={() => setHover(0)}
          className={`text-base leading-none transition-colors disabled:cursor-default ${
            n <= estrelaAtiva ? 'text-amber-400' : 'text-brand-border'
          }`}
        >
          ★
        </button>
      ))}
      {mediaAtual > 0 && (
        <span className="text-xs text-brand-muted ml-1">{mediaAtual.toFixed(1)}</span>
      )}
    </div>
  )
}

export default function VideoList({ taskCode }) {
  const [videos, setVideos] = useState([])
  const [loading, setLoading] = useState(true)
  const [buscando, setBuscando] = useState(false)
  const [erro, setErro] = useState(null)

  useEffect(() => {
    getVideos(taskCode)
      .then(setVideos)
      .catch(() => setErro('Erro ao carregar vídeos.'))
      .finally(() => setLoading(false))
  }, [taskCode])

  async function handleBuscar() {
    setBuscando(true)
    setErro(null)
    try {
      const novos = await buscarVideosIA(taskCode)
      setVideos(novos)
    } catch {
      setErro('Erro ao buscar vídeos com IA.')
    } finally {
      setBuscando(false)
    }
  }

  function handleAvaliado(videoId, novaMedia) {
    setVideos(vs => vs.map(v => v.id === videoId ? { ...v, avaliacao_media: novaMedia } : v))
  }

  if (loading) return (
    <div className="flex items-center justify-center py-16">
      <div className="w-7 h-7 rounded-full border-2 border-brand-border border-t-indigo-500 animate-spin" />
    </div>
  )

  if (!videos.length) return (
    <div className="bg-brand-card border border-brand-border rounded-xl p-8 text-center space-y-4">
      <div className="text-3xl">🎬</div>
      <p className="text-brand-text font-medium text-sm">Nenhum vídeo disponível</p>
      <p className="text-brand-muted text-xs">A IA pode buscar vídeos relevantes no YouTube.</p>
      {erro && <p className="text-red-400 text-xs">{erro}</p>}
      <button
        onClick={handleBuscar}
        disabled={buscando}
        className="px-5 py-2.5 bg-brand-gradient text-white text-sm font-semibold rounded-xl hover:opacity-90 transition-all disabled:opacity-50"
      >
        {buscando ? 'Buscando...' : '🔍 Buscar com IA'}
      </button>
    </div>
  )

  return (
    <div className="space-y-3">
      {videos.map(v => (
        <div key={v.id} className="bg-brand-card border border-brand-border rounded-xl p-4 hover:border-slate-600 transition-all">
          <a
            href={v.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-indigo-400 hover:text-indigo-300 font-medium text-sm transition-colors line-clamp-2"
          >
            {v.titulo}
          </a>
          {v.descricao && (
            <p className="text-brand-muted text-xs mt-1 line-clamp-2">{v.descricao}</p>
          )}
          <StarRating
            videoId={v.id}
            mediaAtual={v.avaliacao_media ?? 0}
            onAvaliado={handleAvaliado}
          />
        </div>
      ))}
      <button
        onClick={handleBuscar}
        disabled={buscando}
        className="w-full py-2 text-xs text-brand-muted hover:text-brand-text border border-brand-border rounded-xl transition-all disabled:opacity-50"
      >
        {buscando ? 'Buscando...' : '↺ Atualizar com IA'}
      </button>
      {erro && <p className="text-red-400 text-xs text-center">{erro}</p>}
    </div>
  )
}
