"""Testes para o módulo de construção de datasets."""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))
from run.construir_datasets import (
    bucketize_progresso,
    garantir_datetime,
    meses_entre,
    normalizar_texto,
    parse_datetime_excel,
    parse_percentual,
    simplificar_status,
    tem_colunas_necessarias,
    tem_fontes_necessarias,
    tem_necessidade_especial,
)


class TestNormalizarTexto:
    """Testes para função normalizar_texto."""

    def test_texto_simples(self) -> None:
        assert normalizar_texto("Teste") == "teste"

    def test_texto_com_acento(self) -> None:
        assert normalizar_texto("Áéíóú") == "aeiou"

    def test_texto_com_espacos(self) -> None:
        assert normalizar_texto("  Teste  ") == "teste"

    def test_texto_vazio(self) -> None:
        assert normalizar_texto("") == ""

    def test_texto_none(self) -> None:
        assert normalizar_texto(None) == ""

    def test_texto_com_maiusculas(self) -> None:
        assert normalizar_texto("TeStE") == "teste"


class TestParsePercentual:
    """Testes para função parse_percentual."""

    def test_percentual_inteiro(self) -> None:
        assert parse_percentual(50) == 50.0

    def test_percentual_float(self) -> None:
        assert parse_percentual(50.5) == 50.5

    def test_percentual_string_com_percentual(self) -> None:
        assert parse_percentual("50%") == 50.0

    def test_percentual_string_com_ponto(self) -> None:
        assert parse_percentual("50.5") == 50.5

    def test_percentual_string_com_virgula(self) -> None:
        assert parse_percentual("50,5") == 50.5

    def test_percentual_vazio(self) -> None:
        import math

        assert math.isnan(parse_percentual(""))

    def test_percentual_none(self) -> None:
        import math

        assert math.isnan(parse_percentual(None))


class TestBucketizeProgresso:
    """Testes para função bucketize_progresso."""

    def test_bucket_0_25(self) -> None:
        assert bucketize_progresso(10) == "0-25%"

    def test_bucket_25_50(self) -> None:
        assert bucketize_progresso(30) == "25-50%"

    def test_bucket_50_75(self) -> None:
        assert bucketize_progresso(60) == "50-75%"

    def test_bucket_75_100(self) -> None:
        assert bucketize_progresso(80) == "75-100%"

    def test_boundaries(self) -> None:
        assert bucketize_progresso(0) == "0-25%"
        assert bucketize_progresso(24.99) == "0-25%"
        assert bucketize_progresso(25) == "25-50%"
        assert bucketize_progresso(49.99) == "25-50%"
        assert bucketize_progresso(50) == "50-75%"
        assert bucketize_progresso(74.99) == "50-75%"
        assert bucketize_progresso(75) == "75-100%"
        assert bucketize_progresso(100) == "75-100%"

    def test_clamp_baixo(self) -> None:
        assert bucketize_progresso(-10) == "0-25%"

    def test_clamp_alto(self) -> None:
        assert bucketize_progresso(150) == "75-100%"

    def test_none(self) -> None:
        assert bucketize_progresso(None) is None

    def test_nan(self) -> None:
        assert bucketize_progresso(float("nan")) is None


class TestSimplificarStatus:
    """Testes para função simplificar_status."""

    def test_status_concluido(self) -> None:
        assert simplificar_status("Concluído") == "Concluído"
        assert simplificar_status("Concluido") == "Concluído"
        assert simplificar_status("Formado") == "Concluído"

    def test_status_ativo(self) -> None:
        assert simplificar_status("Ativo") == "Ativo"
        assert simplificar_status("Cursando") == "Ativo"

    def test_status_trancado(self) -> None:
        assert simplificar_status("Trancado") == "Trancado"

    def test_status_evasao(self) -> None:
        assert simplificar_status("Cancelado") == "Evasão/Cancelado"
        assert simplificar_status("Evadido") == "Evasão/Cancelado"
        assert simplificar_status("Desligado") == "Evasão/Cancelado"

    def test_status_outros(self) -> None:
        assert simplificar_status("Outro") == "Outros"

    def test_status_vazio(self) -> None:
        assert simplificar_status("") == "Outros"

    def test_status_none(self) -> None:
        assert simplificar_status(None) == "Outros"


class TestTemNecessidadeEspecial:
    """Testes para função tem_necessidade_especial."""

    def test_sim(self) -> None:
        assert tem_necessidade_especial("Sim") == "Sim"
        assert tem_necessidade_especial("Deficiência visual") == "Sim"
        assert tem_necessidade_especial("TDAH") == "Sim"

    def test_nao(self) -> None:
        assert tem_necessidade_especial("Não") == "Não"
        assert tem_necessidade_especial("Não possui") == "Não"
        assert tem_necessidade_especial("NAOPOSSUI") == "Não"
        assert tem_necessidade_especial("NaoSeAplica") == "Não"
        assert tem_necessidade_especial("N") == "Não"
        assert tem_necessidade_especial("NA") == "Não"
        assert tem_necessidade_especial("0") == "Não"

    def test_vazio(self) -> None:
        assert tem_necessidade_especial("") == "Não"

    def test_none(self) -> None:
        assert tem_necessidade_especial(None) == "Não"


class TestParseDatetimeExcel:
    """Testes para função parse_datetime_excel."""

    def test_timestamp(self) -> None:
        ts = pd.Timestamp("2020-01-01")
        result = parse_datetime_excel(ts)
        assert result == ts

    def test_string_iso(self) -> None:
        result = parse_datetime_excel("2020-01-01")
        assert result == pd.Timestamp("2020-01-01")

    def test_string_br(self) -> None:
        result = parse_datetime_excel("01/01/2020")
        assert result == pd.Timestamp("2020-01-01")

    def test_excel_serial(self) -> None:
        result = parse_datetime_excel(43831)
        assert result == pd.Timestamp("2020-01-01")

    def test_none(self) -> None:
        result = parse_datetime_excel(None)
        assert pd.isna(result)

    def test_vazio(self) -> None:
        result = parse_datetime_excel("")
        assert pd.isna(result)

    def test_invalid(self) -> None:
        result = parse_datetime_excel("invalid")
        assert pd.isna(result)


class TestGarantirDatetime:
    """Testes para função garantir_datetime."""

    def test_series_valida(self) -> None:
        series = pd.Series(["2020-01-01", "2020-01-02"])
        result = garantir_datetime(series)
        assert isinstance(result, pd.Series)
        assert result.dtype.name.startswith("datetime64")

    def test_series_none(self) -> None:
        result = garantir_datetime(None)
        assert isinstance(result, pd.Series)


class TestMesesEntre:
    """Testes para função meses_entre."""

    def test_meses_calculados(self) -> None:
        inicio = pd.Timestamp("2020-01-01")
        fim = pd.Timestamp("2020-07-01")
        resultado = meses_entre(inicio, fim)
        assert abs(resultado - 6.0) < 0.1

    def test_inicio_none(self) -> None:
        import math

        assert math.isnan(meses_entre(None, pd.Timestamp("2020-01-01")))

    def test_fim_none(self) -> None:
        import math

        assert math.isnan(meses_entre(pd.Timestamp("2020-01-01"), None))

    def test_inicio_nan(self) -> None:
        import math

        assert math.isnan(meses_entre(pd.NaT, pd.Timestamp("2020-01-01")))

    def test_fim_nan(self) -> None:
        import math

        assert math.isnan(meses_entre(pd.Timestamp("2020-01-01"), pd.NaT))


class TestTemColunasNecessarias:
    """Testes para função tem_colunas_necessarias."""

    def test_colunas_presentes(self) -> None:
        df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        assert tem_colunas_necessarias(df, ["col1", "col2"])

    def test_coluna_ausente(self) -> None:
        df = pd.DataFrame({"col1": [1, 2]})
        assert not tem_colunas_necessarias(df, ["col1", "col2"])

    def test_coluna_com_valores_nulos(self) -> None:
        df = pd.DataFrame({"col1": [None, None]})
        assert not tem_colunas_necessarias(df, ["col1"])

    def test_df_vazio(self) -> None:
        df = pd.DataFrame()
        assert not tem_colunas_necessarias(df, ["col1"])


class TestTemFontesNecessarias:
    """Testes para função tem_fontes_necessarias."""

    def test_fontes_all_presentes(self) -> None:
        disponiveis = {"col1", "col2", "col3"}
        spec = {"sources_all": ["col1", "col2"]}
        assert tem_fontes_necessarias(disponiveis, spec)

    def test_fontes_all_ausente(self) -> None:
        disponiveis = {"col1", "col2"}
        spec = {"sources_all": ["col1", "col3"]}
        assert not tem_fontes_necessarias(disponiveis, spec)

    def test_fontes_any_presente(self) -> None:
        disponiveis = {"col1", "col2"}
        spec = {"sources_any": [["col1", "col3"]]}
        assert tem_fontes_necessarias(disponiveis, spec)

    def test_fontes_any_ausente(self) -> None:
        disponiveis = {"col1", "col2"}
        spec = {"sources_any": [["col3", "col4"]]}
        assert not tem_fontes_necessarias(disponiveis, spec)

    def test_sem_requisitos(self) -> None:
        disponiveis = {"col1"}
        spec: dict[str, list[list[str]]] = {}
        assert tem_fontes_necessarias(disponiveis, spec)
