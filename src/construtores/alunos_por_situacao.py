"""Constrói o dataset de alunos por situação."""

import pandas as pd


def construir(df: pd.DataFrame, coluna_status: str) -> pd.DataFrame:
    """
    Constrói o dataset de alunos por situação.

    Args:
        df: O DataFrame pré-processado.
        coluna_status: A coluna de status a ser usada.

    Returns:
        O DataFrame do dataset com colunas Situacao e qtd.
    """
    series = df[coluna_status].fillna("Não informado")
    agrupado = (
        series.groupby(series)
        .size()
        .reset_index(name="qtd")
        .sort_values("qtd", ascending=False)
        .rename(columns={coluna_status: "Situacao"})
    )
    agrupado = agrupado.rename(columns={series.name: "Situacao"})
    agrupado.columns = ["Situacao", "qtd"]
    return agrupado
