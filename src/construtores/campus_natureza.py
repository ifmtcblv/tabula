"""Constrói o dataset de campus × natureza de participação."""

import pandas as pd


def construir(df: pd.DataFrame) -> pd.DataFrame:
    """
    Gera o dataset combinado de campus e natureza de participação.

    Args:
        df: O DataFrame pré-processado.

    Returns:
        O DataFrame do dataset.
    """
    return (
        df.groupby(["campus", "natureza_participacao"])
        .size()
        .reset_index(name="qtd")
    )
