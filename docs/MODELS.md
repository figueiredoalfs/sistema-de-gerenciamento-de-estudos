# Models do banco — ConcursoAI

## Aluno
id UUID | nome | email unique | senha_hash | role ENUM(admin/aluno)
nivel_desafio ENUM(conservador/moderado/agressivo) default=moderado
horas_por_dia Float default=3.0 | ativo bool | created_at

## Topico
id UUID | parent_id UUID FK self nullable | materia | titulo
nivel int (0=matéria / 1=bloco / 2=tópico)
peso_edital Float | decay_rate Float default=0.05
dependencias ARRAY(UUID) | situacao str nullable | created_at

## Proficiencia
id UUID | aluno_id FK | topico_id FK nullable | id_bateria
materia | data | acertos | total | percentual Float
fonte ENUM(qconcursos/tec/prova_anterior_mesma_banca/
           prova_anterior_outra_banca/simulado/quiz_ia/manual/calibracao)
peso_fonte Float default=1.0 | subtopico nullable | created_at

Pesos por fonte:
  mesma_banca=1.5 | outra_banca=1.2 | calibracao=1.2
  plataforma=1.0  | quiz_ia=0.8     | curso=0.6

## ErroCritico
id UUID | aluno_id FK | topico_id FK nullable | id_bateria
materia | topico_texto | qtd_erros | data
status ENUM(pendente/em_revisao/resolvido) default=pendente
observacao nullable | providencia nullable | created_at

## ConfigSistema
id UUID | chave str unique | valor str | descricao nullable
alterado_por UUID FK nullable | updated_at

## Sessao  ← campos críticos — não remover
id UUID | cronograma_id FK | topico_id FK
tipo ENUM(teoria_pdf/exercicios/video/flashcard_texto/calibracao)
duracao_min int | duracao_real_min int nullable
status ENUM(pendente/bloqueada/concluida/pulada)
data_agendada date nullable | data_concluida datetime nullable
taxa_acerto Float nullable
stability Float nullable    ← FSRS — coletar desde o início
difficulty Float nullable   ← FSRS — coletar desde o início
confianca ENUM(baixa/media/alta) default=baixa
uma_vez bool default=False | created_at

## Cronograma
id UUID | aluno_id FK | edital_id FK nullable
modo ENUM(pre_edital/pos_edital) default=pre_edital
data_inicio date | data_prova date nullable
status ENUM(ativo/pausado/concluido) default=ativo
modo_revisao_final bool default=False | created_at

## MetaSemanal
id UUID | aluno_id FK | cronograma_id FK
janela_inicio date | janela_fim date
carga_meta_min int | carga_realizada_min int default=0
deficit_min int default=0  ← PRIVADO — só admin/mentor vê
nivel_desafio str | status ENUM(ativa/concluida/expirada) | created_at

## PadraoCognitivo
id UUID | aluno_id FK | tipo str | confianca Float
total_erros_analisados int | detalhes_json JSONB nullable | updated_at

## Simulado
id UUID | aluno_id FK | edital_id FK nullable
total_questoes int | duracao_min int
questoes_json JSONB | resultado_json JSONB nullable
status ENUM(em_andamento/concluido) default=em_andamento | created_at

## Compatibilidade SQLite (dev) vs PostgreSQL (prod)
```python
if DATABASE_URL.startswith('sqlite'):
    engine = create_engine(DATABASE_URL,
                           connect_args={'check_same_thread': False})
else:
    engine = create_engine(DATABASE_URL)

# Fix Railway
DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://')
```
