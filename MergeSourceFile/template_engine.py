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
Motor de plantillas Jinja2 con sistema de extensiones integrado.

Jinja2 es el núcleo, las extensiones modifican el input antes de procesar.
Incluye registro central de extensiones y gestor unificado.
"""

import importlib
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional, Callable
from jinja2 import Environment, BaseLoader, FileSystemLoader, StrictUndefined, TemplateError

logger = logging.getLogger(__name__)

# ============================================================================
# REGISTRO CENTRAL DE EXTENSIONES
# ============================================================================
# Para agregar una nueva extensión:
# 1. Añadir entrada en EXTENSION_REGISTRY
# 2. Implementar el módulo correspondiente
# 3. Agregar configuración en TOML si es necesario

EXTENSION_REGISTRY: Dict[str, Dict[str, Any]] = {
    "sqlplus": {
        "module": "MergeSourceFile.extensions.sqlplus",
        "function": "process_sqlplus",
        "priority": 10,
        "namespace": "sql",  # Variables disponibles como sql_variable
        "description": "SQLPlus compatibility extension (@includes, DEFINE variables)"
    },
    
    # Ejemplo para futuras extensiones:
    # "yaml": {
    #     "module": "MergeSourceFile.extensions.yaml",
    #     "function": "process_yaml",
    #     "priority": 20,
    #     "namespace": "yaml",
    #     "description": "YAML processing extension"
    # },
    
    # "custom": {
    #     "module": "MergeSourceFile.extensions.custom",
    #     "function": "process_custom",
    #     "priority": 30,
    #     "namespace": "custom",
    #     "description": "Custom processing extension"
    # }
}

def get_extension_info(name: str) -> Dict[str, Any]:
    """
    Obtiene información de una extensión registrada.
    
    Args:
        name: Nombre de la extensión
        
    Returns:
        Información de la extensión
        
    Raises:
        KeyError: Si la extensión no está registrada
    """
    if name not in EXTENSION_REGISTRY:
        available = ", ".join(EXTENSION_REGISTRY.keys())
        logger.error(f"Extensión '{name}' no registrada. Extensiones disponibles: {available}")
        raise KeyError(f"Extensión no registrada: {name}")
    
    return EXTENSION_REGISTRY[name].copy()

def get_available_extensions() -> Dict[str, str]:
    """
    Retorna diccionario de extensiones disponibles con sus descripciones.
    
    Returns:
        Dict[nombre_extension, descripcion]
    """
    return {name: info["description"] for name, info in EXTENSION_REGISTRY.items()}

def validate_extension_list(extensions: list) -> list:
    """
    Valida una lista de extensiones y retorna solo las válidas.
    
    Args:
        extensions: Lista de nombres de extensiones
        
    Returns:
        Lista de extensiones válidas (puede estar vacía)
        
    Raises:
        ValueError: Si alguna extensión no está registrada
    """
    valid_extensions = []
    for ext_name in extensions:
        if ext_name in EXTENSION_REGISTRY:
            valid_extensions.append(ext_name)
        else:
            available = ", ".join(EXTENSION_REGISTRY.keys())
            logger.error(f"Extensión '{ext_name}' no está registrada. Extensiones disponibles: {available}")
            raise ValueError(f"Extensión no registrada: {ext_name}")
    
    return valid_extensions


# ============================================================================
# GESTOR DE EXTENSIONES
# ============================================================================

class ExtensionManager:
    """
    Gestor centralizado de extensiones.
    
    Carga extensiones desde el registro central y las ejecuta en orden de prioridad.
    """
    
    def __init__(self, jinja_config: Dict[str, Any]):
        """
        Inicializa el gestor de extensiones.
        
        Args:
            jinja_config: Configuración de la sección [jinja2]
        """
        self.jinja_config = jinja_config
        self.loaded_extensions: List[Dict[str, Any]] = []
        self._load_enabled_extensions()
    
    def _load_enabled_extensions(self):
        """Carga las extensiones habilitadas desde la configuración."""
        enabled_extensions = self.jinja_config.get('extensions', [])
        
        if not enabled_extensions:
            logger.debug("No hay extensiones habilitadas")
            return
        
        # Validar extensiones
        try:
            valid_extensions = validate_extension_list(enabled_extensions)
        except ValueError as e:
            logger.error(str(e))
            raise
        
        # Cargar cada extensión
        for ext_name in valid_extensions:
            try:
                ext_info = get_extension_info(ext_name)
                ext_info['name'] = ext_name
                ext_info['config'] = self.jinja_config.get(ext_name, {})
                
                # Importar función de procesamiento
                ext_info['handler'] = self._import_function(
                    ext_info['module'], 
                    ext_info['function']
                )
                
                self.loaded_extensions.append(ext_info)
                logger.debug(f"Extensión '{ext_name}' cargada desde {ext_info['module']}")
                
            except Exception as e:
                logger.error(f"Error cargando extensión '{ext_name}': {e}")
                raise
        
        # Ordenar por prioridad
        self.loaded_extensions.sort(key=lambda x: x['priority'])
        
        if self.loaded_extensions:
            ext_names = [ext['name'] for ext in self.loaded_extensions]
            logger.info(f"Extensiones cargadas (orden de ejecución): {ext_names}")
    
    def _import_function(self, module_name: str, function_name: str) -> Callable:
        """
        Importa una función desde un módulo.
        
        Args:
            module_name: Nombre del módulo
            function_name: Nombre de la función
            
        Returns:
            Función importada
            
        Raises:
            ImportError: Si no se puede importar
        """
        try:
            module = importlib.import_module(module_name)
            if not hasattr(module, function_name):
                logger.error(f"Función '{function_name}' no encontrada en módulo '{module_name}'")
                raise ImportError(f"Función no encontrada: {function_name}")
            return getattr(module, function_name)
        except ImportError as e:
            logger.error(f"Error importando {module_name}.{function_name}: {e}")
            raise
    
    def process_content(self, content: str, input_file: str, base_path: str, 
                       variables: Dict[str, Any], verbose: bool = False) -> Tuple[str, Dict[str, Any]]:
        """
        Procesa contenido a través de todas las extensiones cargadas.
        
        Args:
            content: Contenido a procesar
            input_file: Archivo de entrada
            base_path: Ruta base
            variables: Variables Jinja2 originales
            verbose: Modo verbose
            
        Returns:
            Tuple[contenido_procesado, variables_extraídas_con_namespace]
        """
        extracted_variables = {}
        
        for ext_info in self.loaded_extensions:
            ext_name = ext_info['name']
            logger.info(f"Aplicando extensión: {ext_name}")
            
            try:
                # Ejecutar extensión
                result = ext_info['handler'](
                    content=content,
                    input_file=input_file,
                    base_path=base_path,
                    config=ext_info['config'],
                    verbose=verbose
                )
                
                # Procesar resultado
                content, ext_vars = self._process_extension_result(
                    result, ext_info, variables
                )
                extracted_variables.update(ext_vars)
                
                logger.debug(f"Extensión '{ext_name}' completada ({len(content)} caracteres)")
                
            except Exception as e:
                logger.error(f"Error ejecutando extensión '{ext_name}': {e}")
                if verbose:
                    raise
                # En modo no-verbose, continuar con las demás extensiones
        
        return content, extracted_variables
    
    def _process_extension_result(self, result: Any, ext_info: Dict[str, Any], 
                                variables: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """
        Procesa el resultado de una extensión aplicando namespace.
        
        Args:
            result: Resultado de la extensión
            ext_info: Información completa de la extensión
            variables: Variables Jinja2 originales
            
        Returns:
            Tuple[contenido, variables_con_namespace]
        """
        extracted_variables = {}
        ext_name = ext_info['name']
        namespace = ext_info.get('namespace', ext_name)  # Default: nombre extensión
        
        if isinstance(result, tuple) and len(result) == 2:
            content, ext_vars = result
            if ext_vars:
                # Aplicar namespace: namespace_variable
                for var_name, var_value in ext_vars.items():
                    namespaced_name = f"{namespace}_{var_name}"
                    extracted_variables[namespaced_name] = var_value
                    
                    # Warning si hay conflicto con variables Jinja2
                    if var_name in variables:
                        logger.warning(
                            f"CONFLICTO DE VARIABLES: La variable '{var_name}' está definida "
                            f"tanto en extensión '{ext_name}' como en Jinja2. "
                            f"Usando namespace: '{var_name}' → '{{ {namespaced_name} }}'"
                        )
        else:
            # Extensión solo devuelve contenido
            content = result
        
        return content, extracted_variables
    
    def get_custom_loader(self) -> Optional[BaseLoader]:
        """
        Obtiene loader personalizado de extensiones.
        
        Busca función get_EXTENSION_loader en cada extensión cargada.
        Retorna el primer loader encontrado.
        
        Returns:
            Loader personalizado o None
        """
        for ext_info in self.loaded_extensions:
            ext_name = ext_info['name']
            
            try:
                # Buscar función get_{extension}_loader
                module = importlib.import_module(ext_info['module'])
                loader_func_name = f"get_{ext_name}_loader"
                
                if hasattr(module, loader_func_name):
                    loader_func = getattr(module, loader_func_name)
                    loader = loader_func(ext_info['config'])
                    
                    if loader:
                        logger.info(f"Usando loader personalizado de extensión '{ext_name}'")
                        return loader
                        
            except Exception as e:
                logger.debug(f"No se pudo obtener loader de extensión '{ext_name}': {e}")
                
        return None
    
    def has_extensions(self) -> bool:
        """Verifica si hay extensiones cargadas."""
        return len(self.loaded_extensions) > 0
    
    def get_extension_names(self) -> List[str]:
        """Retorna lista de nombres de extensiones cargadas."""
        return [ext['name'] for ext in self.loaded_extensions]


# ============================================================================
# MOTOR DE PLANTILLAS
# ============================================================================


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
        
        # Configurar gestor de extensiones
        self.extension_manager = ExtensionManager(self.jinja_config)
    
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
        content, extracted_variables = self.extension_manager.process_content(
            content=content,
            input_file=str(input_path),
            base_path=str(input_path.parent),
            variables=variables,
            verbose=self.config.get('project', {}).get('verbose', False)
        )
        
        # 3. Combinar variables extraídas con variables originales
        all_variables = variables.copy()
        all_variables.update(extracted_variables)
        
        if extracted_variables:
            logger.info(f"Variables SQLPlus extraídas con namespace sql_: {list(extracted_variables.keys())}")
        
        # 4. Aplicar Jinja2 (procesamiento principal)
        logger.info("Procesando plantilla Jinja2")
        rendered_content = self._render_template(content, all_variables, str(input_path.parent))
        
        logger.info(f"Procesamiento completado ({len(rendered_content)} caracteres)")
        return rendered_content
    
    def _render_template(self, template_content: str, variables: Dict[str, Any], template_dir: str = None) -> str:
        """
        Renderiza contenido con Jinja2.
        
        Args:
            template_content: Contenido de la plantilla
            variables: Variables disponibles
            template_dir: Directorio base para resolver includes
        
        Returns:
            Contenido renderizado
        """
        try:
            # Configurar entorno Jinja2
            env_kwargs = {
                'variable_start_string': self.jinja_config.get('variable_start_string', '{{'),
                'variable_end_string': self.jinja_config.get('variable_end_string', '}}'),
            }
            
            # Obtener loader personalizado de extensiones
            custom_loader = self.extension_manager.get_custom_loader()
            
            if custom_loader:
                env_kwargs['loader'] = custom_loader
            else:
                # Usar FileSystemLoader para permitir includes de Jinja2
                template_dir_path = template_dir if template_dir else str(Path.cwd())
                env_kwargs['loader'] = FileSystemLoader(str(template_dir_path))
            
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
