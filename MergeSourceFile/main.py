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

import re
import sys
from pathlib import Path
from jinja2 import Environment, BaseLoader, StrictUndefined, TemplateSyntaxError, UndefinedError
from jinja2.exceptions import TemplateError
import tomllib


# 1. Funcion para leer y resolver inclusiones @ y @@, construyendo un arbol
def parse_sqlplus_file(input_file, base_path='.', tree_depth=0, verbose=False):
    
    def read_file(file_path, base_path, tree_depth):
        # Si file_path es absoluto o si tree_depth es 0 (archivo principal), usar file_path directamente
        if tree_depth == 0 or Path(file_path).is_absolute():
            full_path = Path(file_path)
        else:
            # Solo para archivos incluidos (@, @@), usar base_path
            full_path = Path(base_path) / file_path
        
        if not full_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {full_path}")
        
        # Crear un prefijo basado en la profundidad del arbol
        prefix = "    " * tree_depth + "|-- "
        
        # Mostrar el archivo que se esta procesando con el nuevo estilo
        print(prefix + f"{full_path.name}")

        content = ""
        with full_path.open('r') as f:
            for line in f:
                line = line.rstrip()
                if verbose:
                    print(f"[VERBOSE] Procesando linea: {line}")
                if line.startswith('@@'):
                    nested_file_path = line[2:].strip()
                    if verbose:
                        print(f"[VERBOSE] Se encontro inclusion de archivo con @@: {nested_file_path}")
                    content += read_file(nested_file_path, full_path.parent, tree_depth + 1) + '\n'
                elif line.startswith('@'):
                    nested_file_path = line[1:].strip()
                    if verbose:
                        print(f"[VERBOSE] Se encontro inclusion de archivo con @: {nested_file_path}")
                    content += read_file(nested_file_path, base_path, tree_depth + 1) + '\n'
                else:
                    content += line + '\n'
        return content
        
    base_path = Path(base_path)
    return read_file(input_file, base_path, tree_depth)


# 2. Funcion para reemplazar variables en el archivo con evaluacion de orden
def process_file_sequentially(file_content, verbose=False):
    defines = {}
    replaced_content = []
    # Modificado para soportar valores con decimales, guiones y otros caracteres validos
    # Acepta: DEFINE var = 'valor' (con comillas) y DEFINE var = valor (sin comillas, incluyendo 3.14, ABC-123, etc.)
    define_pattern = re.compile(r'^define\s+(\w+)\s*=\s*(?:\'(.*?)\'|([^\s;]+))\s*;?\s*$', re.IGNORECASE)
    undefine_pattern = re.compile(r'^undefine\s+(\w+)\s*;\s*$', re.IGNORECASE)
    variable_pattern = re.compile(r"(&\w+)(\.\.)?")
    
    # Diccionario para contar las veces que se reemplazan las variables
    replacement_count = {}

    for line_number, line in enumerate(file_content.splitlines(), 1):
        clean = line.rstrip()

        # Si es un comentario, simplemente lo agregamos sin procesar
        if clean.lstrip().startswith('--'):
            replaced_content.append(line)
            continue

        # Detectar posibles lineas DEFINE problematicas antes del match principal
        if clean.lstrip().upper().startswith('DEFINE '):
            match_define = define_pattern.match(clean)
            if match_define:
                var_name = match_define.group(1)
                # El valor puede estar en el grupo 2 (con comillas) o grupo 3 (sin comillas)
                var_value = match_define.group(2) if match_define.group(2) is not None else match_define.group(3)
                
                # Validar que el valor no sea None (valores vacios '' son validos)
                if var_value is None:
                    raise ValueError(f"Error: DEFINE con valor invalido en linea {line_number}: '{clean.strip()}'")
                
                defines[var_name] = var_value  # Redefinicion permitida
                if verbose:
                    print(f"[VERBOSE] Definiendo variable: {var_name} = {var_value}")
                # Inicializar el contador de reemplazo para la variable definida
                if var_name not in replacement_count:
                    replacement_count[var_name] = 0
                continue  # No agregar la linea DEFINE al resultado final
            else:
                # Es una linea que empieza con DEFINE pero no coincide con el patron
                if verbose:
                    print(f"[VERBOSE] Ignorando DEFINE con sintaxis invalida en linea {line_number}: '{clean.strip()}'")
                # Continuar procesando la linea como texto normal (podria ser un comentario o SQL valido)

        # Si es una linea UNDEFINE, eliminamos la variable
        match_undefine = undefine_pattern.match(clean)
        if match_undefine:
            var_name = match_undefine.group(1)
            if var_name in defines:
                del defines[var_name]  # Eliminar la variable del diccionario
            if verbose:
                print(f"[VERBOSE] Variable indefinida: {var_name}")
            continue  # No agregar la linea UNDEFINE al resultado final

        # Si no es un DEFINE ni UNDEFINE, verificamos si hay variables que deben ser reemplazadas
        all_matches = variable_pattern.findall(clean)

        # Revisar cada variable usada en la linea
        replaced_line = clean
        for match in all_matches:
            var_name = match[0][1:]  # Nombre de la variable sin el simbolo '&'
            if var_name not in defines:
                raise ValueError(f"Error: La variable '{var_name}' se usa antes de ser definida (linea {line_number}).")
            value = defines[var_name]
            
            # Reemplazar y contar
            if match[1]:  # Si tiene puntos concatenados (..)
                replaced_line = replaced_line.replace(match[0] + "..", value + ".")
            else:
                replaced_line = replaced_line.replace(match[0], value)
            
            if verbose:
                print(f"[VERBOSE] Reemplazando variable {var_name} con valor {value} en la linea {line_number}")
            # Incrementar el contador de reemplazos para la variable
            replacement_count[var_name] += 1

        replaced_content.append(replaced_line)

    # Mostrar las variables y cuantas veces fueron reemplazadas, con formato justificado
    print("\nResumen de sustituciones:")
    if replacement_count:
        max_var_length = max(len(var) for var in replacement_count)  # Ancho maximo de las variables
        for var, count in replacement_count.items():
            print(f"{var.ljust(max_var_length)}\t{count}")
    else:
        print("No se realizaron sustituciones de variables.")

    return "\n".join(replaced_content)


# 3. Funcion que combina todo el proceso
def process_file_with_replacements(input_file, skip_var=False, verbose=False):
    # Siempre resolveremos las inclusiones @ y @@
    print("Arbol de inclusiones:")
    # Calcular la ruta base del archivo de entrada
    import os
    
    # Si input_file es relativo, usar el directorio actual como base_path
    # Si input_file es absoluto, usar su directorio padre
    if os.path.isabs(input_file):
        base_path = os.path.dirname(input_file)
    else:
        base_path = os.getcwd()
    
    full_content = parse_sqlplus_file(input_file, base_path, verbose=verbose)

    if not skip_var:
        # Si NO se pasa el flag --skip-var, hacer el reemplazo de variables de sustitucion secuencialmente
        final_content = process_file_sequentially(full_content, verbose=verbose)
        return final_content
    else:
        # Si se pasa el flag --skip-var, devolver solo el contenido combinado sin hacer sustituciones
        return full_content


# 4. Funciones para procesamiento de plantillas Jinja2
def process_jinja2_template(template_content, variables=None, strict_undefined=True, 
                           variable_start_string='{{', variable_end_string='}}'):
    """
    Procesa una plantilla Jinja2 con las variables proporcionadas.
    
    Args:
        template_content (str): Contenido de la plantilla Jinja2
        variables (dict): Diccionario con las variables para la plantilla
        strict_undefined (bool): Si True, lanza error para variables no definidas
        variable_start_string (str): Delimitador de inicio de variable
        variable_end_string (str): Delimitador de fin de variable
    
    Returns:
        str: Contenido renderizado
    
    Raises:
        TemplateError: Para errores de sintaxis o variables no definidas
    """
    if variables is None:
        variables = {}
    
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
        env.filters['sql_escape'] = sql_escape_filter
        env.filters['strftime'] = strftime_filter
        
        # Crear y renderizar la plantilla
        template = env.from_string(template_content)
        return template.render(**variables)
        
    except (TemplateSyntaxError, UndefinedError, TemplateError) as e:
        raise Exception(f"Error procesando plantilla Jinja2: {str(e)}")


def sql_escape_filter(value):
    """
    Filtro personalizado para escapar valores SQL (doble comilla simple).
    """
    if isinstance(value, str):
        return value.replace("'", "''")
    return str(value)


def strftime_filter(value, format_str='%Y-%m-%d'):
    """
    Filtro personalizado para formatear fechas usando strftime.
    """
    if hasattr(value, 'strftime'):
        return value.strftime(format_str)
    return str(value)


def process_file_with_jinja2_replacements(input_file, variables=None, skip_var=False, verbose=False, processing_order='default'):
    """
    Procesa un archivo con multiples estrategias de orden segun el caso de uso.
    
    Args:
        input_file (str): Ruta del archivo de entrada
        variables (dict): Variables para las plantillas Jinja2
        skip_var (bool): Si omitir el procesamiento de variables SQL
        verbose (bool): Modo detallado
        processing_order (str): Orden de procesamiento ('default', 'jinja2_first', 'includes_last')
    
    Returns:
        str: Contenido final procesado
    """
    if variables is None:
        variables = {}
    
    if processing_order == 'jinja2_first':
        # Orden: Jinja2 -> Inclusiones -> Variables SQL
        # util cuando las plantillas Jinja2 determinan que archivos incluir
        return _process_jinja2_first(input_file, variables, skip_var, verbose)
    elif processing_order == 'includes_last':
        # Orden: Variables SQL -> Jinja2 -> Inclusiones  
        # util cuando las variables SQL determinan las inclusiones
        return _process_includes_last(input_file, variables, skip_var, verbose)
    else:
        # Orden por defecto: Inclusiones -> Jinja2 -> Variables SQL
        # Mantiene compatibilidad con implementacion actual
        return _process_default_order(input_file, variables, skip_var, verbose)


def _process_default_order(input_file, variables, skip_var, verbose):
    """Orden: Inclusiones -> Jinja2 -> Variables SQL (comportamiento actual)"""
    # Primero resolver inclusiones @ y @@
    if verbose:
        print("Resolviendo inclusiones de archivos...")
    print("Arbol de inclusiones:")
    # Calcular la ruta base del archivo de entrada
    import os
    
    # Si input_file es relativo, usar el directorio actual como base_path
    # Si input_file es absoluto, usar su directorio padre
    if os.path.isabs(input_file):
        base_path = os.path.dirname(input_file)
    else:
        base_path = os.getcwd()
        
    full_content = parse_sqlplus_file(input_file, base_path, verbose=verbose)
    
    # Luego procesar plantillas Jinja2
    if verbose:
        print("Procesando plantillas Jinja2...")
    jinja2_content = process_jinja2_template(full_content, variables)
    
    # Finalmente procesar variables SQL si no se omite
    if not skip_var:
        if verbose:
            print("Procesando variables SQL...")
        final_content = process_file_sequentially(jinja2_content, verbose=verbose)
        return final_content
    else:
        return jinja2_content


def _process_jinja2_first(input_file, variables, skip_var, verbose):
    """Orden: Jinja2 -> Inclusiones -> Variables SQL"""
    # Primero leer el archivo principal sin resolver inclusiones
    if verbose:
        print("Leyendo archivo principal...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        main_content = f.read()
    
    # Procesar plantillas Jinja2 en el archivo principal
    if verbose:
        print("Procesando plantillas Jinja2 en archivo principal...")
    jinja2_main = process_jinja2_template(main_content, variables)
    
    # Crear archivo temporal en el mismo directorio que el archivo original
    # para que las rutas relativas funcionen correctamente
    import tempfile
    import os
    base_path = os.path.dirname(input_file)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False, 
                                   dir=base_path, encoding='utf-8') as temp_file:
        temp_file.write(jinja2_main)
        temp_path = temp_file.name
    
    try:
        # Ahora resolver inclusiones desde el archivo temporal
        if verbose:
            print("Resolviendo inclusiones de archivos...")
        print("Arbol de inclusiones:")
        full_content = parse_sqlplus_file(temp_path, base_path, verbose=verbose)
        
        # Finalmente procesar variables SQL si no se omite
        if not skip_var:
            if verbose:
                print("Procesando variables SQL...")
            final_content = process_file_sequentially(full_content, verbose=verbose)
            return final_content
        else:
            return full_content
    finally:
        # Limpiar archivo temporal
        os.unlink(temp_path)


def _process_includes_last(input_file, variables, skip_var, verbose):
    """Orden: Variables SQL -> Jinja2 -> Inclusiones"""
    # Primero leer el archivo principal
    if verbose:
        print("Leyendo archivo principal...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        main_content = f.read()
    
    # Procesar variables SQL primero (si no se omite)
    if not skip_var:
        if verbose:
            print("Procesando variables SQL...")
        sql_processed = process_file_sequentially(main_content, verbose=verbose)
    else:
        sql_processed = main_content
    
    # Luego procesar plantillas Jinja2
    if verbose:
        print("Procesando plantillas Jinja2...")
    jinja2_content = process_jinja2_template(sql_processed, variables)
    
    # Crear archivo temporal en el mismo directorio que el archivo original
    import tempfile
    import os
    base_path = os.path.dirname(input_file)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False, 
                                   dir=base_path, encoding='utf-8') as temp_file:
        temp_file.write(jinja2_content)
        temp_path = temp_file.name
    
    try:
        if verbose:
            print("Resolviendo inclusiones de archivos...")
        print("Arbol de inclusiones:")
        final_content = parse_sqlplus_file(temp_path, base_path, verbose=verbose)
        return final_content
    finally:
        os.unlink(temp_path)


def process_content_with_both_engines(content, variables=None, verbose=False):
    """
    Procesa contenido aplicando ambos motores de plantillas: Jinja2 y variables SQL.
    
    Args:
        content (str): Contenido a procesar
        variables (dict): Variables para Jinja2
        verbose (bool): Modo detallado
    
    Returns:
        str: Contenido procesado
    """
    if variables is None:
        variables = {}
    
    # Primero Jinja2
    jinja2_content = process_jinja2_template(content, variables)
    
    # Luego variables SQL
    final_content = process_file_sequentially(jinja2_content, verbose=verbose)
    
    return final_content


def load_config_from_toml(config_file='MKFSource.toml'):
    """
    Carga la configuración desde un archivo TOML.
    
    Args:
        config_file (str): Ruta al archivo de configuración TOML (por defecto: MKFSource.toml)
    
    Returns:
        dict: Diccionario con la configuración cargada
    
    Raises:
        FileNotFoundError: Si el archivo no existe
        ValueError: Si el archivo TOML es inválido
    """
    config_path = Path(config_file)
    current_dir = Path.cwd()
    
    if not config_path.exists():
        error_msg = [
            f"\n{'=' * 70}",
            f"ERROR: No se encontró el archivo de configuración",
            f"{'=' * 70}",
            f"",
            f"Archivo buscado: {config_file}",
            f"Directorio actual: {current_dir}",
            f"",
            f"Para usar MergeSourceFile, necesitas crear un archivo 'MKFSource.toml'",
            f"en el directorio desde donde ejecutas el comando.",
            f"",
            f"Ejemplo mínimo de MKFSource.toml:",
            f"",
            f"  [mergesourcefile]",
            f"  input = \"tu_archivo_entrada.sql\"",
            f"  output = \"archivo_salida.sql\"",
            f"",
            f"Para más información, consulta la documentación.",
            f"{'=' * 70}\n"
        ]
        raise FileNotFoundError('\n'.join(error_msg))
    
    try:
        with open(config_path, 'rb') as f:
            config = tomllib.load(f)
        
        # Validar que la configuración tenga la estructura esperada
        if 'mergesourcefile' not in config:
            error_msg = [
                f"\n{'=' * 70}",
                f"ERROR: Estructura de configuración inválida",
                f"{'=' * 70}",
                f"",
                f"El archivo '{config_file}' no contiene la sección [mergesourcefile].",
                f"",
                f"El archivo debe tener esta estructura:",
                f"",
                f"  [mergesourcefile]",
                f"  input = \"archivo.sql\"",
                f"  output = \"salida.sql\"",
                f"  # ... otras opciones ...",
                f"",
                f"{'=' * 70}\n"
            ]
            raise ValueError('\n'.join(error_msg))
        
        return config['mergesourcefile']
    
    except tomllib.TOMLDecodeError as e:
        error_msg = [
            f"\n{'=' * 70}",
            f"ERROR: Sintaxis TOML inválida",
            f"{'=' * 70}",
            f"",
            f"El archivo '{config_file}' contiene errores de sintaxis TOML.",
            f"",
            f"Detalles del error:",
            f"  {str(e)}",
            f"",
            f"Verifica que:",
            f"  - Las secciones usen corchetes: [mergesourcefile]",
            f"  - Los valores de texto estén entre comillas: input = \"archivo.sql\"",
            f"  - Los valores booleanos sean: true o false (sin comillas)",
            f"",
            f"{'=' * 70}\n"
        ]
        raise ValueError('\n'.join(error_msg))
    except FileNotFoundError:
        # Re-lanzar el FileNotFoundError ya formateado
        raise
    except ValueError:
        # Re-lanzar el ValueError ya formateado
        raise
    except Exception as e:
        error_msg = [
            f"\n{'=' * 70}",
            f"ERROR: No se pudo cargar la configuración",
            f"{'=' * 70}",
            f"",
            f"Ocurrió un error inesperado al cargar '{config_file}':",
            f"  {str(e)}",
            f"",
            f"{'=' * 70}\n"
        ]
        raise ValueError('\n'.join(error_msg))


# Función principal simplificada
def main():
    """
    Función principal que lee la configuración desde MKFSource.toml
    y procesa los archivos SQL según la configuración.
    """
    config_file = 'MKFSource.toml'
    
    try:
        # Cargar configuración desde el archivo TOML
        print(f"Cargando configuración desde: {config_file}")
        config = load_config_from_toml(config_file)
        
        # Extraer parámetros de la configuración
        input_file = config.get('input')
        output_file = config.get('output')
        skip_var = config.get('skip_var', False)
        verbose = config.get('verbose', False)
        jinja2_enabled = config.get('jinja2', False)
        jinja2_vars_file = config.get('jinja2_vars')
        processing_order = config.get('processing_order', 'default')
        
        # Validar parámetros requeridos
        missing_params = []
        if not input_file:
            missing_params.append('input')
        if not output_file:
            missing_params.append('output')
        
        if missing_params:
            error_msg = [
                f"\n{'=' * 70}",
                f"ERROR: Faltan parámetros requeridos en la configuración",
                f"{'=' * 70}",
                f"",
                f"Los siguientes parámetros son obligatorios y no están definidos:",
                f"  - " + "\n  - ".join(missing_params),
                f"",
                f"Tu archivo MKFSource.toml debe incluir:",
                f"",
                f"  [mergesourcefile]",
                f"  input = \"tu_archivo_entrada.sql\"",
                f"  output = \"archivo_salida.sql\"",
                f"",
                f"{'=' * 70}\n"
            ]
            raise ValueError('\n'.join(error_msg))
        
        # Cargar variables Jinja2 si se especifica
        jinja2_variables = {}
        if jinja2_vars_file:
            import json
            with open(jinja2_vars_file, 'r', encoding='utf-8') as f:
                jinja2_variables = json.load(f)
            if verbose:
                print(f"Variables Jinja2 cargadas desde: {jinja2_vars_file}")
        
        # Ejecutar el proceso según las opciones
        if jinja2_enabled:
            # Usar el procesamiento con Jinja2
            result = process_file_with_jinja2_replacements(
                input_file, 
                jinja2_variables, 
                skip_var, 
                verbose,
                processing_order
            )
        else:
            # Usar el procesamiento tradicional
            result = process_file_with_replacements(input_file, skip_var, verbose)

        # Escribir el resultado en el archivo de salida
        with open(output_file, 'w', encoding='utf-8') as output_file_handle:
            output_file_handle.write(result)

        print(f"Procesamiento completado. Resultado escrito en: {output_file}")
        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error de configuración: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error durante el procesamiento: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
