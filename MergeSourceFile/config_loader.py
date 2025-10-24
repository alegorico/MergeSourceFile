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
Módulo de carga y validación de configuración TOML.

Funciones principales:
- load_config(): Carga y valida configuración desde archivo TOML
- _normalize_config(): Aplica valores por defecto y retrocompatibilidad
- _validate_config(): Valida parámetros requeridos
"""

import tomllib
from pathlib import Path
from typing import Dict, Any


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
        raise FileNotFoundError('\n'.join(error_msg))
    
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
        raise ValueError('\n'.join(error_msg))
    

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
        raise ValueError('\n'.join(error_msg))
    
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
        raise ValueError('\n'.join(error_msg))
    
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
        raise ValueError('\n'.join(error_msg))
