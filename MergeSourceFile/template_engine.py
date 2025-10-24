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
Motor de plantillas Jinja2 con sistema de extensiones.

Jinja2 es el núcleo, las extensiones modifican el input antes de procesar.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Callable
from jinja2 import Environment, BaseLoader, StrictUndefined, TemplateError

logger = logging.getLogger(__name__)


class TemplateEngine:
    """
    Motor de plantillas Jinja2 con soporte para extensiones.
    
    Las extensiones se ejecutan ANTES de Jinja2 para pre-procesar el contenido.
    """
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Inicializa el motor de plantillas.
        
        Args:
            config: Configuración completa del sistema
        """
        self.config = config
        self.jinja_config = config.get('jinja2', {})
        self.extensions: Dict[str, Callable] = {}
        
        # Configurar extensiones habilitadas
        self._setup_extensions()
    
    def _setup_extensions(self) -> None:
        """Registra extensiones habilitadas en la configuración."""
        enabled_extensions = self.jinja_config.get('extensions', [])
        
        for ext_name in enabled_extensions:
            if ext_name == 'sqlplus':
                from .extensions.sqlplus import process_sqlplus
                self.extensions['sqlplus'] = process_sqlplus
                logger.debug("Extensión 'sqlplus' registrada")
            else:
                logger.warning(f"Extensión '{ext_name}' no reconocida")
    
    def process_file(self, input_file: str, variables: Dict[str, Any]) -> str:
        """
        Procesa un archivo con Jinja2 y extensiones.
        
        Flujo:
        1. Lee archivo
        2. Aplica extensiones (pre-procesamiento)
        3. Aplica Jinja2 (procesamiento principal)
        
        Args:
            input_file: Archivo de entrada
            variables: Variables para la plantilla
        
        Returns:
            Contenido procesado
        """
        input_path = Path(input_file)
        
        # 1. Leer contenido inicial
        content = input_path.read_text(encoding='utf-8')
        logger.debug(f"Archivo leído: {input_file} ({len(content)} caracteres)")
        
        # 2. Aplicar extensiones (pre-procesamiento)
        for ext_name, ext_func in self.extensions.items():
            logger.info(f"Aplicando extensión: {ext_name}")
            
            ext_config = self.jinja_config.get(ext_name, {})
            content = ext_func(
                content=content,
                input_file=str(input_path),
                base_path=str(input_path.parent),
                config=ext_config,
                verbose=self.config.get('project', {}).get('verbose', False)
            )
            
            logger.debug(f"Extensión '{ext_name}' completada ({len(content)} caracteres)")
        
        # 3. Aplicar Jinja2 (procesamiento principal)
        logger.info("Procesando plantilla Jinja2")
        rendered_content = self._render_template(content, variables)
        
        logger.info(f"Procesamiento completado ({len(rendered_content)} caracteres)")
        return rendered_content
    
    def _render_template(self, template_content: str, variables: Dict[str, Any]) -> str:
        """
        Renderiza contenido con Jinja2.
        
        Args:
            template_content: Contenido de la plantilla
            variables: Variables disponibles
        
        Returns:
            Contenido renderizado
        """
        try:
            # Configurar entorno Jinja2
            env_kwargs = {
                'variable_start_string': self.jinja_config.get('variable_start_string', '{{'),
                'variable_end_string': self.jinja_config.get('variable_end_string', '}}'),
                'loader': BaseLoader()
            }
            
            if self.jinja_config.get('strict_undefined', True):
                env_kwargs['undefined'] = StrictUndefined
            
            env = Environment(**env_kwargs)
            
            # Agregar filtros personalizados
            env.filters['sql_escape'] = self._sql_escape_filter
            env.filters['strftime'] = self._strftime_filter
            
            # Renderizar
            template = env.from_string(template_content)
            return template.render(**variables)
            
        except TemplateError as e:
            raise Exception(f"Error procesando plantilla Jinja2: {str(e)}")
    
    @staticmethod
    def _sql_escape_filter(value):
        """Filtro para escapar comillas SQL."""
        if isinstance(value, str):
            return value.replace("'", "''")
        return str(value)
    
    @staticmethod
    def _strftime_filter(value, format_str='%Y-%m-%d'):
        """Filtro para formatear fechas."""
        if hasattr(value, 'strftime'):
            return value.strftime(format_str)
        return str(value)
