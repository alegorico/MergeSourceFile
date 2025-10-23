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
Plugin para procesamiento de archivos SQL*Plus.

Maneja la resolución de inclusiones (@, @@) y sustitución de variables DEFINE/UNDEFINE.
"""

import re
import logging
from pathlib import Path
from typing import Dict, Tuple

from ..plugin_system import ProcessorPlugin, ProcessingContext

logger = logging.getLogger(__name__)


class SQLPlusIncludesPlugin(ProcessorPlugin):
    """
    Plugin para resolver inclusiones @ y @@ de SQL*Plus.
    """
    
    @property
    def name(self) -> str:
        return "sqlplus_includes"
    
    def process(self, context: ProcessingContext) -> ProcessingContext:
        """
        Resuelve todas las inclusiones de archivos @ y @@.
        
        Args:
            context: Contexto con el archivo a procesar
        
        Returns:
            Contexto con el contenido expandido
        """
        logger.info("Árbol de inclusiones:")
        
        # Determinar la ruta base
        input_path = Path(context.input_file)
        if input_path.is_absolute():
            base_path = input_path.parent
        else:
            base_path = Path(context.base_path)
        
        # Procesar inclusiones
        expanded_content = self._parse_sqlplus_file(
            context.input_file,
            base_path,
            tree_depth=0,
            verbose=context.verbose
        )
        
        context.update_content(expanded_content)
        return context
    
    def _read_file_recursive(self, file_path: str, base_path: Path, tree_depth: int, verbose: bool) -> str:
        """
        Lee un archivo recursivamente resolviendo inclusiones @ y @@.
        
        Args:
            file_path: Archivo a procesar
            base_path: Ruta base para resolución
            tree_depth: Profundidad actual del árbol (para visualización)
            verbose: Si mostrar información detallada
        
        Returns:
            Contenido expandido del archivo
        """
        # Si file_path es absoluto o si tree_depth es 0 (archivo principal), usar file_path directamente
        if tree_depth == 0 or Path(file_path).is_absolute():
            full_path = Path(file_path)
        else:
            # Solo para archivos incluidos (@, @@), usar base_path
            full_path = base_path / file_path
        
        if not full_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {full_path}")
        
        # Crear un prefijo basado en la profundidad del árbol
        prefix = "    " * tree_depth + "|-- "
        
        # Mostrar el archivo que se está procesando
        logger.info(prefix + f"{full_path.name}")

        content = ""
        with full_path.open('r') as f:
            for line in f:
                line = line.rstrip()
                logger.debug(f"Procesando línea: {line}")
                
                if line.startswith('@@'):
                    nested_file_path = line[2:].strip()
                    logger.debug(f"Se encontró inclusión de archivo con @@: {nested_file_path}")
                    content += self._read_file_recursive(nested_file_path, full_path.parent, tree_depth + 1, verbose) + '\n'
                elif line.startswith('@'):
                    nested_file_path = line[1:].strip()
                    logger.debug(f"Se encontró inclusión de archivo con @: {nested_file_path}")
                    content += self._read_file_recursive(nested_file_path, base_path, tree_depth + 1, verbose) + '\n'
                else:
                    content += line + '\n'
        return content
    
    def _parse_sqlplus_file(self, input_file: str, base_path: Path, tree_depth: int = 0, verbose: bool = False) -> str:
        """
        Lee y resuelve inclusiones @ y @@, construyendo un árbol.
        
        Args:
            input_file: Archivo a procesar
            base_path: Ruta base para resolución
            tree_depth: Profundidad actual del árbol (para visualización)
            verbose: Si mostrar información detallada
        
        Returns:
            Contenido expandido
        """
        return self._read_file_recursive(input_file, base_path, tree_depth, verbose)


class SQLPlusVarsPlugin(ProcessorPlugin):
    """
    Plugin para procesar variables DEFINE/UNDEFINE de SQL*Plus.
    """
    
    @property
    def name(self) -> str:
        return "sqlplus_vars"
    
    def process(self, context: ProcessingContext) -> ProcessingContext:
        """
        Procesa variables DEFINE y UNDEFINE en el contenido.
        
        Args:
            context: Contexto con el contenido a procesar
        
        Returns:
            Contexto con las variables sustituidas
        """
        skip_var = self.config.get('skip_var', False)
        
        if skip_var:
            logger.info("Sustitución de variables deshabilitada")
            return context
        
        processed_content, replacement_stats = self._process_file_sequentially(
            context.content,
            verbose=context.verbose
        )
        
        # Guardar estadísticas en metadata
        context.metadata['variable_replacements'] = replacement_stats
        
        context.update_content(processed_content)
        return context
    
    def _process_file_sequentially(self, file_content: str, verbose: bool = False) -> Tuple[str, Dict[str, int]]:
        """
        Reemplaza variables en el archivo con evaluación de orden.
        
        Args:
            file_content: Contenido del archivo
            verbose: Si mostrar información detallada
        
        Returns:
            Tupla (contenido procesado, diccionario de estadísticas de reemplazo)
        """
        defines: Dict[str, str] = {}
        replaced_content = []
        
        # Patrones regex
        define_pattern = re.compile(r'^define\s+(\w+)\s*=\s*(?:\'(.*?)\'|([^\s;]+))\s*;?\s*$', re.IGNORECASE)
        undefine_pattern = re.compile(r'^undefine\s+(\w+)\s*;\s*$', re.IGNORECASE)
        variable_pattern = re.compile(r"(&\w+)(\.\.)?")
        
        # Diccionario para contar las veces que se reemplazan las variables
        replacement_count: Dict[str, int] = {}

        for line_number, line in enumerate(file_content.splitlines(), 1):
            clean = line.rstrip()

            # Si es un comentario, simplemente lo agregamos sin procesar
            if clean.lstrip().startswith('--'):
                replaced_content.append(line)
                continue

            # Detectar líneas DEFINE
            if clean.lstrip().upper().startswith('DEFINE '):
                match_define = define_pattern.match(clean)
                if match_define:
                    var_name = match_define.group(1)
                    # El valor puede estar en el grupo 2 (con comillas) o grupo 3 (sin comillas)
                    var_value = match_define.group(2) if match_define.group(2) is not None else match_define.group(3)
                    
                    # Validar que el valor no sea None
                    if var_value is None:
                        raise ValueError(f"Error: DEFINE con valor inválido en línea {line_number}: '{clean.strip()}'")
                    
                    defines[var_name] = var_value
                    logger.debug(f"Definiendo variable: {var_name} = {var_value}")
                    
                    # Inicializar el contador de reemplazo
                    if var_name not in replacement_count:
                        replacement_count[var_name] = 0
                    continue
                else:
                    # Sintaxis DEFINE inválida
                    logger.debug(f"Ignorando DEFINE con sintaxis invalida en linea {line_number}: '{clean.strip()}'")

            # Si es una línea UNDEFINE
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
                var_name = match[0][1:]  # Nombre sin el símbolo '&'
                if var_name not in defines:
                    raise ValueError(f"Error: La variable '{var_name}' se usa antes de ser definida (línea {line_number}).")
                
                value = defines[var_name]
                
                # Reemplazar
                if match[1]:  # Si tiene puntos concatenados (..)
                    replaced_line = replaced_line.replace(match[0] + "..", value + ".")
                else:
                    replaced_line = replaced_line.replace(match[0], value)
                
                logger.debug(f"Reemplazando variable {var_name} con valor {value} en la línea {line_number}")
                
                replacement_count[var_name] += 1

            replaced_content.append(replaced_line)

        # Mostrar resumen de sustituciones
        logger.info("\nResumen de sustituciones:")
        if replacement_count:
            max_var_length = max(len(var) for var in replacement_count)
            for var, count in replacement_count.items():
                logger.info(f"{var.ljust(max_var_length)}\t{count}")
        else:
            logger.info("No se realizaron sustituciones de variables.")

        return "\n".join(replaced_content), replacement_count
