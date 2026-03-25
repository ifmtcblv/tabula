"""Constrói o dataset de natureza de participação × situação do aluno."""

import pandas as pd


def construir(df: pd.DataFrame) -> pd.DataFrame:
    """
    Gera o dataset combinado de natureza de participação e situação simplificada.

    Args:
        df: O DataFrame pré-processado.

    Returns:
        O DataFrame do dataset.
    """
    return (
        df.groupby(["natureza_participacao", "status_simplificado"])
        .size()
        .reset_index(name="qtd")
    )
