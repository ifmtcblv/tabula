"""Constrói o dataset de distribuição de alunos por tempo de permanência na instituição."""

import pandas as pd

# Alunos ainda matriculados (exclui quem já saiu definitivamente)
_STATUS_MATRICULADOS = {"Ativo", "Trancado", "Outros"}

# Ordem das faixas de tempo (usado para ordenação categórica)
ORDEM_FAIXAS = [
    "Menos de 6 meses",
    "6 a 12 meses",
    "1 a 2 anos",
    "2 a 3 anos",
    "3 a 4 anos",
    "Mais de 4 anos",
]


def _faixa_tempo(meses: float) -> str:
    if meses < 6:
        return "Menos de 6 meses"
    if meses < 12:
        return "6 a 12 meses"
    if meses < 24:
        return "1 a 2 anos"
    if meses < 36:
        return "2 a 3 anos"
    if meses < 48:
        return "3 a 4 anos"
    return "Mais de 4 anos"


def construir(df: pd.DataFrame) -> pd.DataFrame:
    """
    Gera o dataset de alunos atualmente matriculados por faixa de tempo na instituição.

    Usa o campo tempo_curso_meses (já calculado no pré-processamento) apenas para alunos
    ainda matriculados — exclui Concluído e Evasão/Cancelado. Isso garante que o gráfico
    seja uma leitura honesta do snapshot atual: "há quanto tempo esses alunos estão aqui?"

    Args:
        df: O DataFrame pré-processado.

    Returns:
        O DataFrame com colunas faixa_tempo, natureza_participacao e qtd.
    """
    matriculados = df[df["status_simplificado"].isin(_STATUS_MATRICULADOS)].copy()
    matriculados = matriculados[matriculados["tempo_curso_meses"].notna()]

    matriculados["faixa_tempo"] = matriculados["tempo_curso_meses"].apply(_faixa_tempo)

    agrupado = (
        matriculados.groupby(["faixa_tempo", "natureza_participacao"])
        .size()
        .reset_index(name="qtd")
    )

    agrupado["faixa_tempo"] = pd.Categorical(
        agrupado["faixa_tempo"], categories=ORDEM_FAIXAS, ordered=True
    )
    return agrupado.sort_values(["faixa_tempo", "natureza_participacao"]).reset_index(drop=True)
