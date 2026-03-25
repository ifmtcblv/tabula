"""Constrói o dataset de natureza de participação × turno."""

import pandas as pd


def construir(df: pd.DataFrame) -> pd.DataFrame:
    """
    Gera o dataset combinado de natureza de participação e turno.

    Args:
        df: O DataFrame pré-processado.

    Returns:
        O DataFrame do dataset.
    """
    return (
        df.groupby(["natureza_participacao", "turno"])
        .size()
        .reset_index(name="qtd")
    )
