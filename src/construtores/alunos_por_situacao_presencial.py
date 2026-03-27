"""Constrói o dataset de alunos por situação (apenas presencial)."""

import pandas as pd


def construir(df: pd.DataFrame, coluna_status: str) -> pd.DataFrame:
    """
    Constrói o dataset de alunos por situação para alunos presenciais.

    Args:
        df: O DataFrame pré-processado.
        coluna_status: A coluna de status a ser usada.

    Returns:
        O DataFrame do dataset com colunas Situacao e qtd.
    """
    df_presencial = df[df["natureza_participacao"] == "Presencial"].copy()

    if df_presencial.empty:
        return pd.DataFrame(columns=["Situacao", "qtd"])

    series = df_presencial[coluna_status].fillna("Não informado")
    agrupado = (
        series.groupby(series)
        .size()
        .reset_index(name="qtd")
        .sort_values("qtd", ascending=False)
    )
    agrupado.columns = ["Situacao", "qtd"]
    return agrupado
