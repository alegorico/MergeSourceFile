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
Módulo de entrada/salida de recursos del sistema de archivos.

Proporciona clases para lectura (ResourceLoader) y escritura (ResourceWriter)
de archivos, con soporte para diferentes formatos y codificaciones.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ResourceLoader:
    """
    Cargador unificado de recursos del sistema de archivos.
    """
    
    @staticmethod
    def read_text_file(file_path: str, encoding: str = 'utf-8') -> str:
        """
        Lee un archivo de texto.
        
        Args:
            file_path: Ruta al archivo
            encoding: Codificación del archivo
        
        Returns:
            Contenido del archivo como string
        
        Raises:
            FileNotFoundError: Si el archivo no existe
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
        
        return path.read_text(encoding=encoding)
    
    @staticmethod
    def read_json_file(file_path: str, encoding: str = 'utf-8') -> Dict[str, Any]:
        """
        Lee un archivo JSON.
        
        Args:
            file_path: Ruta al archivo JSON
            encoding: Codificación del archivo
        
        Returns:
            Contenido parseado como diccionario
        
        Raises:
            FileNotFoundError: Si el archivo no existe
            ValueError: Si el JSON es inválido
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
        
        try:
            with path.open('r', encoding=encoding) as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error al parsear JSON en {file_path}: {str(e)}")
    
    @staticmethod
    def write_text_file(file_path: str, content: str, encoding: str = 'utf-8') -> None:
        """
        Escribe contenido en un archivo de texto.
        
        Args:
            file_path: Ruta al archivo
            content: Contenido a escribir
            encoding: Codificación del archivo
        
        Raises:
            ValueError: Si file_path está vacío
        """
        if not file_path or not file_path.strip():
            raise ValueError("El parámetro 'file_path' no puede estar vacío")
        
        path = Path(file_path)
        path.write_text(content, encoding=encoding)
    
    @staticmethod
    def resolve_path(file_path: str, base_path: str = None) -> Path:
        """
        Resuelve una ruta de archivo (absoluta o relativa).
        
        Args:
            file_path: Ruta del archivo
            base_path: Ruta base para rutas relativas
        
        Returns:
            Path resuelto
        """
        path = Path(file_path)
        
        if path.is_absolute():
            return path
        
        if base_path:
            return Path(base_path) / path
        
        return Path.cwd() / path


class ResourceWriter:
    """
    Escritor de recursos con conocimiento del destino final.
    
    Esta clase encapsula la lógica de escritura de archivos de salida,
    permitiendo extensiones como validación, backup, o diferentes formatos.
    """
    
    def __init__(self, output_path: str, encoding: str = 'utf-8', 
                 create_backup: bool = False, base_path: Optional[str] = None):
        """
        Inicializa el escritor de recursos.
        
        Args:
            output_path: Ruta del archivo de destino
            encoding: Codificación del archivo (por defecto utf-8)
            create_backup: Si crear backup del archivo existente antes de sobrescribir
            base_path: Ruta base para resolver rutas relativas
        """
        if not output_path or not output_path.strip():
            raise ValueError("El parámetro 'output_path' no puede estar vacío")
        
        self.output_path = output_path
        self.encoding = encoding
        self.create_backup = create_backup
        self.base_path = base_path
        self._resolved_path = self._resolve_output_path()
    
    def _resolve_output_path(self) -> Path:
        """
        Resuelve la ruta de salida (absoluta o relativa).
        
        Returns:
            Path resuelto del archivo de salida
        """
        return ResourceLoader.resolve_path(self.output_path, self.base_path)
    
    def write(self, content: str) -> None:
        """
        Escribe el contenido en el archivo de destino.
        
        Args:
            content: Contenido a escribir
        
        Raises:
            IOError: Si hay error al escribir el archivo
        """
        try:
            # Crear backup si está habilitado y el archivo existe
            if self.create_backup and self._resolved_path.exists():
                self._create_backup()
            
            # Crear directorio si no existe
            self._resolved_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Escribir contenido
            self._resolved_path.write_text(content, encoding=self.encoding)
            
            logger.debug(f"Archivo escrito correctamente: {self._resolved_path}")
            
        except Exception as e:
            raise IOError(f"Error al escribir archivo {self._resolved_path}: {str(e)}")
    
    def _create_backup(self) -> None:
        """
        Crea una copia de backup del archivo existente.
        """
        backup_path = self._resolved_path.with_suffix(
            self._resolved_path.suffix + '.backup'
        )
        try:
            backup_path.write_text(
                self._resolved_path.read_text(encoding=self.encoding),
                encoding=self.encoding
            )
            logger.info(f"Backup creado: {backup_path}")
        except Exception as e:
            logger.warning(f"No se pudo crear backup: {str(e)}")
    
    def get_output_path(self) -> Path:
        """
        Retorna la ruta resuelta del archivo de salida.
        
        Returns:
            Path del archivo de salida
        """
        return self._resolved_path
    
    def __str__(self) -> str:
        """Representación en string del writer."""
        return f"ResourceWriter(output={self._resolved_path})"
    
    def __repr__(self) -> str:
        """Representación para debugging."""
        return (f"ResourceWriter(output_path='{self.output_path}', "
                f"encoding='{self.encoding}', create_backup={self.create_backup})")
