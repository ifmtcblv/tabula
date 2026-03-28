"""Constrói o dataset de transporte × situação."""

import pandas as pd


def construir(df: pd.DataFrame) -> pd.DataFrame:
    """
    Gera o dataset cruzado de transporte e situação.

    Args:
        df (pd.DataFrame): O DataFrame pré-processado.

    Returns:
        pd.DataFrame: O DataFrame do dataset com colunas transporte, status_simplificado e qtd.
    """
    df = df[df["natureza_participacao"] == "Presencial"].copy()

    df["transporte_combinado"] = (
        df["transporte_tipo"].fillna("Não informado")
        + " - "
        + df["transporte_publico"].fillna("Não informado")
    )
    df["transporte_combinado"] = df["transporte_combinado"].replace(
        "Não informado - Não informado", "Não informado"
    )

    return (
        df.groupby(["transporte_combinado", "status_simplificado"])
        .size()
        .reset_index(name="qtd")
    )
