#!/usr/bin/env python3
"""Gera o site estático a partir dos templates e configurações."""

import shutil
import sys
from pathlib import Path
from typing import Dict

from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path(__file__).parent
SRC_STATIC = BASE_DIR / ".." / "src" / "web_static"
WEB_DIR = BASE_DIR / ".." / "web"
TEMPLATES_DIR = BASE_DIR / ".." / "src" / "templates"

# Adiciona diretório pai ao path para importar src
sys.path.insert(0, str(BASE_DIR / ".."))

from src.datasets_config import ESPECS_SAIDA  # noqa: E402
from src.logging_config import get_logger  # noqa: E402

SECTIONS: Dict[str, str] = {
    "overview": "Visão Geral",
    "inclusao": "Inclusão & Acesso",
    "cruzadas": "Análises Cruzadas",
}


def generate_site() -> None:
    logger = get_logger(__name__)
    logger.info(f"Cleaning {WEB_DIR}...")
    if WEB_DIR.exists():
        for item in WEB_DIR.iterdir():
            if item.name == ".gitkeep":
                continue
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
    else:
        WEB_DIR.mkdir()

    logger.info(f"Copying static assets from {SRC_STATIC}...")
    for item in SRC_STATIC.iterdir():
        if item.is_dir():
            shutil.copytree(item, WEB_DIR / item.name)
        else:
            shutil.copy2(item, WEB_DIR / item.name)

    # Setup Jinja2
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

    # Prepare configs
    configs = []
    for spec in ESPECS_SAIDA.values():
        if "frontend" in spec:
            configs.append(spec["frontend"])

    # Generate index.html
    logger.info("Generating web/index.html...")
    template_index = env.get_template("index.html")
    index_content = template_index.render(configs=configs, sections=SECTIONS)
    (WEB_DIR / "index.html").write_text(index_content, encoding="utf-8")

    # Generate individual chart pages
    logger.info("Generating individual chart pages...")
    template_chart = env.get_template("chart.html")
    for config in configs:
        page_name = f"{config['key']}.html"
        logger.info(f"  - {page_name}")

        # Calculate relative path: configs use path relative to 'web/js/',
        # but HTML pages are in 'web/'. So we need to prepend 'js/'.
        # e.g. "./charts/situacao.js" -> "./js/charts/situacao.js"
        module_path = config["module"]
        if module_path.startswith("./"):
            module_path = f"./js/{module_path[2:]}"
        elif module_path.startswith("charts/"):
            module_path = f"js/{module_path}"

        page_content = template_chart.render(module_path=module_path, **config)
        (WEB_DIR / page_name).write_text(page_content, encoding="utf-8")

    # Generate main.js for index dashboard
    logger.info("Generating web/js/main.js...")
    # Logic remains similar but could be templated too.
    # For now, inline generation is fine as it's code, not markup.
    imports = []
    calls = []
    for item in configs:
        func_name = item["function"]
        module_path = item["module"]
        imports.append(f"import {{ {func_name} }} from '{module_path}';")
        calls.append(f"    {func_name}(),")

    main_js_content = f"""{"".join(imports)}

function loadCharts() {{
  const loaders = [
{chr(10).join(calls)}
  ];

  Promise.allSettled(loaders).catch((error) => {{
    console.error('Falha ao carregar os gráficos', error);
  }});
}}

document.addEventListener('DOMContentLoaded', loadCharts);
"""
    (WEB_DIR / "js" / "main.js").write_text(main_js_content, encoding="utf-8")

    logger.info("Site generation complete.")


def main() -> None:
    generate_site()


if __name__ == "__main__":
    main()
