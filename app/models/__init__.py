from app.models.aluno import Aluno
from app.models.topico import Topico
from app.models.proficiencia import Proficiencia
from app.models.erro_critico import ErroCritico
from app.models.config_sistema import ConfigSistema
from app.models.sessao import Sessao
from app.models.cronograma import Cronograma
from app.models.meta_semanal import MetaSemanal
from app.models.padrao_cognitivo import PadraoCognitivo
from app.models.simulado import Simulado
from app.models.questao import Questao
from app.models.exam import Exam
from app.models.subject import Subject
from app.models.topic import Topic
from app.models.topic_progress import TopicProgress
from app.models.question_attempt import QuestionAttempt
from app.models.resposta_questao import RespostaQuestao
from app.models.study_task import StudyTask
from app.models.perfil_estudo import PerfilEstudo
from app.models.ciclo_materia import CicloMateria
from app.models.explicacao_subtopico import ExplicacaoSubtopico
from app.models.questao_banco import QuestaoBanco
from app.models.question_subtopic import QuestionSubtopic
from app.models.task_conteudo import TaskConteudo
from app.models.task_video import TaskVideo
from app.models.task_video_avaliacao import TaskVideoAvaliacao
from app.models.meta import Meta
from app.models.subtopico_estado import SubtopicoEstado
from app.models.plano_base import PlanoBase

__all__ = [
    "Aluno",
    "Topico",
    "Proficiencia",
    "ErroCritico",
    "ConfigSistema",
    "Sessao",
    "Cronograma",
    "MetaSemanal",
    "PadraoCognitivo",
    "Simulado",
    "Questao",
    "Exam",
    "Subject",
    "Topic",
    "TopicProgress",
    "QuestionAttempt",
    "RespostaQuestao",
    "StudyTask",
    "PerfilEstudo",
    "CicloMateria",
    "ExplicacaoSubtopico",
    "QuestaoBanco",
    "QuestionSubtopic",
    "TaskConteudo",
    "TaskVideo",
    "TaskVideoAvaliacao",
    "Meta",
    "SubtopicoEstado",
    "PlanoBase",
]
