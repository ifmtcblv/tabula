"""Constrói o dataset de evolução temporal de matrículas por natureza de participação."""

import pandas as pd


def construir(df: pd.DataFrame) -> pd.DataFrame:
    """
    Gera o dataset de quantidade de alunos por ano de ingresso e natureza de participação.

    Args:
        df: O DataFrame pré-processado.

    Returns:
        O DataFrame do dataset com colunas coorte_ano, natureza_participacao e qtd.
    """
    dados = df.dropna(subset=["coorte_ano", "natureza_participacao"])
    dados = dados[dados["coorte_ano"].notna() & dados["natureza_participacao"].notna()]
    return (
        dados.groupby(["coorte_ano", "natureza_participacao"])
        .size()
        .reset_index(name="qtd")
        .sort_values("coorte_ano")
    )
