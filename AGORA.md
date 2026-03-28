# AGORA.md — Skolai
> Modelo: Desenvolvimento Espiral
> Visão: Analisador de desempenho para concursos públicos fiscais
> O aluno lança o que estudou e o que errou. O Skolai analisa e aponta onde melhorar.
> Atualizado: 28/03/2026 | www.skolai.com.br no ar

---

## Visão do produto

```
Entrada:  aluno lança sessões de estudo e baterias de questões
Processo: algoritmo analisa desempenho por subtópico
Saída:    métricas, gráficos e sugestões de revisão
```

**O que o Skolai NÃO é:** gerador de cronograma, banco de questões, plataforma de resolução.
**O que o Skolai É:** camada de análise e diagnóstico em cima do estudo que o aluno já faz.

---

## Stack
- Backend: FastAPI + SQLAlchemy + SQLite(dev) / PostgreSQL(prod)
- Frontend: React 18 + Vite + Tailwind + React Router v6 + Caddy
- Deploy: Railway — Frontend (Dockerfile+Caddy) + Backend + PostgreSQL
- IA: sem uso no MVP — tudo via algoritmo

---

## Infraestrutura Railway — NÃO alterar sem necessidade

### Serviços ativos
| Serviço | URL | Status |
|---|---|---|
| Frontend | www.skolai.com.br | Online |
| Backend | domínio Railway interno | Online |
| PostgreSQL | gerado pelo Railway | Online |

### Variáveis de ambiente — Backend
- DATABASE_URL — PostgreSQL Railway (automático, não alterar)
- SECRET_KEY — chave JWT
- GEMINI_API_KEY — reservado para futuro uso
- ALLOWED_ORIGINS — https://www.skolai.com.br
- ADMIN_EMAIL, ADMIN_NOME, ADMIN_SENHA

### Variáveis de ambiente — Frontend
- VITE_API_URL — URL pública do backend
- PORT = 80

### Arquivos críticos — nunca modificar sem necessidade
- `frontend/Dockerfile` — build 2 estágios: node:18-alpine + caddy:2-alpine
- `frontend/.dockerignore` — sem isso node_modules Windows quebra o build
- `frontend/Caddyfile` — try_files obrigatório para React Router funcionar
- `frontend/railway.toml` — builder = "dockerfile" (não nixpacks)
- Ferramentas de build (vite, tailwind) em `dependencies`, não devDependencies

### Proibições absolutas
- NÃO voltar para nixpacks — quebra build por NODE_ENV=production
- NÃO deletar .dockerignore do frontend
- NÃO remover PORT=80 das variáveis do frontend
- NÃO alterar DATABASE_URL manualmente
- NÃO commitar .env, dev.db ou sisfig.db
- NÃO remover fix postgres:// → postgresql:// em config.py
- NÃO alterar ALLOWED_ORIGINS para "*" em produção
- NÃO usar gemini-2.5-flash
- NÃO remover try_files do Caddyfile

### Fluxo obrigatório ao mudar schema do banco
```bash
alembic revision --autogenerate -m "descricao"
alembic upgrade head                          # testa local
git add alembic/versions/
git commit && git push                        # Railway faz deploy
railway run alembic upgrade head              # aplica no PostgreSQL
```

---

## Regras de implementação
1. Leia o módulo correspondente em `docs/modulos/` antes de implementar
2. Backend primeiro — testar no /docs antes de tocar no frontend
3. Frontend consome o endpoint confirmado
4. Só concluir quando funcionar no navegador de ponta a ponta
5. Contrato quebrado → corrigir backend, nunca adaptar frontend
6. Sem IA no MVP — toda lógica via algoritmo puro
7. Uma task por vez — não avançar sem concluir e testar a atual

---

## Hierarquia de matérias — Área Fiscal
> Baseada na estrutura do TEC Concursos.
> Três níveis: Matéria → Módulo (Tópico) → Subtópico.
> Esta é a estrutura do seed do banco de dados.

### 1. Direito Tributário
**Módulo 1 — Teoria Geral e Espécies**
- Conceito de Tributo
- Classificação Doutrinária dos Tributos
- Natureza Jurídica Específica dos Tributos
- Impostos (Conceito e Classificações)
- Taxas (CF/1988 e CTN)
- Contribuição de Melhoria (CF/1988 e CTN)
- Empréstimo Compulsório (CF/1988 e CTN)
- Contribuições Especiais (CF/1988)
- Questões Mescladas de Espécies de Tributos

**Módulo 2 — Sistema Tributário Nacional (CF)**
- Princípios Tributários
- Imunidades Tributárias
- Competência para Legislar sobre Direito Tributário
- Competência Tributária: Conceitos e Características
- Repartição da Competência Tributária
- Bitributação e Bis in Idem
- Repartição Constitucional de Receitas (arts. 157 a 162 da CF)

**Módulo 3 — Normas Gerais (CTN)**
- Disposições Gerais da Legislação (arts. 96 a 100)
- Vigência e Aplicação (arts. 101 a 106)
- Interpretação e Integração (arts. 107 a 112)
- Espécies Normativas Aplicadas ao Direito Tributário
- Disposições Gerais da Obrigação Tributária
- Fato Gerador (arts. 114 a 118)
- Sujeito Ativo e Passivo (arts. 119 a 123)
- Solidariedade (arts. 124 e 125)
- Capacidade Tributária (art. 126)
- Domicílio Tributário (art. 127)
- Responsabilidade Tributária (arts. 128 a 138)
- Disposições Gerais do Crédito Tributário
- Lançamento e Constituição (arts. 142 a 150)
- Suspensão da Exigibilidade (arts. 151 a 155-A)
- Extinção do Crédito Tributário (arts. 156 a 174)
- Exclusão do Crédito Tributário (arts. 175 a 182)
- Garantias e Privilégios do Crédito (arts. 183 a 193)
- Fiscalização Tributária (arts. 194 a 200)
- Dívida Ativa Tributária (arts. 201 a 204)
- Certidão Negativa (arts. 205 a 208)
- Disposições Finais e Transitórias do CTN

**Módulo 4 — Impostos em Espécie e Reforma**
- II, IE, IR, IPI, IOF, ITR e IGF
- ICMS, IPVA e ITCMD
- ISS, IPTU e ITBI
- IBS, CBS, Comitê Gestor e Imposto Seletivo (Reforma EC 132/2023)

**Módulo 5 — Processo e Temas Especiais**
- Processo Administrativo Tributário (PAT)
- Processo Judicial Tributário
- Lei de Execução Fiscal (Lei 6.830/80)
- Medida Cautelar Fiscal, Mandado de Segurança e Tutelas
- Elisão, Evasão e Elusão Fiscal
- Direito Tributário Internacional

**Módulo 6 — Jurisprudência Tributária**
- Jurisprudência dos Tribunais Superiores (STF/STJ)

---

### 2. Direito Administrativo
**Módulo 1 — Fundamentos e Atos Administrativos**
- Introdução (Origem, Conceito e Fontes)
- Regime Jurídico Administrativo (Princípios Expressos e Implícitos)
- Conceito e Mérito Administrativo
- Elementos (COMFIFORMOB) e Atributos (PATI)
- Classificação e Espécies de Atos
- Extinção (Anulação, Revogação e Cassação)
- Convalidação e Teoria dos Motivos Determinantes

**Módulo 2 — Poderes e Organização do Estado**
- Poderes Vinculado, Discricionário, Regulamentar, Hierárquico e Disciplinar
- Poder de Polícia (Ciclo e Atributos)
- Abuso de Poder (Excesso e Desvio de Finalidade)
- Administração Direta e Indireta
- Desconcentração e Descentralização
- Lei 13.303/2016 (Estatuto das Estatais)
- Terceiro Setor (OS, OSCIP, Sistema S, MROSC)

**Módulo 3 — Agentes Públicos e Lei 8.112/90**
- Conceito, Classificação e Acessibilidade
- Acumulação de Cargos e Estabilidade (art. 37 a 41 da CF)
- Remuneração e Teto Constitucional
- Provimento e Vacância (Lei 8.112/90)
- Direitos e Vantagens (Férias, Licenças, Adicionais)
- Regime Disciplinar (Deveres, Proibições e Sanções)
- Processo Administrativo Disciplinar (PAD) e Sindicância

**Módulo 4 — Gestão Pública, Responsabilidade e Controle**
- Conceito, Princípios e Classificação de Serviços Públicos
- Concessões e Permissões (Lei 8.987/95)
- Parcerias Público-Privadas (Lei 11.079/04) e Consórcios (Lei 11.107/05)
- Teoria Objetiva e Risco Administrativo
- Responsabilidade por Omissão
- Excludentes e Direito de Regresso
- Autotutela, Controle Judicial e Controle Legislativo
- Desapropriação, Servidão, Requisição, Ocupação, Limitação e Tombamento

**Módulo 5 — Ética, Probidade e Processo**
- Atos de Improbidade (Enriquecimento, Prejuízo e Princípios)
- Sanções, Prescrição e ANPC (Lei 8.429/1992)
- Lei Anticorrupção e Acordo de Leniência (Lei 12.846/2013)
- Processo Administrativo Federal (Lei 9.784/1999)
- Lei de Acesso à Informação — Transparência e Sigilo (Lei 12.527/2011)

**Módulo 6 — Licitações e Contratos (Lei 14.133/2021)**
- Âmbito de Aplicação, Princípios e Fase Preparatória (ETP)
- Modalidades (incluindo Diálogo Competitivo e Pregão)
- Contratação Direta (Inexigibilidade e Dispensa)
- Instrumentos Auxiliares (SRP)
- Alocação de Riscos, Garantias e Duração dos Contratos
- Alteração, Equilíbrio Econômico e Extinção
- Sanções, Recursos e Portal Nacional de Contratações (PNCP)
- Regulamentação Complementar (Decretos 2022-2024)
- Legislação Esparsa (Informática, Publicidade e Estatais)

**Módulo 7 — Jurisprudência**
- Informativos e Súmulas (STF e STJ)

---

### 3. Direito Constitucional
**Módulo 1 — Teoria e Princípios Fundamentais**
- Conceito, Estrutura e Classificação das Constituições
- Aplicabilidade e Eficácia das Normas
- Poder Constituinte (Originário, Derivado e Mutação)
- Interpretação e Hermenêutica Constitucional
- Aplicação no Tempo (Recepção e Repristinação)
- Fundamentos, Objetivos e Princípios Internacionais (arts. 1º ao 4º)

**Módulo 2 — Direitos e Garantias Fundamentais**
- Direitos em Espécie e Características (art. 5º)
- Remédios Constitucionais (HC, MS, MI, HD, AP)
- Direitos Sociais e dos Trabalhadores (arts. 6º a 11)
- Nacionalidade (Natos/Naturalizados e Perda)
- Direitos Políticos (Soberania, Inelegibilidades e Perda/Suspensão)
- Partidos Políticos (art. 17)

**Módulo 3 — Organização do Estado e Administração**
- Competências da União, Estados, DF e Municípios (arts. 18 a 36)
- Intervenção Federal e Estadual
- Disposições Gerais e Servidores Públicos (arts. 37 a 43)

**Módulo 4 — Organização dos Poderes**
- Congresso Nacional, Atribuições e Imunidades Parlamentares
- Processo Legislativo (PEC, Leis, MPs e Vetos)
- Fiscalização Contábil/Financeira — TCU
- Atribuições e Responsabilidades do Presidente
- Estatuto da Magistratura, Garantias e Vedações
- Precatórios, STF, Súmulas Vinculantes, CNJ e STJ
- Justiças Especializadas (Federal, Trabalho, Eleitoral e Militar)
- Ministério Público, Advocacia Pública e Defensoria Pública

**Módulo 5 — Defesa do Estado e Tributação**
- Estado de Defesa, Estado de Sítio e Forças Armadas
- Segurança Pública
- Sistema Tributário Nacional (Limitações e Impostos)
- Finanças Públicas: PPA, LDO e LOA

**Módulo 6 — Ordem Econômica, Social e ADCT**
- Princípios Econômicos, Atuação do Estado e Sistema Financeiro
- Seguridade Social (Saúde, Previdência e Assistência)
- Educação, Cultura, Meio Ambiente, Família e Índios
- Disposições Finais e Transitórias (ADCT)

**Módulo 7 — Controle de Constitucionalidade e Jurisprudência**
- Modelos de Controle (Preventivo/Repressivo)
- Controle Difuso (Incidental)
- Controle Concentrado (ADI, ADC, ADO e ADPF)
- Informativos e Temas de Repercussão Geral (STF e STJ)

---

### 4. Contabilidade Geral e Avançada
**Módulo 1 — Fundamentos e Estrutura Inicial**
- Conceito, Objeto, Campo de Aplicação e Técnicas Contábeis
- Teoria das Contas (Natureza Devedora e Credora)
- CPC 00 (R2): Estrutura Conceitual
- Atos e Fatos Contábeis (Permutativos, Modificativos e Mistos)
- Lançamentos Contábeis (1ª, 2ª, 3ª e 4ª Fórmulas)
- Livros Diário e Razão; Balancete de Verificação
- Regimes de Competência vs. Caixa

**Módulo 2 — Ciclo Operacional e Ativos**
- Critérios de Avaliação de Estoques: PEPS e Média Ponderada (CPC 16)
- Operações com Mercadorias (CMV, RCM e Tributos Recuperáveis)
- Disponibilidades e Conciliação Bancária
- Contas a Receber e PECLD
- Ajuste a Valor Presente (AVP - CPC 12)
- Investimentos: Avaliação pelo Custo ou MEP
- Imobilizado: Mensuração e Depreciação
- Intangível (CPC 04): Ágio (Goodwill)
- CPC 01 (Impairment): Redução ao Valor Recuperável

**Módulo 3 — Passivo e Patrimônio Líquido**
- Empréstimos, Financiamentos e Debêntures (CPC 08)
- CPC 25: Provisões, Passivos e Ativos Contingentes
- Capital Social (Subscrito, a Realizar e Realizado)
- Reservas de Lucros e Reservas de Capital
- Ajuste de Avaliação Patrimonial (AAP)

**Módulo 4 — Demonstrações Contábeis**
- DRE: Estrutura e apuração do Lucro Líquido
- DRA: Demonstração de Resultados Abrangentes
- DFC (CPC 03): Métodos Direto e Indireto
- DVA (CPC 09): Valor Adicionado
- DMPL/DLPA: Mutações do PL
- Notas Explicativas e Consolidação (CPC 36)

**Módulo 5 — Normas Especiais e Contabilidade Digital**
- CPC 06: Arrendamentos (Direito de Uso)
- CPC 47: Receita de Contrato com Cliente
- CPC 24: Eventos Subsequentes
- ECD e Sistema SPED
- Dividendos e Juros sobre Capital Próprio (JCP)

---

### 5. Língua Portuguesa
**Módulo 1 — Bases da Escrita e Sons**
- Fonemas, Dígrafos e Encontros Vocálicos/Consonantais
- Separação Silábica
- Emprego das Letras (X/CH, S/Z, J/G)
- Acentuação Gráfica (Regras e Novo Acordo)
- Uso do Hífen
- Iniciais Maiúsculas e Convenções de Escrita

**Módulo 2 — Morfologia**
- Estrutura e Formação de Palavras
- Substantivo, Artigo, Adjetivo, Numeral, Interjeição e Advérbio
- Conjugação, Reconhecimento e Emprego de Tempos/Modos Verbais
- Correlação Verbal e Locuções Verbais
- Pronomes Pessoais, Possessivos, Indefinidos e Interrogativos
- Pronomes Demonstrativos
- Pronomes Relativos
- Conjunções Coordenativas e Subordinativas
- Preposições

**Módulo 3 — Semântica e Coesão**
- Sinônimos/Antônimos e Homônimos/Parônimos
- Denotação vs Conotação e Polissemia
- Anáfora e Catáfora
- Ordenação de Parágrafos e Significação de Vocábulos

**Módulo 4 — Sintaxe**
- Sujeito (Tipos) e Predicado
- Objetos (Direto/Indireto), Agente da Passiva e Complemento Nominal
- Adjuntos (Adnominal/Adverbial), Aposto e Vocativo
- Adjunto Adnominal x Complemento Nominal
- Orações Coordenadas e Subordinadas
- Orações Reduzidas
- Uso da Vírgula (Casos proibidos, obrigatórios e facultativos)
- Travessão, Aspas, Dois-pontos e Parênteses

**Módulo 5 — Concordância, Regência e Crase**
- Concordância Verbal e Nominal
- Regência Verbal e Nominal
- Crase (Regras e Exceções)
- Vozes Verbais (Ativa, Passiva e Reflexiva)

**Módulo 6 — Interpretação, Estilo e Partículas Especiais**
- Partícula "Se" (Apassivadora, Indeterminadora)
- Vocábulos "Que" e "Como"
- Interpretação de Textos (Compreensão, Tipologia e Gêneros)
- Reescrita de Frases
- Paralelismo Sintático/Semântico
- Figuras, Vícios e Funções da Linguagem

---

### 6. Auditoria
**Módulo 1 — Fundamentos e Normas Profissionais**
- Trabalhos de Asseguração (Razoável vs. Limitada)
- NBC TA 200: Objetivos Gerais do Auditor
- Ceticismo e Julgamento Profissional
- Princípios Éticos e Independência do Auditor
- NBC TA 220 / NBC PA 01: Controle de Qualidade

**Módulo 2 — Planejamento e Identificação de Riscos**
- Estratégia Global vs. Plano de Auditoria (NBC TA 300)
- Risco de Auditoria (Inerente, de Controle e de Detecção)
- Identificação de Distorções Relevantes (NBC TA 315)
- Materialidade no Planejamento e Execução (NBC TA 320)
- Responsabilidade do Auditor e Fraude (NBC TA 240)

**Módulo 3 — Execução e Evidências**
- Adequação e Suficiência das Provas (NBC TA 500)
- Procedimentos: Inspeção, Observação, Indagação, Recálculo
- Procedimentos Analíticos
- Amostragem Estatística vs. Não Estatística (NBC TA 530)
- Auditoria de Estimativas Contábeis e Contingências
- Papéis de Trabalho: Propriedade, Custódia e Sigilo (NBC TA 230)

**Módulo 4 — Conclusão e Relatórios**
- Tipos de Relatório: Sem Ressalva vs. Modificado
- Opinião Modificada: Com Ressalva, Adversa e Abstenção
- Parágrafos de Ênfase e Outros Assuntos
- Eventos Subsequentes (NBC TA 560)
- Continuidade Operacional (NBC TA 570)
- Carta de Responsabilidade da Administração

**Módulo 5 — Auditoria Interna, Governança e Risco**
- Diferenças entre Auditoria Interna e Externa (NBC TI 01)
- COSO ICIF (Controle Interno) e COSO ERM (Gestão de Riscos)
- Lei Sarbanes-Oxley (SOX)
- Princípios e Governança no Setor Público

**Módulo 6 — Especialidades e Normas Complementares**
- Perícia Contábil (NBC TP 01 e PP 01)
- Normas do BACEN e da CVM

---

### 7. Direito Civil
**Módulo 1 — Lei de Introdução e Parte Geral**
- Pessoas Naturais: Personalidade, Capacidade e Direitos da Personalidade
- Pessoas Jurídicas: Disposições Gerais, Associações e Fundações
- Desconsideração da Personalidade Jurídica
- Domicílio das Pessoas Naturais e Jurídicas
- Classificação dos Bens e Bens Públicos

**Módulo 2 — Fatos Jurídicos e Negócio Jurídico**
- Teoria Geral dos Fatos Jurídicos
- Classificações e Disposições Gerais do Negócio Jurídico
- Representação (arts. 115 a 120)
- Condição, Termo e Encargo
- Defeitos ou Vícios do Negócio Jurídico
- Invalidade do Negócio Jurídico
- Atos Ilícitos
- Prescrição e Decadência
- Prova do Negócio Jurídico

**Módulo 3 — Direito das Obrigações**
- Obrigações de Dar, Fazer e Não Fazer
- Obrigações Alternativas, Divisíveis e Solidárias
- Cessão de Crédito e Assunção de Dívida
- Pagamento e Formas de Extinção da Obrigação
- Mora, Perdas e Danos, Juros Legais e Cláusula Penal

**Módulo 4 — Contratos**
- Princípios e Classificação dos Contratos
- Formação, Vícios Redibitórios e Evicção
- Extinção dos Contratos
- Compra e Venda, Doação, Locação, Mandato
- Seguro, Fiança, Transação e demais espécies

**Módulo 5 — Atos Unilaterais e Responsabilidade Civil**
- Promessa de Recompensa, Gestão de Negócios
- Pagamento Indevido e Enriquecimento Sem Causa
- Responsabilidade Civil: Disposições Gerais

**Módulo 6 — Direito das Coisas**
- Posse: Teorias, Aquisição, Efeitos e Perda
- Propriedade: Aquisição, Perda e Direito de Vizinhança
- Condomínio e Propriedades Especiais
- Superfície, Servidões, Usufruto, Uso e Habitação
- Penhor, Hipoteca e Anticrese

**Módulo 7 — Direito de Família e Sucessões**
- Casamento, Regime de Bens e União Estável
- Alimentos, Guarda e Parentesco
- Tutela, Curatela e Tomada de Decisão Apoiada
- Herança, Vocação Hereditária e Testamentos
- Inventário e Partilha

**Módulo 8 — Disposições Finais e Transitórias**
- Regras de Transição e Enfiteuse

---

### 8. Direito Empresarial
**Módulo 1 — Teoria Geral do Empresário**
- Conceito, Autonomia, Fontes e Princípios
- Caracterização e Inscrição do Empresário Individual
- Capacidade Empresarial

**Módulo 2 — Estabelecimento, Registro e Escrituração**
- Do Estabelecimento (arts. 1.142 a 1.149 do CC)
- Do Registro (arts. 1.150 a 1.154 do CC)
- Nome Empresarial, Prepostos e Escrituração

**Módulo 3 — Direito Societário**
- Sociedade em Comum e em Conta de Participação
- Sociedade Simples e em Nome Coletivo
- Sociedade em Comandita Simples
- Sociedade Limitada (arts. 1.052 a 1.087)
- Sociedade Cooperativa
- Dissolução, Liquidação e Extinção das Sociedades
- Operações Societárias (Fusão, Cisão, Incorporação)

**Módulo 4 — Sociedade Anônima (Lei 6.404/1976)**
- Características e Constituição da Companhia
- Capital Social, Ações, Debêntures e Bônus
- Governança: Assembleia, Conselhos e Diretoria
- Dissolução, Liquidação e Extinção das SA
- Grupos de Sociedades e Consórcio

**Módulo 5 — Títulos de Crédito**
- Conceito, Características e Princípios
- Letra de Câmbio e Nota Promissória
- Cheque (Lei 7.357/1985)
- Duplicata (Lei 5.474/1968)
- Protesto e demais espécies

**Módulo 6 — Falência e Recuperação de Empresas (Lei 11.101/2005)**
- Disposições Comuns à Recuperação e à Falência
- Recuperação Judicial e Convolação em Falência
- Da Falência (arts. 75 a 160)
- Recuperação Extrajudicial

**Módulo 7 — Propriedade Industrial (Lei 9.279/1996)**
- Patentes, Desenhos Industriais e Marcas
- Indicações Geográficas e Transferência de Tecnologia
- Propriedade Intelectual de Software (Lei 9.609/1998)

**Módulo 8 — Contratos Mercantis**
- Contratos Bancários (Depósito, Mútuo, Desconto)
- Alienação Fiduciária, Leasing e Factoring
- Representação, Agência, Franquia (Lei 13.966/2019)

**Módulo 9 — Cooperativismo**
- História, Conceitos e Princípios
- Lei 5.764/1971

**Módulo 10 — Jurisprudência**
- STJ e STF sobre Sociedades, Títulos e Falência

---

### 9. Matemática Financeira
**Módulo 1 — Conceitos Fundamentais e Juros**
- Capital, Montante, Taxa e Desconto
- Juros Simples e Taxas Proporcionais
- Juros Compostos e Taxas Equivalentes
- Taxas Efetivas, Nominais e Capitalização Contínua
- Inflação, Juros Reais e Juros Aparentes

**Módulo 2 — Descontos**
- Desconto Comercial Simples e Racional Simples
- Desconto Comercial Composto e Racional Composto
- Relação entre Desconto Comercial e Racional

**Módulo 3 — Séries de Pagamentos e Fluxo de Caixa**
- Classificação das Rendas
- Valor Atual de Uma Série de Pagamentos
- Valor Futuro de Uma Série de Pagamentos
- Equivalência de Capitais e Rearranjo do Fluxo

**Módulo 4 — Sistemas de Amortização**
- Sistema de Amortização Constante (SAC)
- Sistema de Amortização Francês (Tabela Price)
- Sistema de Amortização Americano e Alemão
- Sistemas Mistos de Amortização

**Módulo 5 — Análise de Investimentos**
- Valor Presente Líquido (VPL)
- Taxa Interna de Retorno (TIR) e TMA
- Payback e Payback Descontado
- Índice de Lucratividade e Taxa de Rentabilidade
- Títulos com Cupons Periódicos (Bonds)

---

### 10. Raciocínio Lógico
**Módulo 1 — Lógica Proposicional**
- Proposições e Operadores Lógicos
- Ordem de Precedência entre Conectivos
- Tabela Verdade das Proposições Compostas
- Tautologia, Contradição e Contingência
- Equivalências Lógicas e Negação de Proposições
- Condição Necessária e Suficiente

**Módulo 2 — Lógica de Argumentação**
- Argumentos e Métodos da Tabela Verdade
- Raciocínio Crítico
- Argumentos Indutivos e por Abdução
- Falácias

**Módulo 3 — Lógica de Primeira Ordem**
- Lógica de Primeira Ordem e Predicados
- Diagramas Lógicos e Proposições Categóricas
- Negação de Quantificadores

**Módulo 4 — Problemas de Lógica**
- Sequências de Números, Figuras e Letras
- Associação de Informações
- Exercícios de Verdade/Mentira
- Parentesco, Datas e Calendários
- Problemas com Balança, Palitos e Similares

**Módulo 5 — Lógica Espacial**
- Planificação de Sólidos e Projeções 3D
- Orientação no Plano, no Espaço e no Tempo

---

### 11. Tecnologia da Informação
**Módulo 1 — Organização e Arquitetura de Computadores**
- Sistemas de Numeração e Operações Lógicas
- Arquitetura Von Neumann e Harvard, RISC vs CISC
- Hierarquia de Memória (RAM, ROM, Cache)
- HD, SSD, RAID e Periféricos

**Módulo 2 — Sistemas Operacionais**
- Gerência de Processos, Threads e Deadlock
- Paginação, Memória Virtual e Sistemas de Arquivos
- Windows (XP ao 11) e Comandos CMD/PowerShell
- Linux: Kernel, Comandos de Terminal e Shell Script
- Virtualização, Docker e Kubernetes

**Módulo 3 — Redes de Computadores e Internet**
- Modelo OSI (7 camadas) e TCP/IP (4 camadas)
- IP (IPv4, IPv6), Sub-redes, ARP, DHCP e DNS
- TCP, UDP e Protocolos de Roteamento
- Ethernet, Wi-Fi 6, Bluetooth e VLANs
- HTTP/HTTPS, FTP, SSH, VoIP e SNMP

**Módulo 4 — Segurança da Informação**
- ISO 27001/27002/27005, LGPD e Compliance
- Criptografia Simétrica, Assimétrica e Hashes
- Assinatura Digital e Certificados Digitais (ICP-Brasil)
- Firewall, IDS/IPS, VPN e Zero Trust
- Malware, Phishing, DoS/DDoS e OWASP Top 10
- Backup (RPO/RTO), MFA e Controle de Acesso (RBAC)

**Módulo 5 — Engenharia de Software**
- RUP, Cascata, Espiral, Incremental e Prototipação
- Scrum, Kanban, XP e SAFe
- UML (Casos de Uso, Classes, Sequência)
- Qualidade: ISO 12207, TDD, BDD e Tipos de Testes
- Git, CI/CD e IaC

**Módulo 6 — Desenvolvimento de Sistemas**
- Microsserviços, SOA e Arquitetura Hexagonal
- REST/RESTful, SOAP e gRPC
- Estruturas de Dados e Princípios SOLID
- Linguagens: Java, Python, .NET, C#

**Módulo 7 — Banco de Dados**
- MER, Mapeamento Relacional e Normalização
- SQL: DDL, DML, DQL, Triggers e Views
- Transações ACID e Controle de Concorrência
- NoSQL: Modelos, Teorema CAP e MongoDB

**Módulo 8 — Ciência de Dados e IA**
- Data Warehouse, ETL e Modelagem Dimensional
- OLAP (Drill-down, Roll-up, Slice, Dice)
- Big Data: Hadoop, Data Lake e Apache Spark
- Machine Learning: Supervisionado e Não Supervisionado
- Power BI, Tableau e Python (Pandas, Scikit-Learn)

**Módulo 9 — Gestão e Governança de TI**
- COBIT (4.1, 5, 2019) e ITIL (v3 e v4)
- BPM, BPMN e Processos de Negócio
- IN SGD/ME 94/2022 e Guia de PDTIC

**Módulo 10 — Aplicativos e Ferramentas**
- Microsoft Office (Word, Excel, PowerPoint)
- LibreOffice e Navegadores
- Google Workspace e Microsoft Teams

---

## Matéria fora do ciclo básico (inativa — em implementação)
- **Legislação Tributária** — depende do concurso específico do aluno (ICMS estadual, ISS municipal, RFB federal). Ativar no fluxo pós-edital.

---

## Campos no lançamento de questões
- **Banco de questões** (obrigatório) — de onde veio a questão: TEC Concursos, Qconcursos, Gran Cursos, Estratégia, CERS, Simulado Próprio, Outro
- **Banca** (opcional) — CESPE/CEBRASPE, FCC, FGV, VUNESP, AOCP, IDECAN, IBFC, QUADRIX, IADES, UPENET, Outra

---

## Métricas e gráficos do MVP

### Métricas por subtópico
- Taxa de acerto atual (últimas 20 questões)
- Taxa de acerto histórica (total)
- Tendência: melhorando / estável / piorando (comparar últimas 2 semanas)
- Volume total de questões realizadas
- Dias desde a última sessão
- Status de domínio: Dominado (≥70%) / Em progresso (50-69%) / Crítico (<50%) / Não iniciado

### Métricas por matéria
- Taxa de acerto média ponderada
- Contagem de subtópicos por status (dominado / em progresso / crítico / não iniciado)
- Volume total de questões
- Horas de estudo registradas
- Evolução semanal da taxa de acerto

### Métricas globais
- Taxa de acerto geral
- Meta de 90% — % atingido globalmente e por matéria
- Total de questões realizadas (semana / mês / total)
- Horas de estudo registradas (semana / mês / total)
- Consistência: dias estudados nos últimos 30 dias
- Sequência atual (streak): dias consecutivos com registro
- Matérias com registro esta semana

### Gráficos — ordenados por prioridade
1. **Mapa de calor de subtópicos** — grid matéria × subtópico, cor por taxa de acerto (vermelho <50%, amarelo 50-70%, verde ≥70%)
2. **Radar de matérias** — teia com % acerto por matéria
3. **Evolução temporal por matéria** — linha com taxa de acerto por semana
4. **Volume de questões por semana** — barras empilhadas por matéria, últimas 8 semanas
5. **Heatmap de consistência** — calendário estilo GitHub, últimos 365 dias
6. **Ranking de matérias por taxa de acerto** — barras horizontais
7. **Subtópicos críticos** — lista priorizada por criticidade (taxa baixa × volume alto)
8. **Taxa de acerto por banca** — quando banca informada
9. **Taxa de acerto por banco de questões** — comparativo entre plataformas

### Lista de revisão sugerida (algoritmo)
Subtópicos aparecem na lista quando:
- Taxa de acerto < 70% E última sessão há mais de 7 dias → urgente
- Taxa de acerto < 50% independente da data → crítico
- Mais de 14 dias sem revisão, independente da taxa → revisar

---

## VOLTA 1 — MVP funcional

### V1-T01 — Limpeza do código morto
⬜ PENDING

**Contexto:** O sistema atual tem uma arquitetura complexa de plano de estudos,
engine pedagógica, tasks, metas e questionário. Tudo isso será removido.
O produto novo é mais simples — só precisa de autenticação, lançamento e análise.

**O que deletar — arquivos e pastas:**
```bash
# Backend — remover completamente:
app/services/engine_pedagogica.py
app/services/plano_inicial.py
app/services/plano_base.py       # ou nome equivalente
app/routers/tasks.py             # ou study_tasks.py
app/routers/metas.py
app/routers/task_conteudo.py
app/routers/explicacoes.py
app/routers/conhecimento.py
app/models/study_task.py
app/models/meta.py
app/models/plano_base.py

# Frontend — remover completamente:
frontend/src/pages/TaskView.jsx
frontend/src/components/dashboard/TaskCard.jsx
frontend/src/components/dashboard/TaskHero.jsx
frontend/src/components/dashboard/VerticalTimeline.jsx
frontend/src/components/task/QuestionFlow.jsx
frontend/src/components/task/VideoList.jsx
frontend/src/components/task/PdfPanel.jsx
```

**O que manter:**
- app/routers/auth.py
- app/routers/admin_*.py
- app/models/aluno.py
- app/models/topico.py (matérias/módulos/subtópicos)
- frontend/src/pages/Login.jsx
- frontend/src/pages/Onboarding.jsx
- frontend/src/pages/Desempenho.jsx (reformular)
- frontend/src/components/layout/Sidebar.jsx (simplificar)

**Após deletar:**
- Verificar se o backend ainda sobe sem erros
- Verificar se não há imports quebrados

**Arquivos:** deletar os listados acima

---

### V1-T02 — Limpar e repovoar banco de dados
⬜ PENDING

**Contexto:** O banco tem matérias antigas com estrutura errada.
Precisa ser limpo e repovoado com a hierarquia TEC Concursos completa
das 11 matérias fiscais.

**O que fazer:**
Criar `scripts/seed_fiscal.py` que:
1. Deleta todos os registros de topicos, ciclo_materias, subtopico_area
2. Insere as 11 matérias com seus módulos e subtópicos conforme
   a hierarquia documentada na seção "Hierarquia de matérias" deste arquivo
3. Estrutura: nivel=0 (matéria), nivel=1 (módulo/tópico), nivel=2 (subtópico)
4. Vincula cada subtópico à área "fiscal"

```bash
railway run python scripts/seed_fiscal.py
```

**Verificar:**
- /admin/topicos → 11 matérias aparecem
- Cada matéria expande em módulos
- Cada módulo expande em subtópicos

**Arquivos a criar:**
- CRIAR: `scripts/seed_fiscal.py`

---

### V1-T03 — Simplificar onboarding
⬜ PENDING

**Contexto:** O onboarding atual tem muitas etapas e opções.
Manter a estrutura visual mas desativar o que não está implementado.

**O que fazer:**
Em `frontend/src/pages/Onboarding.jsx` e componentes relacionados:

Etapa de seleção de área:
- Área Fiscal → ativa, clicável
- Todas as outras áreas → aparência desativada (cinza), tooltip "Em implementação"

Etapa de funcionalidades:
- "Análise de Desempenho" → ativa, selecionada por padrão
- Todas as outras funcionalidades → desativadas com tag "Em implementação"

Etapa de fase de estudo:
- "Pré-edital" → ativa
- "Pós-edital" → desativada com tag "Em implementação"

Manter o fluxo existente para o que está ativo.
Não remover o código das opções inativas — só desabilitar visualmente.

**Verificar:**
- Onboarding completo sem erros
- Áreas inativas não são clicáveis
- Área Fiscal funciona normalmente

**Arquivos:**
- MODIFICAR: `frontend/src/pages/Onboarding.jsx` e componentes de etapa

---

### V1-T04 — Reformular dashboard como central de análise
⬜ PENDING

**Contexto:** O dashboard atual mostra tasks do dia. O novo dashboard
é a central de análise — mostra o estado atual do desempenho do aluno.

**O que implementar:**

**Backend — novos endpoints:**
```
GET /desempenho/resumo
  Retorna:
  - taxa_acerto_geral: float
  - total_questoes: int
  - total_horas: float
  - streak_dias: int
  - dias_estudados_30d: int
  - materias: [{ nome, taxa_acerto, total_questoes, status }]

GET /desempenho/subtopicos-criticos?limit=10
  Retorna lista dos subtópicos com pior desempenho:
  [{ materia, modulo, subtopico, taxa_acerto, total_questoes, dias_sem_revisar }]

GET /desempenho/sugestoes-revisao
  Algoritmo:
  - taxa < 50%: crítico
  - taxa < 70% + sem revisão > 7 dias: urgente
  - sem revisão > 14 dias: revisar
  Retorna lista ordenada por prioridade
```

**Frontend — nova Dashboard.jsx:**
```
Seção 1 — KPIs globais (4 cards):
  Taxa de acerto geral | Total de questões | Dias de estudo | Streak

Seção 2 — Matérias (barras horizontais):
  Ranking de matérias por taxa de acerto, com cor por status

Seção 3 — Revisão sugerida (lista):
  Subtópicos que precisam de atenção, com botão "Registrar sessão"

Seção 4 — Atividade recente:
  Últimas 5 sessões registradas
```

**Verificar:**
- Dashboard carrega com dados reais
- KPIs corretos
- Lista de revisão aparece quando há subtópicos abaixo de 70%

**Arquivos:**
- CRIAR/MODIFICAR: `app/routers/desempenho.py`
- CRIAR: `app/services/analise_desempenho.py`
- MODIFICAR: `frontend/src/pages/Dashboard.jsx`

---

### V1-T05 — Implementar registro de sessão de estudo
⬜ PENDING

**Contexto:** O aluno registra que estudou um subtópico — com ou sem questões.
Isso alimenta o heatmap de consistência e o cálculo de "última revisão".

**O que implementar:**

**Backend:**
Model `SessaoEstudo`:
```python
id, aluno_id, subtopico_id, tipo ("teoria" | "questoes"),
data, duracao_min (opcional), created_at
```

Endpoint `POST /sessoes`:
```json
{
  "subtopico_id": "uuid",
  "tipo": "teoria",
  "data": "2026-03-28",
  "duracao_min": 45
}
```

**Frontend:**
Nova página `/registrar-estudo`:
- Select hierárquico: Matéria → Módulo → Subtópico
- Select tipo: Teoria / Questões
- Input data (default hoje)
- Input duração em minutos (opcional)
- Botão Salvar
- Após salvar: feedback + opção de registrar outro

Link na sidebar: "Registrar Estudo"

**Verificar:**
- Registrar sessão de teoria → aparece no heatmap do dashboard
- Dados de duração aparecem no resumo de horas estudadas

**Arquivos:**
- CRIAR: `app/models/sessao_estudo.py`
- CRIAR/MODIFICAR: `app/routers/sessoes.py`
- CRIAR: `frontend/src/pages/RegistrarEstudo.jsx`
- Criar migration Alembic

---

### V1-T06 — Implementar Caderno de Questões
⬜ PENDING

**Contexto:** Centro do produto. O aluno registra baterias de questões
que fez em plataformas externas (TEC Concursos, Qconcursos, etc.).
O sistema analisa esses dados.

**O que implementar:**

**Backend:**
Model `BateriaQuestoes`:
```python
id, aluno_id, subtopico_id, data,
acertos, total, percentual (calculado),
banco_questoes, banca (nullable), created_at
```

Endpoint `POST /baterias`:
```json
{
  "subtopico_id": "uuid",
  "data": "2026-03-28",
  "acertos": 14,
  "total": 20,
  "banco_questoes": "TEC Concursos",
  "banca": "CESPE"
}
```

Endpoint `GET /baterias?aluno_id=me&limit=20`

**Frontend:**
Página `/caderno-questoes`:

Formulário de registro:
- Select hierárquico: Matéria → Módulo → Subtópico
- Input acertos (número)
- Input total (número, ≥ acertos)
- Percentual calculado automaticamente e exibido
- Select banco de questões (obrigatório):
  TEC Concursos, Qconcursos, Gran Cursos, Estratégia, CERS, Simulado Próprio, Outro
- Select banca (opcional):
  CESPE/CEBRASPE, FCC, FGV, VUNESP, AOCP, IDECAN, IBFC, QUADRIX, IADES, UPENET, Outra
- Input data (default hoje)
- Botão Salvar
- Após salvar: "Registrado! X% de acerto em [Subtópico]" + opção de registrar outro

Histórico (abaixo do formulário):
- Tabela: data | matéria | subtópico | acertos/total | % | banco | banca

**Verificar:**
- Registrar bateria → aparece no histórico
- Taxa de acerto calculada corretamente
- Dados aparecem nos gráficos do dashboard

**Arquivos:**
- CRIAR: `app/models/bateria_questoes.py`
- CRIAR/MODIFICAR: `app/routers/baterias.py`
- CRIAR: `frontend/src/pages/CadernoQuestoes.jsx`
- Criar migration Alembic

---

### V1-T07 — Implementar página de desempenho detalhado
⬜ PENDING

**Leia antes:** `docs/modulos/desempenho.md`

**Contexto:** Página com todos os gráficos e métricas detalhadas.
É aqui que o aluno entende profundamente seu desempenho.

**O que implementar:**

**Backend — endpoints:**
```
GET /desempenho/por-materia
  [{ materia, taxa_acerto, total_questoes, horas, subtopicos_dominados,
     subtopicos_criticos, evolucao_semanal: [{ semana, taxa }] }]

GET /desempenho/heatmap-subtopicos
  [{ materia, modulo, subtopico, taxa_acerto, total_questoes, status }]

GET /desempenho/volume-semanal
  Últimas 8 semanas: [{ semana, total_questoes, por_materia: {...} }]

GET /desempenho/consistencia
  Últimos 365 dias: [{ data, total_questoes, total_minutos }]

GET /desempenho/por-banca
  [{ banca, taxa_acerto, total_questoes }]

GET /desempenho/por-banco-questoes
  [{ banco, taxa_acerto, total_questoes }]
```

**Frontend — página `/desempenho`:**

Filtro global no topo: período (7d / 30d / 90d / tudo) e matéria

Bloco 1 — Radar de matérias (recharts RadarChart)
Bloco 2 — Mapa de calor de subtópicos (grid visual com cores)
Bloco 3 — Evolução temporal por matéria (recharts LineChart)
Bloco 4 — Volume semanal de questões (recharts BarChart empilhado)
Bloco 5 — Heatmap de consistência (calendário estilo GitHub)
Bloco 6 — Desempenho por banca (recharts BarChart horizontal)
Bloco 7 — Desempenho por banco de questões (recharts BarChart)

**Verificar:**
- Todos os gráficos carregam com dados reais
- Filtro de período funciona
- Mapa de calor mostra cores corretas por taxa de acerto

**Arquivos:**
- CRIAR/MODIFICAR: `app/routers/desempenho.py`
- MODIFICAR: `frontend/src/pages/Desempenho.jsx`

---

### V1-T08 — Bugs e melhorias de autenticação
⬜ PENDING

**Contexto:** Três bugs de autenticação identificados que precisam
ser corrigidos antes do beta.

**Bug 01 — Onboarding: "Erro ao salvar suas preferências"**
Verificar logs do Railway para o erro exato.
Testar POST /onboarding no /docs com os dados do formulário.
Verificar se todas as migrations foram aplicadas.

**Bug 02 — Usuário logado vai para /login**
O AuthContext não restaura o token antes do ProtectedRoute redirecionar.
Corrigir: enquanto loading === true, não redirecionar para nenhum lugar.

**Bug 03 — Cadastro incompleto + código de convite**
- Adicionar campo "Confirmar senha" com validação
- Adicionar botão mostrar/ocultar senha no cadastro e no login
- Validações: senha 8+ caracteres, email formato válido
- Implementar código de convite:
  - Campo obrigatório na tela de cadastro
  - Admin cria códigos no painel com limite de usos
  - Backend valida antes de criar a conta
  - Tabela CodigoConvite: codigo, limite_usos, usos_atuais, ativo

**Arquivos:**
- MODIFICAR: `frontend/src/pages/Login.jsx`
- MODIFICAR: `frontend/src/context/AuthContext.jsx`
- CRIAR: `app/models/codigo_convite.py`
- MODIFICAR: `app/routers/auth.py`
- Criar migration Alembic para CodigoConvite

---

### V1-T09 — Perfil do usuário
⬜ PENDING

**Contexto:** Não existe página de perfil. O aluno não consegue
trocar senha ou atualizar seus dados.

**Backend:**
- PATCH /auth/me — atualizar nome e email
- POST /auth/alterar-senha — validar senha atual, salvar nova

**Frontend — `/perfil`:**
- Seção dados pessoais: nome, email
- Seção alterar senha: atual + nova + confirmar
- Seção conta: área, data de cadastro (somente leitura)

**Arquivos:**
- CRIAR: `frontend/src/pages/Perfil.jsx`
- CRIAR/MODIFICAR: endpoints em `app/routers/auth.py`

---

## VOLTA 2 — Análise avançada
> Só iniciar após Volta 1 validada com usuários beta reais.

- V2-T01: Exportar relatório de desempenho em PDF
- V2-T02: Comparativo de período (semana vs semana, mês vs mês)
- V2-T03: Meta de questões semanal configurável pelo aluno
- V2-T04: Filtro por banca em todos os gráficos
- V2-T05: Histórico completo por subtópico (evolução detalhada)
- V2-T06: Confirmação de email e recuperação de senha

---

## VOLTA 3 — IA e conteúdo
> Só iniciar após Volta 2 validada.

- V3-T01: Análise de padrão de erro via IA ("você erra questões sobre X")
- V3-T02: Sugestão inteligente de revisão com justificativa textual
- V3-T03: PDF explicativo por subtópico (resumo de apoio ao estudo)
- V3-T04: Sugestão de vídeos por subtópico

---

## VOLTA 4 — Expansão
> Produto validado, crescimento planejado.

- V4-T01: Áreas militares (EAOF-COM, EAOF-SVM, CFOE-COM)
- V4-T02: Legislação Tributária pós-edital
- V4-T03: Monetização (planos e gateway)
- V4-T04: Backup PostgreSQL → Google Drive
- V4-T05: Sentry + auditoria admin

---

## Rotas React — Volta 1

| Rota | Página | Role |
|---|---|---|
| /login | Login | público |
| /onboarding | Onboarding | autenticado sem área |
| / | Dashboard (análise) | estudante |
| /registrar-estudo | RegistrarEstudo | estudante |
| /caderno-questoes | CadernoQuestoes | estudante |
| /desempenho | Desempenho | estudante |
| /perfil | Perfil | estudante |
| /admin | AdminDashboard | administrador |
| /admin/topicos | AdminTopicos | administrador |
| /admin/usuarios | AdminUsuarios | administrador |
| /admin/convites | AdminConvites | administrador |

