"""
Paquete de plugins para MergeSourceFile.

Este módulo centraliza el registro de todos los plugins disponibles.
"""

from .sqlplus_plugin import SQLPlusIncludesPlugin, SQLPlusVarsPlugin
from .jinja2_plugin import Jinja2Plugin

__all__ = ['SQLPlusIncludesPlugin', 'SQLPlusVarsPlugin', 'Jinja2Plugin']


# Registro centralizado de plugins disponibles
# Este es el único lugar donde se mapea nombres de plugins a sus clases
AVAILABLE_PLUGINS = {
    'sqlplus_includes': SQLPlusIncludesPlugin,
    'sqlplus_vars': SQLPlusVarsPlugin,
    'jinja2': Jinja2Plugin,
}


def get_available_plugins():
    """
    Retorna el diccionario de plugins disponibles.
    
    Returns:
        Dict con mapeo de nombre_plugin -> clase_plugin
    """
    return AVAILABLE_PLUGINS.copy()
