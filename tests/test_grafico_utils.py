"""Testes para o módulo de gráficos."""

import pandas as pd

from src.grafico_utils import contar_categoria_simples, gerar_resumo_categoria


class TestContarCategoriaSimples:
    """Testes para função contar_categoria_simples."""

    def test_contagem_basica(self) -> None:
        df = pd.DataFrame({"categoria": ["A", "B", "A", "C", "B", "A"]})
        resultado = contar_categoria_simples(df, "categoria")
        assert len(resultado) == 3
        assert resultado[resultado["categoria"] == "A"]["qtd"].values[0] == 3
        assert resultado[resultado["categoria"] == "B"]["qtd"].values[0] == 2
        assert resultado[resultado["categoria"] == "C"]["qtd"].values[0] == 1

    def test_coluna_inexistente(self) -> None:
        df = pd.DataFrame({"col1": [1, 2, 3]})
        resultado = contar_categoria_simples(df, "coluna_inexistente")
        assert "qtd" in resultado.columns
        assert len(resultado) == 0

    def test_ignorar_vazios(self) -> None:
        df = pd.DataFrame({"categoria": ["A", "", None, "B", "  "]})
        resultado = contar_categoria_simples(df, "categoria", ignorar_vazios=True)
        assert len(resultado) == 2

    def test_incluir_percentual(self) -> None:
        df = pd.DataFrame({"categoria": ["A", "B", "A", "C"]})
        resultado = contar_categoria_simples(df, "categoria", incluir_percentual=True)
        assert "pct_total" in resultado.columns
        total = resultado["qtd"].sum()
        assert total == 4
        assert (
            abs(resultado[resultado["categoria"] == "A"]["pct_total"].values[0] - 50.0)
            < 0.01
        )

    def test_ordenar_por_qtd(self) -> None:
        df = pd.DataFrame({"categoria": ["A", "B", "C", "A", "A"]})
        resultado = contar_categoria_simples(
            df, "categoria", ordenar_por="qtd", ordem_decrescente=True
        )
        assert resultado.iloc[0]["categoria"] == "A"
        assert resultado.iloc[0]["qtd"] == 3

    def test_limite(self) -> None:
        df = pd.DataFrame({"categoria": ["A", "B", "C", "D", "E", "F"]})
        resultado = contar_categoria_simples(df, "categoria", limite=3)
        assert len(resultado) == 3

    def test_renomear_coluna(self) -> None:
        df = pd.DataFrame({"categoria": ["A", "B", "A"]})
        resultado = contar_categoria_simples(df, "categoria", nome_coluna_saida="tipo")
        assert "tipo" in resultado.columns
        assert "categoria" not in resultado.columns


class TestGerarResumoCategoria:
    """Testes para função gerar_resumo_categoria."""

    def test_resumo_completo(self) -> None:
        df = pd.DataFrame({"categoria": ["A", "B", "A", "C"]})
        resultado = gerar_resumo_categoria(df, "categoria")
        assert resultado["total"] == 4
        assert len(resultado["registros"]) == 3
        assert resultado["coluna"] == "categoria"

    def test_resumo_com_renomeacao(self) -> None:
        df = pd.DataFrame({"categoria": ["A", "B", "A"]})
        resultado = gerar_resumo_categoria(df, "categoria", nome_coluna_saida="tipo")
        assert resultado["coluna"] == "tipo"

    def test_resumo_df_vazio(self) -> None:
        df = pd.DataFrame()
        resultado = gerar_resumo_categoria(df, "categoria")
        assert resultado["total"] == 0
        assert len(resultado["registros"]) == 0
