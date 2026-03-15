"""
Serviço de conteúdo compartilhado de tasks.

Fluxo:
  1. obter_ou_criar_conteudo: get-or-create por (subtopico_id, tipo)
  2. gerar_objetivo_instrucoes: gera objetivo e instruções via IA, salva no banco
  3. gerar_pdf: gera material em formato cursinho via IA, salva no banco
  4. buscar_videos_ia: pede à IA sugestões de vídeos do YouTube, salva no banco
"""
import json
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.ai_provider import get_ai_provider
from app.models.task_conteudo import TaskConteudo, gerar_task_code
from app.models.task_video import TaskVideo
from app.models.topico import Topico


def _hierarquia(topico_id: str, db: Session) -> list[str]:
    nomes = []
    t = db.query(Topico).filter(Topico.id == topico_id).first()
    if not t:
        return nomes
    nomes.append(t.nome)
    if t.parent_id:
        pai = db.query(Topico).filter(Topico.id == t.parent_id).first()
        if pai:
            nomes.insert(0, pai.nome)
            if pai.parent_id:
                avo = db.query(Topico).filter(Topico.id == pai.parent_id).first()
                if avo:
                    nomes.insert(0, avo.nome)
    return nomes


def obter_ou_criar_conteudo(subtopico_id: str | None, tipo: str, db: Session) -> TaskConteudo:
    conteudo = db.query(TaskConteudo).filter(
        TaskConteudo.subtopico_id == subtopico_id,
        TaskConteudo.tipo == tipo,
    ).first()
    if conteudo:
        return conteudo

    novo = TaskConteudo(
        task_code=gerar_task_code(tipo),
        subtopico_id=subtopico_id,
        tipo=tipo,
    )
    try:
        db.add(novo)
        db.commit()
        db.refresh(novo)
    except IntegrityError:
        db.rollback()
        conteudo = db.query(TaskConteudo).filter(
            TaskConteudo.subtopico_id == subtopico_id,
            TaskConteudo.tipo == tipo,
        ).first()
        return conteudo
    return novo


TIPO_LABELS = {
    "teoria":       "Teoria",
    "revisao":      "Revisão",
    "questionario": "Questionário",
    "simulado":     "Simulado",
    "reforco":      "Reforço",
}


def gerar_objetivo_instrucoes(conteudo: TaskConteudo, db: Session) -> TaskConteudo:
    subtopico_nome = ""
    hierarquia_str = ""
    if conteudo.subtopico_id:
        hier = _hierarquia(conteudo.subtopico_id, db)
        subtopico_nome = hier[-1] if hier else ""
        hierarquia_str = " > ".join(hier)

    tipo_label = TIPO_LABELS.get(conteudo.tipo, conteudo.tipo)
    prompt = (
        f"Você é um professor preparatório para concursos públicos brasileiros.\n"
        f"Crie para a task do tipo '{tipo_label}' sobre o subtópico '{subtopico_nome}' "
        f"(contexto: {hierarquia_str}) dois textos curtos em JSON:\n\n"
        f"1. 'objetivo': uma frase descrevendo o que o aluno vai aprender/praticar (máx 100 palavras)\n"
        f"2. 'instrucoes': orientações práticas sobre como realizar a atividade (máx 80 palavras)\n\n"
        f"Responda APENAS com JSON no formato: {{\"objetivo\": \"...\", \"instrucoes\": \"...\"}}"
    )

    resposta = get_ai_provider().generate(prompt, max_tokens=400)

    try:
        dados = json.loads(resposta)
        conteudo.objetivo  = dados.get("objetivo", "")
        conteudo.instrucoes = dados.get("instrucoes", "")
    except (json.JSONDecodeError, AttributeError):
        conteudo.objetivo  = resposta[:500]
        conteudo.instrucoes = ""

    db.commit()
    db.refresh(conteudo)
    return conteudo


def gerar_pdf(task_code: str, db: Session) -> str:
    conteudo = db.query(TaskConteudo).filter(TaskConteudo.task_code == task_code).first()
    if not conteudo:
        return ""

    if conteudo.conteudo_pdf:
        return conteudo.conteudo_pdf

    subtopico_nome = ""
    hierarquia_str = ""
    if conteudo.subtopico_id:
        hier = _hierarquia(conteudo.subtopico_id, db)
        subtopico_nome = hier[-1] if hier else ""
        hierarquia_str = " > ".join(hier)

    tipo_label = TIPO_LABELS.get(conteudo.tipo, conteudo.tipo)
    is_reforco = conteudo.tipo == "reforco"

    prompt = (
        f"Você é um professor de cursinho preparatório para concursos públicos brasileiros.\n"
        f"Escreva um material de estudo {'resumido ' if is_reforco else ''}sobre '{subtopico_nome}' "
        f"(contexto: {hierarquia_str}) para a task de {tipo_label}.\n\n"
        f"{'Como é um Reforço, seja mais conciso: máx 300 palavras.' if is_reforco else 'Máx 600 palavras.'}\n\n"
        f"Estruture com:\n"
        f"## {subtopico_nome}\n"
        f"### Conceito Principal\n"
        f"### Como é Cobrado em Concurso\n"
        f"### Pontos-Chave\n"
        f"### Dica de Memorização\n\n"
        f"Use Markdown. Linguagem acessível para concurseiros."
    )

    pdf_texto = get_ai_provider().generate(prompt, max_tokens=2048)
    conteudo.conteudo_pdf = pdf_texto
    db.commit()
    return pdf_texto


def buscar_videos_ia(task_code: str, db: Session) -> list[TaskVideo]:
    conteudo = db.query(TaskConteudo).filter(TaskConteudo.task_code == task_code).first()
    if not conteudo:
        return []

    subtopico_nome = ""
    if conteudo.subtopico_id:
        hier = _hierarquia(conteudo.subtopico_id, db)
        subtopico_nome = hier[-1] if hier else ""

    prompt = (
        f"Sugira 3 vídeos educativos do YouTube sobre '{subtopico_nome}' para concursos públicos brasileiros.\n\n"
        f"Responda APENAS com JSON no formato:\n"
        f"[{{\"titulo\": \"...\", \"url\": \"https://youtube.com/watch?v=...\", \"descricao\": \"...\"}}]\n\n"
        f"Use URLs reais e conhecidas. Se não souber URLs exatas, use https://www.youtube.com/results?search_query={subtopico_nome.replace(' ', '+')}."
    )

    resposta = get_ai_provider().generate(prompt, max_tokens=600)

    try:
        inicio = resposta.find("[")
        fim = resposta.rfind("]") + 1
        dados = json.loads(resposta[inicio:fim])
    except (json.JSONDecodeError, ValueError):
        return []

    novos = []
    for item in dados[:3]:
        url = item.get("url", "")
        titulo = item.get("titulo", "")
        if not url or not titulo:
            continue
        existente = db.query(TaskVideo).filter(
            TaskVideo.task_code == task_code,
            TaskVideo.url == url,
        ).first()
        if not existente:
            video = TaskVideo(
                task_code=task_code,
                titulo=titulo,
                url=url,
                descricao=item.get("descricao", ""),
            )
            db.add(video)
            novos.append(video)

    if novos:
        db.commit()
        for v in novos:
            db.refresh(v)

    return db.query(TaskVideo).filter(TaskVideo.task_code == task_code).all()
