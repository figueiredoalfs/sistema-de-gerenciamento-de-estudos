"""
app/services/sugestao_subtopicos.py — Classificação automática de questões via IA.

Sugere subtópicos relevantes para uma questão analisando seu enunciado com Gemini.
Segue o mesmo padrão de app/services/explicacao_subtopico.py.
"""
import json
import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.ai_provider import AIProvider
from app.models.questao_banco import QuestaoBanco
from app.models.question_subtopic import QuestionSubtopic
from app.models.topico import Topico


def _build_prompt(questao: QuestaoBanco, subtopicos: list[Topico]) -> str:
    catalog_lines = [f'  {{"id": "{t.id}", "nome": "{t.nome}"}}' for t in subtopicos]
    catalog = "[\n" + ",\n".join(catalog_lines) + "\n]"

    try:
        alts = json.loads(questao.alternatives_json)
        alts_text = "\n".join(f"  {k}) {v}" for k, v in alts.items())
    except Exception:
        alts_text = ""

    return (
        "Você é um classificador de questões para concursos públicos brasileiros.\n"
        "Analise a questão abaixo e identifique quais subtópicos do catálogo são abordados nela.\n"
        "Retorne SOMENTE um array JSON com os IDs dos subtópicos relevantes (máximo 3).\n"
        "Se nenhum for relevante, retorne [].\n\n"
        f"DISCIPLINA: {questao.subject}\n\n"
        f"ENUNCIADO:\n{questao.statement}\n\n"
        + (f"ALTERNATIVAS:\n{alts_text}\n\n" if alts_text else "")
        + f"CATÁLOGO DE SUBTÓPICOS DISPONÍVEIS:\n{catalog}\n\n"
        "Resposta (apenas o array JSON, sem markdown, sem texto adicional):"
    )


def _parse_ids(raw: str, valid_ids: set) -> list[str]:
    text = raw.strip()

    # Remove markdown code fences se presentes
    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1] if len(parts) > 1 else text
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return []

    if not isinstance(parsed, list):
        return []

    validated = [str(item) for item in parsed if isinstance(item, str) and item in valid_ids]
    return validated[:5]  # guarda adicional contra excesso de retornos


def sugerir_subtopicos(
    questao: QuestaoBanco,
    subtopicos_disponiveis: list[Topico],
    ai: AIProvider,
) -> list[str]:
    """
    Retorna lista de IDs de subtópicos sugeridos pela IA para a questão.
    Nunca lança exceção — retorna [] em caso de falha.
    """
    if not subtopicos_disponiveis:
        return []

    valid_ids = {str(t.id) for t in subtopicos_disponiveis}
    prompt = _build_prompt(questao, subtopicos_disponiveis)

    try:
        raw = ai.generate(prompt)
        return _parse_ids(raw, valid_ids)
    except Exception:
        return []


def salvar_sugestoes(question_id: str, subtopic_ids: list[str], db: Session) -> None:
    """
    Persiste as associações sugeridas pela IA com fonte='ia'.
    Ignora duplicatas silenciosamente.
    """
    for subtopic_id in subtopic_ids:
        try:
            with db.begin_nested():
                assoc = QuestionSubtopic(
                    id=str(uuid.uuid4()),
                    question_id=question_id,
                    subtopic_id=subtopic_id,
                    fonte="ia",
                )
                db.add(assoc)
                db.flush()
        except IntegrityError:
            pass  # associação duplicada — ignora silenciosamente
