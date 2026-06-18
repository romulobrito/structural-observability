#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Textos da interface em portugues brasileiro (linguagem simples)."""

from __future__ import annotations

APP_TITLE = "Avaliação de medidas do processo"
APP_SUBTITLE = (
    "Veja o que dá para calcular com os medidores instalados "
    "e descubra quais medidores faltam para calcular todas as grandezas."
)

# Abas (titulos curtos; detalhes em TAB_GUIDE e TAB_INTRO_*)
TAB_DIAGNOSTIC = "Classificação"
TAB_PLACEMENT = "Inst. mínima (automática)"
TAB_REPAIR = "Inst. mínima (lista fixa)"
TAB_MILP = "Regras MILP (URS)"

TAB_GUIDE_TITLE = "Qual aba usar?"
TAB_GUIDE = (
    "**1. Classificação** — Você já tem uma lista de medidores e quer saber "
    "o que o processo consegue calcular hoje (sem instalar nada novo).\n\n"
    "**2. Inst. mínima (automática)** — O sistema descobre sozinho onde medir "
    "a mais para calcular tudo. Não precisa informar candidatos.\n\n"
    "**3. Inst. mínima (lista fixa)** — Você informa quais medidores podem ser "
    "instalados (ex.: sensores falhos) e o sistema busca o menor acréscimo.\n\n"
    "**4. Regras MILP (URS)** — Otimização pelas regras de engenharia do "
    "documento URS (F+R, permeados, limites por equação). Critério diferente "
    "da análise estrutural das abas anteriores."
)

TAB_INTRO_DIAGNOSTIC = (
    "**Objetivo:** avaliar a instrumentação **atual**.\n\n"
    "**Entrada:** equações do modelo + lista de medidores já instalados.\n\n"
    "**Saída:** quantas grandezas são calculáveis, quais ficam indetermináveis "
    "e onde o balanço ficou aberto.\n\n"
    "**Quando usar:** primeiro passo — entender a situação antes de propor novos medidores."
)
TAB_INTRO_PLACEMENT = (
    "**Objetivo:** encontrar o **menor número de medidores novos** para calcular "
    "**todas** as grandezas do modelo.\n\n"
    "**Entrada:** equações + medidores base (opcional; vazio = começa do zero).\n\n"
    "**Como funciona:** o algoritmo identifica automaticamente quais variáveis "
    "ainda não são calculáveis e testa combinações até achar a solução mínima.\n\n"
    "**Atenção:** pode haver várias opções equivalentes (ex.: pares Ra ou pares FC). "
    "Modelos grandes (busca do zero) podem demorar ou não encontrar solução."
)
TAB_INTRO_REPAIR = (
    "**Objetivo:** mesmo que a aba automática, mas **restrito a uma lista de candidatos** "
    "que você define no YAML.\n\n"
    "**Entrada:** equações + medidores base + lista de candidatos permitidos.\n\n"
    "**Quando usar:** quando já sabe **onde pode** instalar (ex.: reinstalar sensores "
    "falhos R, Ra_C, Ra_D, Ra_E do cenário PDF).\n\n"
    "**Diferença da automática:** aqui o resultado depende da lista informada; "
    "na automática o sistema monta a lista sozinho."
)
TAB_INTRO_MILP = (
    "**Objetivo:** otimizar sensores pelas **regras de engenharia MILP** do documento URS, "
    "não pela observabilidade estrutural (tearing).\n\n"
    "**Modos:** global (menor conjunto pelas regras), verificar (auditar conjunto fixo).\n\n"
    "**Importante:** o conjunto ótimo MILP (ex.: 11 sensores) **não garante** calcular "
    "todas as 43 grandezas no tearing. Use a comparação estrutural no resultado."
)

MILP_WARNING = (
    "Esta aba usa **regras de engenharia MILP** (modelo y/z do documento URS). "
    "Os resultados podem diferir das abas de instrumentação mínima (análise estrutural). "
    "Use **MILP global** para propor instrumentação pelas regras; "
    "use **verificar** para auditar um conjunto fixo de medidores."
)

MILP_MODE_GLOBAL = "Otimização global"
MILP_MODE_VERIFY = "Auditoria (conjunto fixo)"
MILP_MODE_REPAIR = "Reparo com base fixa"

MILP_HINT_GLOBAL = (
    "**O que faz:** busca o menor número de medidores que satisfaz todas as regras MILP, "
    "partindo do zero.\n\n"
    "**Quando usar:** para propor um novo projeto de instrumentação pelas regras de engenharia."
)
MILP_HINT_VERIFY_IDEAL = (
    "**O que faz:** verifica se o conjunto **fixo** de 26 medidores do PDF (Seção 4.1) "
    "cumpre as regras MILP.\n\n"
    "**Resultado esperado:** inviável — o PDF foi desenhado para tearing, não para MILP. "
    "A lista de conflitos explica o porquê."
)
MILP_HINT_VERIFY_REAL = (
    "**O que faz:** verifica se os 22 medidores reais do PDF (Seção 4.2) cumprem as regras MILP.\n\n"
    "**Resultado esperado:** inviável — faltam permeados, F e outras regras. "
    "Use a aba de instrumentação mínima para saber o que falta no tearing."
)
CRITERION_LINE = (
    "Critério de sucesso (abas de classificação e instrumentação mínima): "
    "todas as grandezas do modelo passam a ser calculáveis com as medidas escolhidas."
)

PRESET_LABEL = "Cenário"
HELP_PRESET = (
    "Conjunto pré-configurado de equações e medidores. "
    "No modo avançado você pode enviar ou editar seu próprio YAML."
)
PRESET_IDEAL = "URS ideal — 26 medidores (PDF Seção 4.1)"
PRESET_REAL = "URS real — 22 medidores (PDF Seção 4.2)"
PRESET_REPAIR = "URS real — reparo com candidatos falhos (PDF)"
PRESET_MILP_GLOBAL = "MILP global — menor conjunto pelas regras URS"
PRESET_MILP_VERIFY_REAL = "MILP verificar — 22 medidores reais do PDF"
PRESET_MILP_VERIFY_IDEAL = "MILP verificar — 26 medidores ideais do PDF"
PRESET_PLACEMENT_REAL = "URS real — busca automática a partir de 22 medidores"
PRESET_PLACEMENT_ZERO = "Busca automática do zero (sem medidores base)"

DIAG_HINT_IDEAL = (
    "**26 medidores** do cenário ideal do PDF. "
    "Esperado: calcula **todas** as 43 grandezas."
)
DIAG_HINT_REAL = (
    "**22 medidores** do cenário real do PDF (4 sensores falhos). "
    "Esperado: calcula **34 de 43** grandezas — faltam 9."
)

DIAG_PRESET_HINTS: dict[str, str] = {
    PRESET_IDEAL: DIAG_HINT_IDEAL,
    PRESET_REAL: DIAG_HINT_REAL,
}

REPAIR_HINT = (
    "**Lista fixa de candidatos:** R, Ra_C, Ra_D, Ra_E (sensores falhos do PDF). "
    "O sistema busca o **menor número** deles a reinstalar para calcular tudo. "
    "Esperado: instalar **2** entre {Ra_C, Ra_D, Ra_E}."
)

MILP_PRESET_HINTS: dict[str, str] = {
    PRESET_MILP_GLOBAL: MILP_HINT_GLOBAL,
    PRESET_MILP_VERIFY_IDEAL: MILP_HINT_VERIFY_IDEAL,
    PRESET_MILP_VERIFY_REAL: MILP_HINT_VERIFY_REAL,
}

RUN_DIAGNOSTIC = "Avaliar medidas"
RUN_REPAIR = "Buscar medidores faltantes"
RUN_PLACEMENT = "Buscar instrumentação mínima"
RUN_MILP = "Executar MILP"

CARD_CALCULABLE = "Calculável hoje"
CARD_NOT_CALCULABLE = "Ainda não calculável"
CARD_MEASURED = "Medidores instalados"
CARD_INFERRED = "Calculadas (inferidas)"
CARD_INDETERMINATE = "Indetermináveis"
CARD_OPEN_TEARS = "Pontos abertos"
CARD_EXTERNAL_REACH = "Alcance com pontos críticos"
CARD_DIRECT = "Cobertura direta"
CARD_TO_ADD = "Medidores a mais (mínimo)"
CARD_TOTAL_AFTER = "Total após correção"
CARD_GRANDEZAS = "Grandezas no modelo"
CARD_MILP_SENSORS = "Medidores MILP (y=1)"
CARD_MILP_INFERRED = "Inferidas MILP (z=1)"
CARD_MILP_REDUNDANCY = "Custo de redundância"
CARD_MILP_TEARING = "C_cl após auditoria (tearing)"

HELP_MILP_SENSORS = (
    "Quantidade de medidores com y=1 na solução MILP (instalados diretamente)."
)
HELP_MILP_INFERRED = (
    "Grandezas com z=1: calculadas indiretamente a partir de outras medidas "
    "na mesma equação, sem medidor próprio."
)
HELP_MILP_REDUNDANCY = (
    "Soma, por equação, do excesso de medidores acima de 2. "
    "Indica redundância nas regras MILP."
)
HELP_MILP_TEARING = (
    "Após o MILP, roda a análise estrutural (tearing) no conjunto y=1 "
    "para comparar C_cl com o paradigma CP-SAT. Os dois critérios diferem."
)
HELP_MILP_MODE = "Tipo de pergunta que este cenário MILP responde."
HELP_MILP_STATUS = "Resultado do solver MILP (SCIP/CBC) para este modo."

SECTION_MILP_ADDITIONS = "Medidores adicionados (reparo MILP)"
SECTION_MILP_MODE = "Modo MILP"

# Tooltips (hover) dos KPIs -- linguagem simples
HELP_COMPUTES_ALL = (
    "Sim quando todas as grandezas do modelo podem ser calculadas "
    "com as medidas escolhidas, sem lacunas no balanço."
)
HELP_CALCULABLE = (
    "Grandezas que o processo consegue obter hoje usando apenas "
    "os medidores instalados e os balanços fechados."
)
HELP_INFERRED = (
    "Grandezas não medidas diretamente, mas obtidas por cálculo "
    "a partir dos medidores e das equações do modelo."
)
HELP_INDETERMINATE = (
    "Grandezas que não podem ser calculadas com as medidas atuais: "
    "falta informação em algum ponto do balanço."
)
HELP_MEASURED = (
    "Quantidade de grandezas que possuem medidor instalado "
    "no cenário analisado."
)
HELP_NOT_CALCULABLE = (
    "Grandezas que ainda ficam fora do que conseguimos calcular "
    "com a instrumentação atual."
)
HELP_OPEN_TEARS = (
    "Pontos em que o balanço de massa ficou aberto porque "
    "falta medida em um fluxo crítico."
)
HELP_EXTERNAL_REACH = (
    "Quantas grandezas seriam calculáveis se medíssemos os pontos "
    "abertos (cenário hipotético de reparo parcial)."
)
HELP_DIRECT = (
    "Grandezas obtidas diretamente das medidas ou de parâmetros "
    "conhecidos, sem cálculo indireto pelo balanço."
)
HELP_TO_ADD = (
    "Menor número de medidores novos necessários para passar a "
    "calcular todas as grandezas do modelo."
)
HELP_TOTAL_AFTER = (
    "Total de medidores após instalar a quantidade mínima indicada "
    "(medidores atuais + novos)."
)
HELP_GRANDEZAS = (
    "Número total de variáveis (fluxos e grandezas) "
    "representadas no modelo de balanço."
)
HELP_TECH_C_CL = (
    "Cobertura fechada (C_cl): grandezas calculáveis sem depender "
    "de medidas externas em pontos abertos."
)
HELP_TECH_C_EXT = (
    "Alcance externo (C_ext): grandezas calculáveis se os pontos "
    "abertos do balanço forem fornecidos externamente."
)
HELP_TECH_C_DIR = (
    "Cobertura direta (C_dir): grandezas ligadas imediatamente "
    "às medidas ou constantes conhecidas."
)
HELP_TECH_SOLVER = "Resultado do otimizador estrutural (CP-SAT)."
HELP_TECH_OPEN_TEARS = "Variáveis selecionadas como tear aberto no modelo."
HELP_TECH_INDETERMINATE = (
    "Grandezas efetivamente indetermináveis após a análise estrutural."
)
HELP_TECH_EQUATIONS = "Número de equações de balanço no caso analisado."

SECTION_CALCULATED = "O que já calculamos"
SECTION_NOT_CALCULATED = "O que ainda não dá para calcular"
SECTION_OPEN_BALANCES = "Pontos em que o balanço ficou aberto"
SECTION_INFERRED = "Grandezas inferidas (calculadas a partir das medidas)"
SECTION_INDETERMINATE = "Grandezas indetermináveis"
SECTION_MEASURED = "Grandezas já medidas"
SECTION_BY_STATUS = "Detalhamento por situação"
SECTION_VARIABLE_TABLE = "Todas as grandezas do modelo"
SECTION_INSTALL_OPTIONS = "Opções de instalação"
SECTION_REPAIR_BEFORE = "Situação antes de instalar novos medidores"
SECTION_REPAIR_CANDIDATES = "Medidores candidatos (lista informada no YAML)"
SECTION_AUTO_POOL = "Variáveis analisadas na busca automática"
HELP_REPAIR_CANDIDATES = (
    "Somente estes medidores podem ser instalados. "
    "Definidos em analysis.repair.candidates no YAML."
)
HELP_AUTO_POOL = (
    "Pool montado automaticamente a partir das grandezas indetermináveis. "
    "O algoritmo testa combinações deste conjunto."
)
SECTION_MILP_MEASURED = "Medidores instalados pelo MILP"
SECTION_MILP_INFERRED = "Grandezas inferidas pelo MILP"
SECTION_MILP_CONFLICTS = "Conflitos com as regras MILP"
SECTION_MILP_TEARING_AUDIT = "Comparação com análise estrutural (tearing)"

COL_TAG = "Grandeza"
COL_STATUS = "Situação"
COL_OPTION = "Opção"
COL_INSTALL = "Medidores a instalar"
COL_RESULT = "Resultado"
COL_TOTAL_MEASURED = "Total de medidores"
COL_INDETERMINATE = "Indetermináveis"
COL_OPEN_TEARS = "Pontos abertos"

DOWNLOAD_ZIP = "Baixar relatório completo (ZIP)"
HELP_DOWNLOAD_ZIP = "Exporta YAML, JSON e CSV com detalhes técnicos para auditoria."
ADVANCED_MODE = "Modo avançado (editar YAML)"
HELP_ADVANCED = (
    "Permite enviar ou editar o arquivo de cenário (YAML) e ver métricas técnicas "
    "como C_cl, C_ext e status do solver CP-SAT."
)
UPLOAD_YAML = "Enviar arquivo de cenário (YAML)"
HELP_UPLOAD_YAML = (
    "Arquivo com equações, medidores instalados e objetivo da análise. "
    "Substitui o cenário pré-configurado selecionado."
)
YAML_EDITOR = "Editar cenário (YAML)"
HELP_YAML_EDITOR = "Edite o cenário antes de executar. Validação ao clicar no botão de execução."

SOLVER_CONFIRMED = "Resultado confirmado"
SOLVER_OTHER = "Resultado com ressalvas (ver detalhes técnicos)"

YES = "Sim"
NO = "Não"
COMPUTES_ALL_QUESTION = "Calcula tudo?"

ABOUT_TITLE = "Sobre"
ABOUT_TEXT = (
    "Esta ferramenta oferece três paradigmas complementares:\n\n"
    "1) **Classificação (CP-SAT tearing):** avalia o que é calculável "
    "estruturalmente com as medidas atuais.\n\n"
    "2) **Instrumentação mínima (automática / candidatos):** descobre o menor "
    "acréscimo de medidores para cobertura fechada C_cl = |V|, com busca "
    "automática de candidatos ou lista manual.\n\n"
    "3) **Colocação MILP (y/z):** otimiza sensores sob regras de engenharia do "
    "documento URS (F+R, permeados, limites por equação). O conjunto ótimo MILP "
    "pode diferir do tearing.\n\n"
    "Nenhum dos modos substitui validação algébrica completa. "
    "Os arquivos exportados contêm detalhes técnicos para auditoria."
)

MILP_STATUS_OPTIMAL = "Solução ótima MILP encontrada"
MILP_STATUS_FEASIBLE = "Conjunto viável nas regras MILP"
MILP_STATUS_INFEASIBLE = "Conjunto inviável nas regras MILP"
MILP_STATUS_NOT_OPTIMAL = "Solver sem solução ótima (tempo ou limites)"

ERROR_INVALID_CASE = "Não foi possível ler o cenário. Verifique o arquivo YAML."
ERROR_RUN_FAILED = "A análise não pode ser concluída."

TECH_C_CL = "C_cl (cobertura fechada)"
TECH_C_EXT = "C_ext (alcance externo)"
TECH_C_DIR = "C_dir (cobertura direta)"
TECH_SOLVER = "Status do solver"
TECH_OPEN_TEARS = "Tears abertos"
TECH_INDETERMINATE = "Indetermináveis efetivas"
TECH_EQUATIONS = "Equações no modelo"

SIDEBAR_HEADER = "Configuração"
SIDEBAR_TIME_LIMIT = "Tempo máximo por análise (s)"
HELP_TIME_LIMIT = (
    "Limite de tempo do solver CP-SAT em cada classificação. "
    "Aumente se a análise retornar resultado com ressalvas."
)
HELP_RUN_DIAGNOSTIC = "Executa a classificação estrutural com os medidores do cenário."
HELP_RUN_REPAIR = "Busca o menor acréscimo entre os candidatos informados no YAML."
HELP_RUN_PLACEMENT = (
    "Descobre automaticamente onde medir. Pode levar alguns segundos "
    "(mais combinações = mais tempo)."
)
HELP_RUN_MILP = "Resolve o modelo MILP com as regras de engenharia URS."
TECH_DETAILS_HEADER = "Detalhes técnicos"

SPINNER_DIAGNOSTIC = "Analisando medidas..."
SPINNER_REPAIR = "Buscando medidores faltantes..."
SPINNER_PLACEMENT = "Buscando instrumentação mínima (pode demorar)..."
SPINNER_MILP = "Resolvendo MILP..."

REPAIR_BASELINE_INFO = (
    "Reparo com **lista fixa de candidatos** (sensores falhos do PDF). "
    "Para descobrir candidatos automaticamente, use a aba **Inst. mínima (automática)**."
)

PLACEMENT_INFO = (
    "Busca **automática**: o sistema identifica quais variáveis ainda não são "
    "calculáveis e encontra o menor número de medidores novos para calcular tudo. "
    "Você **não precisa** informar candidatos."
)
PLACEMENT_HINT_REAL = (
    "**Partida:** 22 medidores reais do PDF (Seção 4.2).\n\n"
    "**Esperado:** instalar **2 medidores** a mais (várias combinações possíveis, "
    "incluindo pares entre Ra_C, Ra_D, Ra_E).\n\n"
    "**Tempo:** cerca de 30–60 segundos."
)
PLACEMENT_HINT_ZERO = (
    "**Partida:** nenhum medidor instalado.\n\n"
    "**Limitação:** modelos grandes exigem muitas combinações; "
    "a busca pode não encontrar solução ou demorar muito. "
    "Prefira partir de uma base conhecida (cenário URS real)."
)

VAR_STATUS_MEASURED = "Já medido"
VAR_STATUS_KNOWN = "Parâmetro conhecido"
VAR_STATUS_DIRECT = "Calculado direto"
VAR_STATUS_CLOSED_LOOP = "Calculado pelo balanço"
VAR_STATUS_CLOSED_TEAR = "Fechado no balanço"
VAR_STATUS_CONDITIONED = "Calculado com ponto extra"
VAR_STATUS_CLOSED_EXT = "Fechado com medida externa"
VAR_STATUS_OPEN_TEAR = "Precisa de medida extra"
VAR_STATUS_NOT_CALCULABLE = "Não calculável"

VAR_STATUS_BY_CLASS: dict[str, str] = {
    "measured_sensor": VAR_STATUS_MEASURED,
    "known_constant": VAR_STATUS_KNOWN,
    "inferred_direct": VAR_STATUS_DIRECT,
    "inferred_closed_loop": VAR_STATUS_CLOSED_LOOP,
    "closed_tear": VAR_STATUS_CLOSED_TEAR,
    "inferred_conditioned_open_tear": VAR_STATUS_CONDITIONED,
    "closed_tear_external_dependency": VAR_STATUS_CLOSED_EXT,
    "open_tear": VAR_STATUS_OPEN_TEAR,
    "pure_indeterminate": VAR_STATUS_NOT_CALCULABLE,
}
