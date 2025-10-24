# MIT License
# 
# Copyright (c) 2023 Alejandro G.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
MergeSourceFile - Sistema de plantillas basado en Jinja2.

Motor de plantillas con soporte para extensiones opcionales.
"""

import sys
import logging
import traceback
import json
from pathlib import Path
from typing import Dict, Any

from .config_loader import load_config
from .template_engine import TemplateEngine

logger = logging.getLogger(__name__)


def _setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    log_format = '%(message)s' if not verbose else '[%(levelname)s] %(name)s: %(message)s'
    logging.basicConfig(level=level, format=log_format, handlers=[logging.StreamHandler(sys.stdout)])


def _load_variables(config: Dict[str, Any]) -> Dict[str, Any]:
    variables = {}
    variables_file = config.get('jinja2', {}).get('variables_file')
    if variables_file:
        try:
            with open(variables_file, 'r', encoding='utf-8') as f:
                file_vars = json.load(f)
                variables.update(file_vars)
                logger.info(f"Variables cargadas desde: {variables_file}")
        except FileNotFoundError:
            logger.warning(f"Archivo de variables no encontrado: {variables_file}")
        except json.JSONDecodeError as e:
            logger.warning(f"Error al leer variables JSON: {e}")
    return variables


def main(config_file: str = None) -> int:
    if config_file is None:
        config_file = 'MKFSource.toml'
    config = None
    try:
        logger.info(f"Cargando configuración desde: {config_file}")
        config = load_config(config_file)
        verbose = config.get('project', {}).get('verbose', False)
        _setup_logging(verbose)
        engine = TemplateEngine(config)
        variables = _load_variables(config)
        input_file = config['project']['input']
        result_content = engine.process_file(input_file, variables)
        output_file = config['project']['output']
        output_path = Path(output_file)
        if config.get('project', {}).get('create_backup', False) and output_path.exists():
            backup_path = output_path.with_suffix(output_path.suffix + '.bak')
            backup_path.write_text(output_path.read_text(encoding='utf-8'), encoding='utf-8')
            logger.info(f"Backup creado: {backup_path}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(result_content, encoding='utf-8')
        logger.info(f"Procesamiento completado. Resultado en: {output_path}")
        return 0
    except FileNotFoundError as e:
        logger.error(f"Error: {e}")
        return 1
    except ValueError as e:
        logger.error(f"Error de configuración: {e}")
        return 1
    except Exception as e:
        logger.error(f"Error durante el procesamiento: {e}")
        if config and config.get('project', {}).get('verbose', False):
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
