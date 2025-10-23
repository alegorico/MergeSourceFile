"""
MergeSourceFile - Sistema modular de procesamiento de archivos basado en plugins.

Arquitectura extensible que permite procesar archivos de texto mediante
plugins configurables. El framework es agnóstico al tipo de procesamiento,
permitiendo implementar cualquier lógica de transformación mediante plugins.

Versión 2.0.0 - Breaking Changes
================================
Esta versión introduce una arquitectura completamente nueva basada en plugins.
No es compatible con la API de la versión 1.x.

Los plugins disponibles se registran dinámicamente. Para consultar los plugins
instalados, usa: `get_available_plugins()`

Para migrar código existente, consulta la documentación de migración.
"""

__version__ = "2.0.0"
__author__ = "Alejandro G."
__license__ = "MIT"

from .main import main

# Core - API Principal
from .config_loader import ConfigLoader
from .resource_io import ResourceLoader
from .plugin_system import (
    ProcessingContext,
    ProcessorPlugin,
    PluginRegistry,
    ProcessorPipeline
)

# Plugin System - Acceso a plugins disponibles
from .plugins import get_available_plugins

__all__ = [
    # Función principal
    "main",
    # Core API
    "ConfigLoader",
    "ResourceLoader",
    "ProcessingContext",
    "ProcessorPlugin",
    "PluginRegistry",
    "ProcessorPipeline",
    # Plugin Discovery
    "get_available_plugins",
]
