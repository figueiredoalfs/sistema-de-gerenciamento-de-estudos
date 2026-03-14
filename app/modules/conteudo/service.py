from app.core.ai_provider import get_ai_provider


def gerar_resumo(topico: str) -> str:
    ai = get_ai_provider()
    prompt = (
        f"Explique o subtópico '{topico}' de forma clara e objetiva em no máximo 5 linhas. "
        "Foque especificamente neste subtópico e nos pontos mais cobrados em concursos públicos. "
        "Não fale de outros temas."
    )
    return ai.generate(prompt)


def gerar_flashcards(topico: str) -> list[dict]:
    ai = get_ai_provider()
    prompt = (
        f"Gere exatamente 5 flashcards sobre '{topico}' para estudo de concursos públicos. "
        "Responda SOMENTE neste formato JSON, sem texto adicional:\n"
        '[{"frente": "pergunta", "verso": "resposta"}, ...]'
    )
    import json
    texto = ai.generate(prompt)
    # Extrai o JSON da resposta
    inicio = texto.find("[")
    fim = texto.rfind("]") + 1
    if inicio == -1 or fim == 0:
        return []
    return json.loads(texto[inicio:fim])


def gerar_exemplo(topico: str) -> str:
    ai = get_ai_provider()
    prompt = (
        f"Dê um exemplo prático e objetivo sobre '{topico}' relevante para concursos públicos. "
        "Use no máximo 4 linhas."
    )
    return ai.generate(prompt)
