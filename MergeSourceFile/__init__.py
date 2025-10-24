"""
MergeSourceFile - Sistema de plantillas basado en Jinja2.

Motor de plantillas Jinja2 con soporte para extensiones opcionales.
Las extensiones permiten pre-procesar el contenido antes del renderizado Jinja2.

Versión 2.0.0 - Nueva Arquitectura
===================================
Esta versión introduce una arquitectura simplificada centrada en Jinja2.
El sistema de plugins ha sido reemplazado por extensiones opcionales.

Extensiones disponibles:
- sqlplus: Compatibilidad con SQL*Plus (inclusiones @/@@, variables DEFINE)

Para configurar extensiones, consulta la documentación.
"""

__version__ = "2.0.0"
__author__ = "Alejandro G."
__license__ = "MIT"

from .main import main

# Core - API Principal
from .config_loader import load_config
from .template_engine import TemplateEngine

__all__ = [
    # Función principal
    "main",
    # Core API
    "load_config",
    "TemplateEngine",
]
