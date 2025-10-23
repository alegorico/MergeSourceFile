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
MergeSourceFile - Sistema modular de procesamiento de archivos basado en plugins.

Arquitectura extensible que permite procesar archivos de texto mediante
plugins configurables. El sistema es agnóstico al tipo de procesamiento,
delegando toda la lógica específica a los plugins registrados.
"""

import sys
import logging
import traceback
from pathlib import Path
from typing import Dict, Any, List

from .config_loader import ConfigLoader
from .resource_io import ResourceLoader, ResourceWriter
from .plugin_system import ProcessingContext, PluginRegistry, ProcessorPipeline
from .plugins import get_available_plugins

# Configuración de logging
logger = logging.getLogger(__name__)


def _setup_plugins(config: Dict[str, Any]) -> PluginRegistry:
    """
    Configura y registra plugins dinámicamente basándose en la configuración.
    
    Los plugins se registran solo si:
    1. Están definidos en la sección [plugins.nombre_plugin]
    2. Tienen enabled = true
    3. Existe una clase de plugin disponible
    
    Args:
        config: Configuración normalizada
    
    Returns:
        Registro de plugins configurados
    """
    registry = PluginRegistry()
    plugins_config = config.get('plugins', {})
    available_plugins = get_available_plugins()
    
    # Iterar sobre todos los plugins configurados
    for plugin_name, plugin_config in plugins_config.items():
        # Verificar si el plugin está habilitado
        if not plugin_config.get('enabled', False):
            logger.debug(f"Plugin '{plugin_name}' está deshabilitado")
            continue
        
        # Verificar si existe una clase de plugin disponible
        if plugin_name not in available_plugins:
            logger.warning(
                f"Plugin '{plugin_name}' está configurado pero no existe "
                f"una implementación disponible. Plugins disponibles: {list(available_plugins.keys())}"
            )
            continue
        
        # Instanciar y registrar el plugin
        plugin_class = available_plugins[plugin_name]
        try:
            plugin_instance = plugin_class(plugin_config)
            registry.register(plugin_instance)
            logger.debug(f"Plugin '{plugin_name}' registrado correctamente")
        except Exception as e:
            logger.error(f"Error al instanciar plugin '{plugin_name}': {e}")
            raise
    
    return registry


def _create_context(config: Dict[str, Any]) -> ProcessingContext:
    """
    Crea el contexto inicial de procesamiento.
    
    Args:
        config: Configuración normalizada
    
    Returns:
        Contexto de procesamiento inicializado
    """
    project_config = config['project']
    
    context = ProcessingContext()
    context.input_file = project_config['input']
    context.base_path = Path.cwd()
    context.verbose = project_config.get('verbose', False)
    
    # Cargar contenido del archivo de entrada
    try:
        input_content = ResourceLoader.read_text_file(context.input_file)
        context.update_content(input_content)
        logger.debug(f"Contenido cargado desde: {context.input_file}")
    except FileNotFoundError:
        logger.error(f"Archivo de entrada no encontrado: {context.input_file}")
        raise
    
    # Cargar variables desde archivos de configuración de plugins
    # Buscar cualquier plugin que tenga un 'variables_file' configurado
    plugins_config = config.get('plugins', {})
    for plugin_name, plugin_config in plugins_config.items():
        variables_file = plugin_config.get('variables_file')
        
        if variables_file:
            try:
                plugin_variables = ResourceLoader.read_json_file(variables_file)
                context.variables.update(plugin_variables)
                logger.info(f"Variables cargadas desde: {variables_file} (plugin: {plugin_name})")
            except FileNotFoundError:
                logger.warning(f"Archivo de variables no encontrado: {variables_file}")
            except ValueError as e:
                logger.warning(f"Error al cargar variables desde {variables_file}: {e}")
    
    return context


def _get_execution_order(config: Dict[str, Any]) -> List[str]:
    """
    Obtiene y valida el orden de ejecución de plugins desde la configuración.
    
    Args:
        config: Configuración normalizada
    
    Returns:
        Lista con el orden de ejecución
    
    Raises:
        ValueError: Si execution_order no está definido o está vacío
    """
    project_config = config.get('project', {})
    execution_order = project_config.get('execution_order', [])
    available_plugins = get_available_plugins()
    
    if not execution_order:
        # Obtener lista de plugins disponibles para el mensaje de error
        available_list = list(available_plugins.keys())
        example_order = available_list[:2] if len(available_list) >= 2 else available_list
        
        error_msg = [
            f"\n{'=' * 70}",
            f"ERROR: Orden de ejecución no definido",
            f"{'=' * 70}",
            f"",
            f"Debes especificar el orden de ejecución de plugins en tu archivo .toml:",
            f"",
            f"  [project]",
            f"  input = \"archivo.sql\"",
            f"  output = \"salida.sql\"",
            f"  execution_order = [\"plugin1\", \"plugin2\"]",
            f"",
            f"Plugins disponibles: {available_list}",
            f"",
            f"Ejemplo con los plugins disponibles:",
            f"",
            f"  [project]",
            f"  execution_order = {example_order}",
            f"",
            f"{'=' * 70}\n"
        ]
        raise ValueError('\n'.join(error_msg))
    
    # Validar que los plugins en execution_order estén configurados
    plugins_config = config.get('plugins', {})
    for plugin_name in execution_order:
        if plugin_name not in plugins_config:
            logger.warning(
                f"Plugin '{plugin_name}' está en execution_order pero no está "
                f"configurado en la sección [plugins.{plugin_name}]"
            )
        elif not plugins_config[plugin_name].get('enabled', False):
            logger.warning(
                f"Plugin '{plugin_name}' está en execution_order pero está deshabilitado"
            )
    
    return execution_order


def _setup_logging(verbose: bool = False) -> None:
    """
    Configura el sistema de logging.
    
    Args:
        verbose: Si activar modo verbose (DEBUG level)
    """
    level = logging.DEBUG if verbose else logging.INFO
    
    # Formato del log
    log_format = '%(message)s' if not verbose else '[%(levelname)s] %(name)s: %(message)s'
    
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def main(config_file: str = None) -> int:
    """
    Función principal de ejecución.
    
    Args:
        config_file: Ruta al archivo de configuración TOML (opcional, por defecto 'MKFSource.toml')
    
    Returns:
        Código de salida (0 = éxito, 1 = error)
    
    Flujo:
    1. Cargar configuración
    2. Configurar plugins
    3. Crear contexto
    4. Ejecutar pipeline
    5. Escribir resultado
    """
    if config_file is None:
        config_file = 'MKFSource.toml'
    
    config = None
    
    try:
        # 1. Cargar configuración
        logger.info(f"Cargando configuración desde: {config_file}")
        config = ConfigLoader.load(config_file)
        
        # Configurar logging según el modo verbose
        verbose = config.get('project', {}).get('verbose', False)
        _setup_logging(verbose)
        
        # 2. Configurar plugins
        registry = _setup_plugins(config)
        
        # 3. Crear contexto de procesamiento
        context = _create_context(config)
        
        # 4. Ejecutar pipeline
        execution_order = _get_execution_order(config)
        pipeline = ProcessorPipeline(registry, execution_order)
        
        result_context = pipeline.execute(context)
        
        # 5. Escribir resultado usando ResourceWriter
        output_file = config['project']['output']
        create_backup = config.get('project', {}).get('create_backup', False)
        
        writer = ResourceWriter(
            output_path=output_file,
            create_backup=create_backup,
            base_path=str(context.base_path)
        )
        writer.write(result_context.content)
        
        logger.info(f"Procesamiento completado. Resultado escrito en: {writer.get_output_path()}")
        return 0
    
    except FileNotFoundError as e:
        logger.error(f"Error: {e}")
        return 1
    except ValueError as e:
        logger.error(f"Error de configuración: {e}")
        return 1
    except Exception as e:
        logger.error(f"Error durante el procesamiento: {e}")
        if config and config.get('project', {}).get('verbose', False):
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
