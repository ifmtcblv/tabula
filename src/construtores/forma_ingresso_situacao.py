"""Constrói o dataset de forma de ingresso × situação."""

import pandas as pd


def construir(df: pd.DataFrame) -> pd.DataFrame:
    """
    Gera o dataset cruzado de forma de ingresso e situação.

    Args:
        df (pd.DataFrame): O DataFrame pré-processado.

    Returns:
        pd.DataFrame: O DataFrame do dataset.
    """
    df = df[df["natureza_participacao"] == "Presencial"].copy()

    return (
        df.groupby(["forma_ingresso", "status_simplificado"])
        .size()
        .reset_index(name="qtd")
    )
