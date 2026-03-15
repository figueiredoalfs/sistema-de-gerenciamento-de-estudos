"""
Serviço de explicações automáticas de subtópicos com cache.

Fluxo:
  1. Verifica se já existe explicação salva para o topico_id → retorna cache
  2. Se não existe: monta prompt com hierarquia, chama IA, salva e retorna
"""
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.ai_provider import get_ai_provider
from app.models.explicacao_subtopico import ExplicacaoSubtopico
from app.models.topico import Topico


def _build_prompt(nome: str, hierarquia: list[str]) -> str:
    hierarquia_str = " > ".join(hierarquia)
    return (
        f"Você é um professor preparatório para concursos públicos brasileiros.\n"
        f"Explique de forma clara e direta o tópico **{nome}** "
        f"(contexto: {hierarquia_str}).\n\n"
        f"Estruture a explicação com:\n"
        f"1. **Conceito principal** (2-3 linhas)\n"
        f"2. **Como é cobrado em concurso** (padrão de questões, pegadinhas comuns)\n"
        f"3. **Dica de memorização** (1 frase, exemplo prático ou analogia)\n\n"
        f"Use linguagem acessível para quem estuda para concursos. Máximo 350 palavras."
    )


def obter_ou_gerar(topico_id: str, db: Session) -> tuple[str, bool]:
    """
    Retorna (content, cached).
    cached=True se veio do banco; cached=False se foi gerado agora pela IA.
    """
    # 1. Verifica cache no banco
    cache = db.query(ExplicacaoSubtopico).filter(
        ExplicacaoSubtopico.topico_id == topico_id
    ).first()
    if cache:
        return cache.content, True

    # 2. Busca tópico e hierarquia para o prompt
    topico = db.query(Topico).filter(Topico.id == topico_id).first()
    if not topico:
        return "Subtópico não encontrado.", False

    hierarquia = [topico.nome]
    if topico.parent_id:
        pai = db.query(Topico).filter(Topico.id == topico.parent_id).first()
        if pai:
            hierarquia.insert(0, pai.nome)
            if pai.parent_id:
                avo = db.query(Topico).filter(Topico.id == pai.parent_id).first()
                if avo:
                    hierarquia.insert(0, avo.nome)

    # 3. Gera via IA
    prompt = _build_prompt(topico.nome, hierarquia)
    content = get_ai_provider().generate(prompt)

    # 4. Salva no cache (protegido contra race condition via IntegrityError)
    explicacao = ExplicacaoSubtopico(topico_id=topico_id, content=content)
    try:
        db.add(explicacao)
        db.commit()
    except IntegrityError:
        db.rollback()
        # Outro processo salvou primeiro — retorna o que já existe
        cache = db.query(ExplicacaoSubtopico).filter(
            ExplicacaoSubtopico.topico_id == topico_id
        ).first()
        return (cache.content if cache else content), True

    return content, False
