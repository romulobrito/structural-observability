#!/usr/bin/env python3
"""Simple Portuguese UI strings (no technical jargon on the main screen)."""

from __future__ import annotations

APP_TITLE = "Avaliacao de medidas do processo"
APP_SUBTITLE = (
    "Verifique o que da para calcular com os medidores instalados "
    "e quais medidores faltam para calcular tudo."
)

TAB_DIAGNOSTIC = "Avaliar medidas atuais"
TAB_REPAIR = "O que falta medir?"

CRITERION_LINE = (
    "Sucesso: todas as grandezas do modelo passam a ser calculaveis "
    "com as medidas escolhidas."
)

PRESET_LABEL = "Cenario"
PRESET_IDEAL = "URS ideal (26 medidores)"
PRESET_REAL = "URS real (22 medidores)"
PRESET_REPAIR = "URS real + sugestao de medidores (PDF)"

RUN_DIAGNOSTIC = "Avaliar medidas"
RUN_REPAIR = "Buscar medidores faltantes"

CARD_CALCULABLE = "Calculavel hoje"
CARD_NOT_CALCULABLE = "Ainda nao calculavel"
CARD_MEASURED = "Medidores instalados"
CARD_TO_ADD = "Medidores a mais (minimo)"
CARD_TOTAL_AFTER = "Total apos correcao"

SECTION_CALCULATED = "O que ja calculamos"
SECTION_NOT_CALCULATED = "O que ainda nao da para calcular"
SECTION_OPEN_BALANCES = "Pontos em que o balanco ficou aberto"
SECTION_INSTALL_OPTIONS = "Opcoes de instalacao"

COL_TAG = "Grandeza"
COL_STATUS = "Situacao"
COL_OPTION = "Opcao"
COL_INSTALL = "Medidores a instalar"
COL_RESULT = "Resultado"

DOWNLOAD_ZIP = "Baixar relatorio completo (ZIP)"
ADVANCED_MODE = "Mostrar detalhes tecnicos"
UPLOAD_YAML = "Enviar arquivo de cenario (YAML)"
YAML_EDITOR = "Editar cenario (YAML)"

SOLVER_CONFIRMED = "Resultado confirmado"
SOLVER_OTHER = "Resultado com ressalvas (ver detalhes tecnicos)"

YES = "Sim"
NO = "Nao"
COMPUTES_ALL_QUESTION = "Calcula tudo?"

ABOUT_TITLE = "Sobre"
ABOUT_TEXT = (
    "Esta ferramenta avalia balancos de massa com base nas medidas instaladas. "
    "Nao substitui validacao algebrica nem otimizacao MILP global de sensores. "
    "Os arquivos exportados contem detalhes tecnicos para auditoria."
)

ERROR_INVALID_CASE = "Nao foi possivel ler o cenario. Verifique o arquivo YAML."
ERROR_RUN_FAILED = "A analise nao pode ser concluida."

TECH_C_CL = "C_cl (cobertura fechada)"
TECH_C_EXT = "C_ext (alcance externo)"
TECH_C_DIR = "C_dir (cobertura direta)"
TECH_SOLVER = "Status do solver"

VAR_STATUS_MEASURED = "Ja medido"
VAR_STATUS_KNOWN = "Parametro conhecido"
VAR_STATUS_DIRECT = "Calculado direto"
VAR_STATUS_CLOSED_LOOP = "Calculado pelo balanco"
VAR_STATUS_CLOSED_TEAR = "Fechado no balanco"
VAR_STATUS_CONDITIONED = "Calculado com ponto extra"
VAR_STATUS_CLOSED_EXT = "Fechado com medida externa"
VAR_STATUS_OPEN_TEAR = "Precisa de medida extra"
VAR_STATUS_NOT_CALCULABLE = "Nao calculavel"

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
