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
Plugin para procesamiento de plantillas Jinja2.

Procesa plantillas Jinja2 con variables y filtros personalizados.
"""

import logging
from jinja2 import Environment, BaseLoader, StrictUndefined, TemplateSyntaxError, UndefinedError
from jinja2.exceptions import TemplateError

from ..plugin_system import ProcessorPlugin, ProcessingContext

logger = logging.getLogger(__name__)


class Jinja2Plugin(ProcessorPlugin):
    """
    Plugin para procesamiento de plantillas Jinja2.
    """
    
    @property
    def name(self) -> str:
        return "jinja2"
    
    def process(self, context: ProcessingContext) -> ProcessingContext:
        """
        Procesa el contenido como una plantilla Jinja2.
        
        Args:
            context: Contexto con el contenido a procesar
        
        Returns:
            Contexto con el contenido renderizado
        """
        logger.info("Procesando plantillas Jinja2...")
        
        # Obtener configuración
        strict_undefined = self.config.get('strict_undefined', True)
        variable_start_string = self.config.get('variable_start_string', '{{')
        variable_end_string = self.config.get('variable_end_string', '}}')
        
        # Procesar plantilla
        rendered_content = self._process_template(
            context.content,
            context.variables,
            strict_undefined,
            variable_start_string,
            variable_end_string
        )
        
        context.update_content(rendered_content)
        return context
    
    def _process_template(self, template_content: str, variables: dict, 
                         strict_undefined: bool = True,
                         variable_start_string: str = '{{',
                         variable_end_string: str = '}}') -> str:
        """
        Procesa una plantilla Jinja2 con las variables proporcionadas.
        
        Args:
            template_content: Contenido de la plantilla
            variables: Variables para la plantilla
            strict_undefined: Si lanzar error para variables no definidas
            variable_start_string: Delimitador de inicio de variable
            variable_end_string: Delimitador de fin de variable
        
        Returns:
            Contenido renderizado
        
        Raises:
            TemplateError: Para errores de sintaxis o variables no definidas
        """
        try:
            # Configurar el entorno Jinja2
            env_kwargs = {
                'variable_start_string': variable_start_string,
                'variable_end_string': variable_end_string,
                'loader': BaseLoader()
            }
            
            if strict_undefined:
                env_kwargs['undefined'] = StrictUndefined
            
            env = Environment(**env_kwargs)
            
            # Agregar filtros personalizados
            env.filters['sql_escape'] = self._sql_escape_filter
            env.filters['strftime'] = self._strftime_filter
            
            # Crear y renderizar la plantilla
            template = env.from_string(template_content)
            return template.render(**variables)
            
        except (TemplateSyntaxError, UndefinedError, TemplateError) as e:
            raise Exception(f"Error procesando plantilla Jinja2: {str(e)}")
    
    @staticmethod
    def _sql_escape_filter(value):
        """
        Filtro personalizado para escapar valores SQL (doble comilla simple).
        """
        if isinstance(value, str):
            return value.replace("'", "''")
        return str(value)
    
    @staticmethod
    def _strftime_filter(value, format_str='%Y-%m-%d'):
        """
        Filtro personalizado para formatear fechas usando strftime.
        """
        if hasattr(value, 'strftime'):
            return value.strftime(format_str)
        return str(value)
