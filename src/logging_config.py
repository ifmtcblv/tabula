"""Configuração de logging para o projeto tabula."""

import logging
import sys


def setup_logging(
    name: str, level: int = logging.INFO, verbose: bool = False
) -> logging.Logger:
    """
    Configura logger com formato padrão.

    Args:
        name: Nome do logger (geralmente __name__)
        level: Nível de logging padrão
        verbose: Se True, usa DEBUG level

    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if verbose else level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG if verbose else level)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Obtém logger configurado para o módulo.

    Args:
        name: Nome do logger

    Returns:
        Logger configurado
    """
    return logging.getLogger(name)
