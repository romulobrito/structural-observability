#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Textos da interface em portugues brasileiro (linguagem simples)."""

from __future__ import annotations

APP_TITLE = "Avaliação de medidas do processo"
APP_SUBTITLE = (
    "Verifique o que dá para calcular com os medidores instalados "
    "e quais medidores faltam para calcular tudo."
)

TAB_DIAGNOSTIC = "Classificação (avaliar medidas atuais)"
TAB_REPAIR = "Instrumentação mínima (o que falta medir)"

CRITERION_LINE = (
    "Sucesso: todas as grandezas do modelo passam a ser calculáveis "
    "com as medidas escolhidas."
)

PRESET_LABEL = "Cenário"
PRESET_IDEAL = "URS ideal (26 medidores)"
PRESET_REAL = "URS real (22 medidores)"
PRESET_REPAIR = "URS real + sugestão de medidores (PDF)"

RUN_DIAGNOSTIC = "Avaliar medidas"
RUN_REPAIR = "Buscar medidores faltantes"

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
SECTION_REPAIR_CANDIDATES = "Medidores candidatos à instalação"

COL_TAG = "Grandeza"
COL_STATUS = "Situação"
COL_OPTION = "Opção"
COL_INSTALL = "Medidores a instalar"
COL_RESULT = "Resultado"
COL_TOTAL_MEASURED = "Total de medidores"
COL_INDETERMINATE = "Indetermináveis"
COL_OPEN_TEARS = "Pontos abertos"

DOWNLOAD_ZIP = "Baixar relatório completo (ZIP)"
ADVANCED_MODE = "Mostrar detalhes técnicos"
UPLOAD_YAML = "Enviar arquivo de cenário (YAML)"
YAML_EDITOR = "Editar cenário (YAML)"

SOLVER_CONFIRMED = "Resultado confirmado"
SOLVER_OTHER = "Resultado com ressalvas (ver detalhes técnicos)"

YES = "Sim"
NO = "Não"
COMPUTES_ALL_QUESTION = "Calcula tudo?"

ABOUT_TITLE = "Sobre"
ABOUT_TEXT = (
    "Esta ferramenta avalia balanços de massa com base nas medidas instaladas. "
    "Não substitui validação algébrica nem otimização MILP global de sensores. "
    "Os arquivos exportados contêm detalhes técnicos para auditoria."
)

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
SIDEBAR_TIME_LIMIT = "Tempo máximo (s)"
TECH_DETAILS_HEADER = "Detalhes técnicos"

SPINNER_DIAGNOSTIC = "Analisando medidas..."
SPINNER_REPAIR = "Buscando medidores faltantes..."

REPAIR_BASELINE_INFO = (
    "Situação de partida: URS real com 22 medidores ({preset})."
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
