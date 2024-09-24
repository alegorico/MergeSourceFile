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
import argparse
from pathlib import Path


# 1. Función para leer y resolver inclusiones @ y @@
def parse_sqlplus_file(input_file, base_path='.'):
    
    def read_file(file_path, base_path):
        full_path = Path(base_path) / file_path
        if not full_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {full_path}")
            
        content = ""
        with full_path.open('r') as f:
            for line in f:
                line = line.rstrip()
                if line.startswith('@@'):
                    nested_file_path = line[2:].strip()
                    content += read_file(nested_file_path, full_path.parent) + '\n'
                elif line.startswith('@'):
                    nested_file_path = line[1:].strip()
                    content += read_file(nested_file_path, base_path) + '\n'
                else:
                    content += line + '\n'
        return content
        
    base_path = Path(base_path)
    return read_file(input_file, base_path)


# 2. Función para reemplazar variables en el archivo con evaluación de orden
def process_file_sequentially(file_content):
    defines = {}
    replaced_content = []
    define_pattern = re.compile(r'^define\s+(\w+)\s*=\s*\'(.*?)\'\s*;\s*$', re.IGNORECASE)
    undefine_pattern = re.compile(r'^undefine\s+(\w+)\s*;\s*$', re.IGNORECASE)
    variable_pattern = re.compile(r"(&\w+)(\.\.)?")

    for line_number, line in enumerate(file_content.splitlines(), 1):
        clean = line.rstrip()

        # Si es un comentario, simplemente lo agregamos sin procesar
        if clean.lstrip().startswith('--'):
            replaced_content.append(line)
            continue

        # Si es una línea DEFINE, la registramos o redefinimos
        match_define = define_pattern.match(clean)
        if match_define:
            var_name = match_define.group(1)
            var_value = match_define.group(2)
            defines[var_name] = var_value  # Redefinición permitida
            continue  # No agregar la línea DEFINE al resultado final

        # Si es una línea UNDEFINE, eliminamos la variable
        match_undefine = undefine_pattern.match(clean)
        if match_undefine:
            var_name = match_undefine.group(1)
            if var_name in defines:
                del defines[var_name]  # Eliminar la variable del diccionario
            continue  # No agregar la línea UNDEFINE al resultado final

        # Si no es un DEFINE ni UNDEFINE, verificamos si hay variables que deben ser reemplazadas
        all_matches = variable_pattern.findall(clean)

        # Revisar cada variable usada en la línea
        replaced_line = clean
        for match in all_matches:
            var_name = match[0][1:]  # Nombre de la variable sin el símbolo '&'
            if var_name not in defines:
                raise ValueError(f"Error: La variable '{var_name}' se usa antes de ser definida (línea {line_number}).")
            value = defines[var_name]
            if match[1]:  # Si tiene puntos concatenados (..)
                replaced_line = replaced_line.replace(match[0] + "..", value + ".")
            else:
                replaced_line = replaced_line.replace(match[0], value)

        replaced_content.append(replaced_line)

    return "\n".join(replaced_content)


# 3. Función que combina todo el proceso
def process_file_with_replacements(input_file, full_process=False):
    # Siempre resolveremos las inclusiones @ y @@
    full_content = parse_sqlplus_file(input_file)

    if full_process:
        # Si se pasa el flag --full-process, hacer el reemplazo de variables de sustitución secuencialmente
        final_content = process_file_sequentially(full_content)
        return final_content
    else:
        # Si NO se pasa el flag --full-process, devolver solo el contenido combinado sin hacer sustituciones
        return full_content


# 4. Configuración de argparse y ejecución
def main():
    parser = argparse.ArgumentParser(description='Procesa un script de SQL*Plus con o sin resolución de inclusiones.')
    
    # Argumentos
    parser.add_argument('input_file', help='El archivo de entrada a procesar')
    parser.add_argument('--full-process', action='store_true',
                        help='Realiza el proceso completo: resuelve inclusiones @ y @@, luego reemplaza variables de sustitución.')

    args = parser.parse_args()

    try:
        # Ejecutar el proceso completo o parcial
        result = process_file_with_replacements(args.input_file, args.full_process)
        print(result)
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except ValueError as e:
        print(f"Error de procesamiento: {e}")


if __name__ == '__main__':
    main()
