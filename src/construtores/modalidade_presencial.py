"""Constrói o dataset de modalidade (apenas presencial)."""

import pandas as pd

from grafico_utils import contar_categoria_simples


def construir(df: pd.DataFrame) -> pd.DataFrame:
    """
    Constrói o dataset de modalidade para alunos presenciais.

    Args:
        df (pd.DataFrame): O DataFrame pré-processado.

    Returns:
        pd.DataFrame: O DataFrame do dataset.
    """
    df_presencial = df[df["natureza_participacao"] == "Presencial"].copy()

    if df_presencial.empty:
        return pd.DataFrame(columns=["Modalidade", "qtd", "pct_total"])

    return contar_categoria_simples(
        df_presencial,
        "modalidade",
        nome_coluna_saida="Modalidade",
        incluir_percentual=True,
        nome_percentual="pct_total",
        casas_percentual=2,
    )
