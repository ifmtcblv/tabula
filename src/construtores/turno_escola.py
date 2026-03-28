"""Constrói o dataset de turno × tipo de escola."""

import pandas as pd


def construir(df: pd.DataFrame) -> pd.DataFrame:
    """
    Gera o dataset cruzado de turno e tipo de escola de origem.

    Args:
        df (pd.DataFrame): O DataFrame pré-processado.

    Returns:
        pd.DataFrame: O DataFrame do dataset.
    """
    df = df[df["natureza_participacao"] == "Presencial"].copy()

    return df.groupby(["turno", "tipo_escola_origem"]).size().reset_index(name="qtd")
