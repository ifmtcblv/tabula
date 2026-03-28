"""Constrói o dataset de etnia × turno."""

import pandas as pd


def construir(df: pd.DataFrame) -> pd.DataFrame:
    """
    Gera o dataset cruzado de etnia/raça e turno.

    Args:
        df (pd.DataFrame): O DataFrame pré-processado.

    Returns:
        pd.DataFrame: O DataFrame do dataset.
    """
    df = df[df["natureza_participacao"] == "Presencial"].copy()

    return df.groupby(["etnia_raca", "turno"]).size().reset_index(name="qtd")
