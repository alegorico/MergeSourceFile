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
Core - Sistema de plantillas basado en Jinja2.

Funcionalidades principales:
- Carga y validación de configuración TOML
- Función main() para procesamiento completo
- Setup de logging y carga de variables
"""

import sys
import logging
import traceback
import json
import tomllib
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


# ============================================================================
# CONFIGURACIÓN Y VALIDACIÓN TOML
# ============================================================================

def load_config(config_file: str = 'MKFSource.toml') -> Dict[str, Any]:
    """
    Carga la configuración desde un archivo TOML.
    
    Args:
        config_file: Ruta al archivo de configuración TOML
    
    Returns:
        Diccionario con la configuración normalizada
    
    Raises:
        FileNotFoundError: Si el archivo no existe
        ValueError: Si el archivo TOML es inválido
    """
    config_path = Path(config_file)
    current_dir = Path.cwd()
    
    if not config_path.exists():
        error_msg = [
            f"\n{'=' * 70}",
            f"ERROR: No se encontró el archivo de configuración",
            f"{'=' * 70}",
            f"",
            f"Archivo buscado: {config_file}",
            f"Directorio actual: {current_dir}",
            f"",
            f"Para usar MergeSourceFile, necesitas crear un archivo 'MKFSource.toml'",
            f"en el directorio desde donde ejecutas el comando.",
            f"",
            f"Ejemplo mínimo de MKFSource.toml:",
            f"",
            f"  [project]",
            f"  input = \"tu_archivo_entrada.sql\"",
            f"  output = \"archivo_salida.sql\"",
            f"",
            f"Para más información, consulta la documentación.",
            f"{'=' * 70}\n"
        ]
        logger.error('\n'.join(error_msg))
        raise FileNotFoundError(f"Archivo de configuración no encontrado: {config_path}")
    
    try:
        with open(config_path, 'rb') as f:
            config = tomllib.load(f)
        
        # Normalizar configuración (retrocompatibilidad)
        normalized = _normalize_config(config)
        
        # Validar configuración
        _validate_config(normalized, config_file)
        
        return normalized
    
    except tomllib.TOMLDecodeError as e:
        error_msg = [
            f"\n{'=' * 70}",
            f"ERROR: Sintaxis TOML inválida",
            f"{'=' * 70}",
            f"",
            f"El archivo '{config_file}' contiene errores de sintaxis TOML.",
            f"",
            f"Detalles del error:",
            f"  {str(e)}",
            f"",
            f"Verifica que:",
            f"  - Las secciones usen corchetes: [project]",
            f"  - Los valores de texto estén entre comillas: input = \"archivo.sql\"",
            f"  - Los valores booleanos sean: true o false (sin comillas)",
            f"",
            f"{'=' * 70}\n"
        ]
        logger.error('\n'.join(error_msg))
        raise ValueError("Error de sintaxis en archivo TOML")


def _normalize_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normaliza la configuración asegurando valores por defecto.
    
    Formato esperado:
        [project]
        input = "..."
        output = "..."
        execution_order = ["plugin1", "plugin2"]
        
        [plugins.nombre_plugin]
        enabled = true
        # ... otras configuraciones del plugin
    
    Nota: Los plugins específicos y su orden de ejecución deben ser
    definidos explícitamente en el archivo .toml, no hay valores
    por defecto hardcodeados.
    """
    # Asegurar que existan las secciones principales
    if 'project' not in config:
        config['project'] = {}
    if 'plugins' not in config:
        config['plugins'] = {}
    
    # Retrocompatibilidad: mover execution_order de [pipeline] a [project]
    if 'pipeline' in config and 'execution_order' in config['pipeline']:
        if 'execution_order' not in config['project']:
            config['project']['execution_order'] = config['pipeline']['execution_order']
    
    # Valores por defecto para project
    config['project'].setdefault('input', '')
    config['project'].setdefault('output', '')
    config['project'].setdefault('verbose', False)
    config['project'].setdefault('create_backup', False)
    
    # execution_order debe ser definido explícitamente
    config['project'].setdefault('execution_order', [])
    
    return config


def _validate_config(config: Dict[str, Any], config_file: str) -> None:
    """
    Valida que la configuración tenga todos los parámetros requeridos.
    
    Args:
        config: Configuración normalizada
        config_file: Nombre del archivo de configuración
    
    Raises:
        ValueError: Si faltan parámetros requeridos
    """
    # Validar sección project
    if 'project' not in config:
        error_msg = [
            f"\n{'=' * 70}",
            f"ERROR: Estructura de configuración inválida",
            f"{'=' * 70}",
            f"",
            f"El archivo '{config_file}' no contiene la sección [project].",
            f"",
            f"El archivo debe tener esta estructura:",
            f"",
            f"  [project]",
            f"  input = \"archivo.sql\"",
            f"  output = \"salida.sql\"",
            f"",
            f"{'=' * 70}\n"
        ]
        logger.error('\n'.join(error_msg))
        raise ValueError("Configuración inválida: falta sección [project]")
    
    # Validar parámetros requeridos (input y output son obligatorios)
    project_config = config['project']
    
    if not project_config.get('input'):
        error_msg = [
            f"\n{'=' * 70}",
            f"ERROR: Falta el parámetro 'input' requerido en la configuración",
            f"{'=' * 70}",
            f"",
            f"El parámetro 'input' es obligatorio y no está definido.",
            f"",
            f"Tu archivo {config_file} debe incluir:",
            f"",
            f"  [project]",
            f"  input = \"tu_archivo_entrada.sql\"",
            f"  output = \"archivo_salida.sql\"",
            f"",
            f"{'=' * 70}\n"
        ]
        logger.error('\n'.join(error_msg))
        raise ValueError("Configuración inválida: falta parámetro 'input'")
    
    if not project_config.get('output'):
        error_msg = [
            f"\n{'=' * 70}",
            f"ERROR: Falta el parámetro 'output' requerido en la configuración",
            f"{'=' * 70}",
            f"",
            f"El parámetro 'output' es obligatorio y no puede estar vacío.",
            f"",
            f"Tu archivo {config_file} debe incluir:",
            f"",
            f"  [project]",
            f"  input = \"tu_archivo_entrada.sql\"",
            f"  output = \"archivo_salida.sql\"",
            f"",
            f"{'=' * 70}\n"
        ]
        logger.error('\n'.join(error_msg))
        raise ValueError("Configuración inválida: falta parámetro 'output'")


# ============================================================================
# FUNCIONES PRINCIPALES Y ORQUESTACIÓN
# ============================================================================

def _setup_logging(verbose: bool = False) -> None:
    """Configura el sistema de logging."""
    level = logging.DEBUG if verbose else logging.INFO
    log_format = '%(message)s' if not verbose else '[%(levelname)s] %(name)s: %(message)s'
    logging.basicConfig(level=level, format=log_format, handlers=[logging.StreamHandler(sys.stdout)])


def _load_variables(config: Dict[str, Any]) -> Dict[str, Any]:
    """Carga variables desde archivo JSON si está configurado."""
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
    """
    Función principal del sistema.
    
    Args:
        config_file: Archivo de configuración TOML
        
    Returns:
        Código de salida (0 = éxito, 1 = error)
    """
    if config_file is None:
        config_file = 'MKFSource.toml'
    
    config = None
    try:
        # 1. Cargar configuración
        logger.info(f"Cargando configuración desde: {config_file}")
        config = load_config(config_file)
        
        # 2. Configurar logging
        verbose = config.get('project', {}).get('verbose', False)
        _setup_logging(verbose)
        
        # 3. Inicializar motor de plantillas
        from .template_engine import TemplateEngine
        engine = TemplateEngine(config)
        
        # 4. Cargar variables
        variables = _load_variables(config)
        
        # 5. Procesar archivo
        input_file = config['project']['input']
        result_content = engine.process_file(input_file, variables)
        
        # 6. Crear backup si se solicita
        output_file = config['project']['output']
        output_path = Path(output_file)
        
        if config.get('project', {}).get('create_backup', False) and output_path.exists():
            backup_path = output_path.with_suffix(output_path.suffix + '.bak')
            backup_path.write_text(output_path.read_text(encoding='utf-8'), encoding='utf-8')
            logger.info(f"Backup creado: {backup_path}")
        
        # 7. Escribir resultado
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(result_content, encoding='utf-8')
        logger.info(f"Procesamiento completado. Resultado en: {output_path}")
        
        return 0
        
    except FileNotFoundError as e:
        # El mensaje detallado ya se mostró via logger.error en load_config
        return 1
    except ValueError as e:
        # El mensaje detallado ya se mostró via logger.error en _validate_config
        return 1
    except Exception as e:
        logger.error(f"Error durante el procesamiento: {e}")
        if config and config.get('project', {}).get('verbose', False):
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())