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
Sistema de plugins para MergeSourceFile.

Define la interfaz base para plugins y el pipeline de procesamiento.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class ProcessingContext:
    """
    Contexto compartido entre plugins durante el procesamiento.
    
    Attributes:
        content: Contenido actual siendo procesado
        input_file: Archivo de entrada original
        base_path: Ruta base para resolución de archivos
        variables: Variables disponibles para procesamiento
        metadata: Metadatos adicionales del procesamiento
    """
    
    def __init__(self, content: str = "", input_file: str = "", base_path: str = ".") -> None:
        self.content = content
        self.input_file = input_file
        self.base_path = base_path
        self.variables: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}
        self.verbose = False
    
    def update_content(self, new_content: str) -> None:
        """Actualiza el contenido del contexto."""
        self.content = new_content
    
    def set_variable(self, key: str, value: Any) -> None:
        """Establece una variable en el contexto."""
        self.variables[key] = value
    
    def get_variable(self, key: str, default: Any = None) -> Any:
        """Obtiene una variable del contexto."""
        return self.variables.get(key, default)


class ProcessorPlugin(ABC):
    """
    Interfaz base para todos los plugins de procesamiento.
    
    Cada plugin debe implementar el método process() que toma un contexto
    y retorna el contexto modificado.
    """
    
    def __init__(self, config: Dict[str, Any] = None) -> None:
        """
        Inicializa el plugin con configuración específica.
        
        Args:
            config: Diccionario con configuración del plugin
        """
        self.config = config or {}
        self.enabled = self.config.get('enabled', True)
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Retorna el nombre único del plugin."""
        pass
    
    @abstractmethod
    def process(self, context: ProcessingContext) -> ProcessingContext:
        """
        Procesa el contexto y retorna el contexto modificado.
        
        Args:
            context: Contexto de procesamiento actual
        
        Returns:
            Contexto modificado después del procesamiento
        """
        pass
    
    def is_enabled(self) -> bool:
        """Verifica si el plugin está habilitado."""
        return self.enabled


class PluginRegistry:
    """
    Registro de plugins disponibles en el sistema.
    
    Permite registrar y obtener plugins por nombre.
    """
    
    def __init__(self) -> None:
        self._plugins: Dict[str, ProcessorPlugin] = {}
    
    def register(self, plugin: ProcessorPlugin) -> None:
        """
        Registra un plugin en el sistema.
        
        Args:
            plugin: Plugin a registrar
        """
        self._plugins[plugin.name] = plugin
    
    def get(self, name: str) -> ProcessorPlugin:
        """
        Obtiene un plugin por nombre.
        
        Args:
            name: Nombre del plugin
        
        Returns:
            Plugin correspondiente
        
        Raises:
            KeyError: Si el plugin no está registrado
        """
        if name not in self._plugins:
            raise KeyError(f"Plugin '{name}' no encontrado en el registro")
        return self._plugins[name]
    
    def get_all(self) -> Dict[str, ProcessorPlugin]:
        """Retorna todos los plugins registrados."""
        return self._plugins.copy()
    
    def has(self, name: str) -> bool:
        """Verifica si un plugin está registrado."""
        return name in self._plugins


class ProcessorPipeline:
    """
    Pipeline de ejecución de plugins.
    
    Ejecuta los plugins en el orden especificado, pasando el contexto
    de uno a otro.
    """
    
    def __init__(self, registry: PluginRegistry, execution_order: List[str] = None) -> None:
        """
        Inicializa el pipeline.
        
        Args:
            registry: Registro de plugins disponibles
            execution_order: Lista con el orden de ejecución de plugins
        """
        self.registry = registry
        self.execution_order = execution_order or []
    
    def execute(self, context: ProcessingContext) -> ProcessingContext:
        """
        Ejecuta el pipeline de procesamiento.
        
        Args:
            context: Contexto inicial de procesamiento
        
        Returns:
            Contexto después de procesar todos los plugins
        """
        if context.verbose:
            logger.info("=" * 70)
            logger.info("Iniciando pipeline de procesamiento")
            logger.info("=" * 70)
            logger.info(f"Orden de ejecución: {' -> '.join(self.execution_order)}")
            logger.info("")
        
        for plugin_name in self.execution_order:
            try:
                plugin = self.registry.get(plugin_name)
                
                if not plugin.is_enabled():
                    logger.debug(f"Plugin '{plugin_name}' deshabilitado, omitiendo...")
                    continue
                
                logger.debug(f"Ejecutando plugin: {plugin_name}")
                
                context = plugin.process(context)
                
                logger.debug(f"Plugin '{plugin_name}' completado")
                
            except KeyError as e:
                logger.warning(f"{e}")
                continue
            except Exception as e:
                raise Exception(f"Error en plugin '{plugin_name}': {str(e)}")
        
        if context.verbose:
            logger.info("")
            logger.info("=" * 70)
            logger.info("Pipeline completado exitosamente")
            logger.info("=" * 70)
        
        return context
    
    def set_execution_order(self, order: List[str]) -> None:
        """
        Establece el orden de ejecución de plugins.
        
        Args:
            order: Lista con nombres de plugins en orden de ejecución
        """
        self.execution_order = order
