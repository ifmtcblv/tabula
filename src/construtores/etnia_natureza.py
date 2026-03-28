"""Constrói o dataset de etnia/raça por natureza de participação."""

import pandas as pd


def construir(df: pd.DataFrame) -> pd.DataFrame:
    """
    Gera o dataset combinado de etnia/raça e natureza de participação.

    Args:
        df (pd.DataFrame): O DataFrame pré-processado.

    Returns:
        pd.DataFrame: O DataFrame do dataset.
    """
    return (
        df.groupby(["natureza_participacao", "etnia_raca"])
        .size()
        .reset_index(name="qtd")
    )
