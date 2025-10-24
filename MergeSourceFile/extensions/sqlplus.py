# MIT License
# 
# Copyright (c) 2023 Alejandro G.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/sell
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
Extensión SQLPlus para Jinja2.

Funciones de pre-procesamiento para compatibilidad con SQL*Plus:
- Resolución de inclusiones @ y @@
- Procesamiento de variables DEFINE/UNDEFINE
"""

import re
import logging
from pathlib import Path
from typing import Dict, Tuple
from jinja2 import BaseLoader, TemplateError

logger = logging.getLogger(__name__)


class NoIncludeLoader(BaseLoader):
    """
    Loader personalizado que deshabilita includes de Jinja2 para SQLPlus.
    
    Lanza error si se intenta usar {% include %} cuando SQLPlus maneja las inclusiones.
    """
    
    def get_source(self, environment, template):
        raise TemplateError(
            "Los includes de Jinja2 están deshabilitados porque la extensión SQLPlus "
            "está manejando las inclusiones. Use '@archivo' en lugar de '{% include \"archivo\" %}'"
        )


def process_sqlplus(
    content: str,
    input_file: str,
    base_path: str,
    config: Dict,
    verbose: bool = False
) -> Tuple[str, Dict[str, str]]:
    """
    Procesa contenido con extensiones SQLPlus.
    
    Procesa inclusiones SQLPlus (@, @@) y variables (DEFINE/UNDEFINE),
    extrayendo las variables DEFINE para su uso en Jinja2 con namespace sql_.
    
    Args:
        content: Contenido a procesar (no usado si process_includes=True)
        input_file: Archivo de entrada (para resolver rutas relativas)
        base_path: Ruta base para resolución de archivos
        config: Configuración de la extensión sqlplus
        verbose: Modo verbose
    
    Returns:
        Tuple[contenido_procesado, variables_define_extraidas]
    """
    extracted_variables = {}
    
    # 1. Procesar inclusiones @ / @@ (si está habilitado)
    if config.get('process_includes', True):
        logger.info("Procesando inclusiones SQLPlus (@, @@)")
        content = _process_includes(content, input_file, base_path, verbose)
    
    # 2. Procesar variables DEFINE / UNDEFINE (si está habilitado)
    if config.get('process_defines', True):
        logger.info("Procesando variables SQLPlus (DEFINE, UNDEFINE)")
        content, extracted_variables = _process_defines_with_extraction(content, verbose)
    
    return content, extracted_variables


def get_sqlplus_loader(config: Dict) -> BaseLoader:
    """
    Retorna el loader apropiado para SQLPlus basado en configuración.
    
    Args:
        config: Configuración de la extensión SQLPlus
        
    Returns:
        NoIncludeLoader si process_includes=True, None si no debe interferir
    """
    if config.get('process_includes', True):
        return NoIncludeLoader()
    return None


def _process_includes(content: str, input_file: str, base_path: str, verbose: bool) -> str:
    """
    Resuelve inclusiones @ y @@ en el contenido.
    
    Esta función lee el archivo original y expande las inclusiones recursivamente.
    
    Args:
        content: Contenido original (no usado, se lee desde input_file)
        input_file: Archivo de entrada
        base_path: Ruta base para resolución
        verbose: Modo verbose
    
    Returns:
        Contenido con inclusiones expandidas
    """
    input_path = Path(input_file)
    logger.info("Árbol de inclusiones:")
    
    return _read_file_recursive(
        file_path=str(input_path),
        base_path=input_path.parent if input_path.is_absolute() else Path(base_path),
        tree_depth=0,
        verbose=verbose
    )


def _read_file_recursive(file_path: str, base_path: Path, tree_depth: int, verbose: bool) -> str:
    """
    Lee archivo recursivamente resolviendo inclusiones @ y @@.
    
    Args:
        file_path: Archivo a procesar
        base_path: Ruta base para resolución
        tree_depth: Profundidad del árbol (para logging)
        verbose: Modo verbose
    
    Returns:
        Contenido expandido
    """
    # Si es el archivo principal (tree_depth=0) o path absoluto, usar path directamente
    if tree_depth == 0 or Path(file_path).is_absolute():
        full_path = Path(file_path)
    else:
        # Para archivos incluidos, resolver relativo a base_path
        full_path = base_path / file_path
    
    if not full_path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {full_path}")
    
    # Prefijo para visualizar el árbol
    prefix = "    " * tree_depth + "|-- "
    logger.info(prefix + f"{full_path.name}")
    
    content = ""
    for line in full_path.read_text(encoding='utf-8').splitlines():
        line = line.rstrip()
        logger.debug(f"Procesando línea: {line}")
        
        if line.startswith('@@'):
            # @@ = relativo al directorio del archivo padre
            nested_file = line[2:].strip()
            logger.debug(f"Inclusión @@: {nested_file}")
            content += _read_file_recursive(nested_file, full_path.parent, tree_depth + 1, verbose) + '\n'
        elif line.startswith('@'):
            # @ = relativo a base_path
            nested_file = line[1:].strip()
            logger.debug(f"Inclusión @: {nested_file}")
            content += _read_file_recursive(nested_file, base_path, tree_depth + 1, verbose) + '\n'
        else:
            content += line + '\n'
    
    return content


def _process_defines_with_extraction(content: str, verbose: bool) -> Tuple[str, Dict[str, str]]:
    """
    Procesa variables DEFINE y UNDEFINE, extrayendo las variables para Jinja2.
    
    Args:
        content: Contenido a procesar
        verbose: Modo verbose
    
    Returns:
        Tuple[contenido_con_variables_sustituidas, variables_extraidas]
    """
    defines: Dict[str, str] = {}
    replaced_lines = []
    replacement_count: Dict[str, int] = {}
    
    # Patrones regex
    define_pattern = re.compile(r'^define\s+(\w+)\s*=\s*(?:\'(.*?)\'|([^\s;]+))\s*;?\s*$', re.IGNORECASE)
    undefine_pattern = re.compile(r'^undefine\s+(\w+)\s*;\s*$', re.IGNORECASE)
    variable_pattern = re.compile(r"(&\w+)(\.\.)?")
    
    for line_number, line in enumerate(content.splitlines(), 1):
        clean = line.rstrip()
        
        # Comentarios se preservan sin procesar
        if clean.lstrip().startswith('--'):
            replaced_lines.append(line)
            continue
        
        # Detectar líneas DEFINE
        if clean.lstrip().upper().startswith('DEFINE '):
            match = define_pattern.match(clean)
            if match:
                var_name = match.group(1)
                # Valor puede estar con comillas (grupo 2) o sin comillas (grupo 3)
                var_value = match.group(2) if match.group(2) is not None else match.group(3)
                
                if var_value is None:
                    raise ValueError(f"Error: DEFINE con valor inválido en línea {line_number}: '{clean.strip()}'")
                
                defines[var_name] = var_value
                logger.debug(f"Definiendo variable: {var_name} = {var_value}")
                
                # Inicializar contador
                if var_name not in replacement_count:
                    replacement_count[var_name] = 0
                continue
            else:
                # Sintaxis DEFINE inválida - ignorar
                logger.debug(f"Ignorando DEFINE con sintaxis inválida en línea {line_number}: '{clean.strip()}'")
        
        # Detectar líneas UNDEFINE
        match_undefine = undefine_pattern.match(clean)
        if match_undefine:
            var_name = match_undefine.group(1)
            if var_name in defines:
                del defines[var_name]
            logger.debug(f"Variable indefinida: {var_name}")
            continue
        
        # Reemplazar variables en la línea
        all_matches = variable_pattern.findall(clean)
        replaced_line = clean
        
        for match in all_matches:
            var_name = match[0][1:]  # Sin el símbolo '&'
            if var_name not in defines:
                raise ValueError(
                    f"Error: La variable '{var_name}' se usa antes de ser definida (línea {line_number})."
                )
            
            value = defines[var_name]
            
            # Reemplazar
            if match[1]:  # Tiene concatenación '..'
                replaced_line = replaced_line.replace(match[0] + "..", value + ".")
            else:
                replaced_line = replaced_line.replace(match[0], value)
            
            logger.debug(f"Reemplazando variable {var_name} con valor {value} en línea {line_number}")
            replacement_count[var_name] += 1
        
        replaced_lines.append(replaced_line)
    
    # Mostrar resumen de sustituciones
    logger.info("\nResumen de sustituciones:")
    if replacement_count:
        max_var_length = max(len(var) for var in replacement_count)
        for var, count in replacement_count.items():
            logger.info(f"{var.ljust(max_var_length)}\t{count}")
    else:
        logger.info("No se realizaron sustituciones de variables.")
    
    return "\n".join(replaced_lines), defines


def _process_defines(content: str, verbose: bool) -> str:
    """
    Procesa variables DEFINE y UNDEFINE en el contenido.
    
    Args:
        content: Contenido a procesar
        verbose: Modo verbose
    
    Returns:
        Contenido con variables sustituidas
    """
    defines: Dict[str, str] = {}
    replaced_lines = []
    replacement_count: Dict[str, int] = {}
    
    # Patrones regex
    define_pattern = re.compile(r'^define\s+(\w+)\s*=\s*(?:\'(.*?)\'|([^\s;]+))\s*;?\s*$', re.IGNORECASE)
    undefine_pattern = re.compile(r'^undefine\s+(\w+)\s*;\s*$', re.IGNORECASE)
    variable_pattern = re.compile(r"(&\w+)(\.\.)?")
    
    for line_number, line in enumerate(content.splitlines(), 1):
        clean = line.rstrip()
        
        # Comentarios se preservan sin procesar
        if clean.lstrip().startswith('--'):
            replaced_lines.append(line)
            continue
        
        # Detectar líneas DEFINE
        if clean.lstrip().upper().startswith('DEFINE '):
            match = define_pattern.match(clean)
            if match:
                var_name = match.group(1)
                # Valor puede estar con comillas (grupo 2) o sin comillas (grupo 3)
                var_value = match.group(2) if match.group(2) is not None else match.group(3)
                
                if var_value is None:
                    raise ValueError(f"Error: DEFINE con valor inválido en línea {line_number}: '{clean.strip()}'")
                
                defines[var_name] = var_value
                logger.debug(f"Definiendo variable: {var_name} = {var_value}")
                
                # Inicializar contador
                if var_name not in replacement_count:
                    replacement_count[var_name] = 0
                continue
            else:
                # Sintaxis DEFINE inválida - ignorar
                logger.debug(f"Ignorando DEFINE con sintaxis inválida en línea {line_number}: '{clean.strip()}'")
        
        # Detectar líneas UNDEFINE
        match_undefine = undefine_pattern.match(clean)
        if match_undefine:
            var_name = match_undefine.group(1)
            if var_name in defines:
                del defines[var_name]
            logger.debug(f"Variable indefinida: {var_name}")
            continue
        
        # Reemplazar variables en la línea
        all_matches = variable_pattern.findall(clean)
        replaced_line = clean
        
        for match in all_matches:
            var_name = match[0][1:]  # Sin el símbolo '&'
            if var_name not in defines:
                raise ValueError(
                    f"Error: La variable '{var_name}' se usa antes de ser definida (línea {line_number})."
                )
            
            value = defines[var_name]
            
            # Reemplazar
            if match[1]:  # Tiene concatenación '..'
                replaced_line = replaced_line.replace(match[0] + "..", value + ".")
            else:
                replaced_line = replaced_line.replace(match[0], value)
            
            logger.debug(f"Reemplazando variable {var_name} con valor {value} en línea {line_number}")
            replacement_count[var_name] += 1
        
        replaced_lines.append(replaced_line)
    
    # Mostrar resumen de sustituciones
    logger.info("\nResumen de sustituciones:")
    if replacement_count:
        max_var_length = max(len(var) for var in replacement_count)
        for var, count in replacement_count.items():
            logger.info(f"{var.ljust(max_var_length)}\t{count}")
    else:
        logger.info("No se realizaron sustituciones de variables.")
    
    return "\n".join(replaced_lines)
