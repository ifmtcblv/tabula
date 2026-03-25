#!/usr/bin/env python3
"""Constrói datasets CSV agregados a partir da exportação mestre do SUAP."""

import argparse
import importlib
import json
import math
import re
import sys
import unicodedata
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple, Union

import pandas as pd

# Adiciona diretório pai ao path para importar src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.datasets_config import COLUNAS_DATA, ESPECS_SAIDA, SINONIMOS_COLUNAS
from src.logging_config import get_logger, setup_logging


def normalizar_texto(valor: Optional[str]) -> str:
    if valor is None:
        return ""
    texto = str(valor).strip()
    if not texto:
        return ""
    texto_nfkd = unicodedata.normalize("NFKD", texto)
    return "".join(ch for ch in texto_nfkd if not unicodedata.combining(ch)).lower()


def resolver_colunas(colunas: Sequence[str]) -> Dict[str, str]:
    mapa_normalizado = {normalizar_texto(col): col for col in colunas}
    resolvido: Dict[str, str] = {}
    for canonica, candidatas in SINONIMOS_COLUNAS.items():
        for candidata in candidatas + [canonica]:
            chave = normalizar_texto(candidata)
            if chave in mapa_normalizado:
                resolvido[canonica] = mapa_normalizado[chave]
                break
    return resolvido


def parse_datetime_excel(
    valor: Union[str, int, float, datetime, pd.Timestamp, None],
) -> Optional[pd.Timestamp]:
    if pd.isna(valor):
        return pd.NaT
    if isinstance(valor, pd.Timestamp):
        return valor
    if isinstance(valor, datetime):
        return pd.Timestamp(valor)
    if isinstance(valor, str):
        texto = valor.strip()
        if not texto:
            return pd.NaT
        parsed = pd.to_datetime(texto, errors="coerce", dayfirst=True)
        if pd.isna(parsed):
            parsed = pd.to_datetime(texto, errors="coerce")
        return parsed
    if isinstance(valor, (int, float)):
        if math.isnan(valor):
            return pd.NaT
        data_base = datetime(1899, 12, 30)
        return pd.Timestamp(data_base + timedelta(days=float(valor)))
    return pd.NaT


def garantir_datetime(series: Optional[pd.Series]) -> pd.Series:
    if series is None:
        return pd.Series(dtype="datetime64[ns]")
    convertido = series.apply(parse_datetime_excel)
    return pd.to_datetime(convertido, errors="coerce")


def parse_percentual(valor: Union[str, int, float, None]) -> float:
    if pd.isna(valor):
        return math.nan
    if isinstance(valor, (int, float)):
        return float(valor)
    texto = str(valor).strip()
    if not texto:
        return math.nan
    texto = texto.replace("%", "")
    texto = texto.replace(" ", "")
    texto = texto.replace(".", "", texto.count(".") - 1)
    texto = texto.replace(",", ".")
    match = re.search(r"-?\d+(?:\.\d+)?", texto)
    if not match:
        return math.nan
    try:
        return float(match.group())
    except ValueError:
        return math.nan


def bucketize_progresso(valor: Optional[float]) -> Optional[str]:
    if valor is None or pd.isna(valor):
        return None
    valor = max(0.0, min(100.0, float(valor)))
    if valor < 25:
        return "0-25%"
    if valor < 50:
        return "25-50%"
    if valor < 75:
        return "50-75%"
    return "75-100%"


def simplificar_status(texto: Optional[str]) -> str:
    normalizado = normalizar_texto(texto)
    if not normalizado:
        return "Outros"
    prefixos = {
        ("concl", "form"): "Concluído",
        ("ativ", "curs"): "Ativo",
        ("tranc",): "Trancado",
        ("cancel", "evad", "desl"): "Evasão/Cancelado",
    }
    for chaves, rotulo in prefixos.items():
        if any(normalizado.startswith(chave) for chave in chaves):
            return rotulo
    return "Outros"


def parse_ano(valor: object, data_fallback: Optional[pd.Timestamp]) -> Optional[int]:
    if valor is not None and not pd.isna(valor):
        if isinstance(valor, (int,)):
            return int(valor)
        if isinstance(valor, float):
            if not math.isnan(valor):
                return int(valor)
        texto = str(valor).strip()
        match = re.search(r"(19|20)\d{2}", texto)
        if match:
            return int(match.group())
    if data_fallback is not None and not pd.isna(data_fallback):
        return int(data_fallback.year)
    return None


def meses_entre(inicio: Optional[pd.Timestamp], fim: Optional[pd.Timestamp]) -> float:
    if inicio is None or pd.isna(inicio) or fim is None or pd.isna(fim):
        return math.nan
    delta_dias = (fim - inicio).days
    return float(round(delta_dias / 30.4375, 2))


def carregar_dataframe(caminho: Path) -> pd.DataFrame:
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")
    ext = caminho.suffix.lower()
    engine = None
    if ext == ".xls":
        engine = "xlrd"
    elif ext in {".xlsx", ".xlsm"}:
        engine = "openpyxl"
    try:
        return pd.read_excel(caminho, engine=engine)
    except ImportError as err:
        sys.exit(f"Dependência ausente para leitura de {ext}: {err}")


def pre_processar(df: pd.DataFrame) -> Tuple[pd.DataFrame, set]:
    df = df.copy()
    resolvido = resolver_colunas(df.columns)
    df = df.rename(columns={origem: destino for destino, origem in resolvido.items()})
    fontes_disponiveis = set(resolvido.keys())

    # Garante que as colunas canônicas existam
    for canonica in SINONIMOS_COLUNAS:
        if canonica not in df.columns:
            df[canonica] = pd.NA

    for col in COLUNAS_DATA:
        df[col] = garantir_datetime(df[col])

    if "situacao_curso" in fontes_disponiveis and df["situacao_curso"].notna().any():
        series_status = df["situacao_curso"]
    else:
        series_status = df["situacao_sistema"]
    df["status_simplificado"] = series_status.apply(simplificar_status)

    df["percentual_progresso_num"] = df["percentual_progresso"].apply(parse_percentual)
    df["bucket_progresso"] = df["percentual_progresso_num"].apply(bucketize_progresso)

    hoje = pd.Timestamp(datetime.today().date())
    df["tempo_curso_meses"] = df.apply(
        lambda row: (
            meses_entre(
                row.get("data_matricula"),
                (
                    row.get("data_conclusao")
                    if row.get("status_simplificado") == "Concluído"
                    else hoje
                ),
            )
            if not pd.isna(row.get("data_matricula"))
            else math.nan
        ),
        axis=1,
    )

    df["coorte_ano"] = df.apply(
        lambda row: parse_ano(
            row.get("ano_ingresso"),
            row.get("data_matricula"),
        ),
        axis=1,
    )

    return df, fontes_disponiveis


def resolver_coluna_status(df: pd.DataFrame, fontes_disponiveis: set) -> str:
    if "situacao_curso" in fontes_disponiveis and df["situacao_curso"].notna().any():
        return "situacao_curso"
    if (
        "situacao_sistema" in fontes_disponiveis
        and df["situacao_sistema"].notna().any()
    ):
        return "situacao_sistema"
    return "status_simplificado"


def escrever_csv(df: pd.DataFrame, caminho: Path) -> None:
    df.to_csv(caminho, index=False, sep=";", encoding="utf-8")


def tem_colunas_necessarias(df: pd.DataFrame, requires: Iterable[str]) -> bool:
    for coluna in requires:
        if coluna not in df.columns:
            return False
        series = df[coluna]
        if isinstance(series, pd.Series) and series.dropna().empty:
            return False
    return True


def tem_fontes_necessarias(disponiveis: set, spec: Dict) -> bool:
    fontes_todas: List[str] = spec.get("sources_all", [])
    for coluna in fontes_todas:
        if coluna not in disponiveis:
            return False
    fontes_alguma: List[List[str]] = spec.get("sources_any", [])
    for grupo in fontes_alguma:
        if not any(coluna in disponiveis for coluna in grupo):
            return False
    return True


def construir_datasets(caminho_entrada: Path, diretorio_saida: Path) -> None:
    logger = get_logger(__name__)
    df = carregar_dataframe(caminho_entrada)
    df, fontes_disponiveis = pre_processar(df)
    diretorio_saida.mkdir(parents=True, exist_ok=True)

    for nome_arquivo, spec in ESPECS_SAIDA.items():
        builder_name = spec.get("builder")
        if not builder_name:
            continue

        try:
            builder_module = importlib.import_module(f"src.construtores.{builder_name}")
        except ImportError:
            logger.warning(f"Construtor não encontrado para: {nome_arquivo}")
            continue

        requires = spec.get("requires", [])
        if not tem_fontes_necessarias(fontes_disponiveis, spec):
            logger.info(f"Dataset pulado (fontes ausentes): {nome_arquivo}")
            continue
        if not tem_colunas_necessarias(df, requires):
            logger.info(f"Dataset pulado (dados insuficientes): {nome_arquivo}")
            continue

        if builder_name == "alunos_por_situacao":
            coluna_status = resolver_coluna_status(df, fontes_disponiveis)
            gerado = builder_module.construir(df, coluna_status)
        else:
            gerado = builder_module.construir(df)

        if gerado is None or gerado.empty:
            logger.info(f"Dataset pulado (sem dados): {nome_arquivo}")
            continue
        escrever_csv(gerado, diretorio_saida / nome_arquivo)
        logger.info(f"Gerado: {nome_arquivo}")

    # Registra data/hora da importação para exibição no painel
    meta = {"atualizado_em": datetime.now().strftime("%d/%m/%Y %H:%M")}
    (diretorio_saida / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False), encoding="utf-8"
    )
    logger.info("Gerado: meta.json")


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gera datasets agregados em CSV")
    parser.add_argument(
        "--in",
        dest="caminho_entrada",
        required=True,
        help="Arquivo mestre (.xls/.xlsx)",
    )
    parser.add_argument(
        "--out",
        dest="diretorio_saida",
        required=True,
        help="Diretório de saída para CSVs",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Aumenta verbosidade do logging",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)
    setup_logging(__name__, verbose=args.verbose)
    logger = get_logger(__name__)
    caminho_entrada = Path(args.caminho_entrada)
    diretorio_saida = Path(args.diretorio_saida)
    logger.info(f"Processando arquivo: {caminho_entrada}")
    logger.info(f"Saída: {diretorio_saida}")
    construir_datasets(caminho_entrada, diretorio_saida)


if __name__ == "__main__":
    main()
