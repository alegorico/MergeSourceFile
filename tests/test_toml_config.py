"""
Tests para configuración TOML de MergeSourceFile
"""
import pytest
import subprocess
import sys
import json
from pathlib import Path


class TestTomlConfig:
    """Tests para la configuración desde archivo TOML"""
    
    def test_config_file_basic(self, temp_dir):
        """Test básico para leer configuración desde archivo TOML"""
        # Crear archivo TOML de configuración
        config_file = temp_dir / "config.toml"
        config_content = """[mergesourcefile]
input = "input.sql"
output = "output.sql"
"""
        config_file.write_text(config_content, encoding='utf-8')
        
        # Crear archivo de entrada
        input_file = temp_dir / "input.sql"
        input_content = """-- Test file
SELECT sysdate FROM dual;
"""
        input_file.write_text(input_content, encoding='utf-8')
        
        # Ejecutar con --config
        result = subprocess.run([
            sys.executable, "-m", "MergeSourceFile.main",
            "--config", str(config_file)
        ], capture_output=True, text=True, cwd=str(temp_dir))
        
        assert result.returncode == 0
        
        # Verificar que el archivo de salida fue creado
        output_file = temp_dir / "output.sql"
        assert output_file.exists()
        output_content = output_file.read_text(encoding='utf-8')
        assert "SELECT sysdate FROM dual" in output_content
    
    def test_config_file_with_all_options(self, temp_dir):
        """Test para archivo TOML con todas las opciones"""
        # Crear archivo TOML de configuración
        config_file = temp_dir / "config.toml"
        config_content = """[mergesourcefile]
input = "input.sql"
output = "output.sql"
skip_var = true
verbose = true
"""
        config_file.write_text(config_content, encoding='utf-8')
        
        # Crear archivo de entrada
        input_file = temp_dir / "input.sql"
        input_content = """-- Test file
DEFINE var1=test_value
SELECT '&var1' FROM dual;
"""
        input_file.write_text(input_content, encoding='utf-8')
        
        # Ejecutar con --config
        result = subprocess.run([
            sys.executable, "-m", "MergeSourceFile.main",
            "--config", str(config_file)
        ], capture_output=True, text=True, cwd=str(temp_dir))
        
        assert result.returncode == 0
        
        # Verificar que el archivo de salida fue creado
        output_file = temp_dir / "output.sql"
        assert output_file.exists()
        
        # Verificar que skip_var funcionó (variable no reemplazada)
        output_content = output_file.read_text(encoding='utf-8')
        assert "&var1" in output_content
        
        # Verificar que verbose mode funcionó
        assert "[VERBOSE]" in result.stdout
    
    def test_config_file_with_jinja2(self, temp_dir):
        """Test para archivo TOML con opciones de Jinja2"""
        # Crear archivo TOML de configuración
        config_file = temp_dir / "config.toml"
        
        # Crear variables Jinja2
        jinja2_vars_file = temp_dir / "vars.json"
        jinja2_vars = {"table_name": "test_table", "schema": "test_schema"}
        jinja2_vars_file.write_text(json.dumps(jinja2_vars), encoding='utf-8')
        
        config_content = f"""[mergesourcefile]
input = "input.sql"
output = "output.sql"
jinja2 = true
jinja2_vars = "vars.json"
processing_order = "default"
"""
        config_file.write_text(config_content, encoding='utf-8')
        
        # Crear archivo de entrada con plantilla Jinja2
        input_file = temp_dir / "input.sql"
        input_content = """-- Test file with Jinja2
SELECT * FROM {{ schema }}.{{ table_name }};
"""
        input_file.write_text(input_content, encoding='utf-8')
        
        # Ejecutar con --config
        result = subprocess.run([
            sys.executable, "-m", "MergeSourceFile.main",
            "--config", str(config_file)
        ], capture_output=True, text=True, cwd=str(temp_dir))
        
        assert result.returncode == 0
        
        # Verificar que el archivo de salida fue creado con Jinja2 procesado
        output_file = temp_dir / "output.sql"
        assert output_file.exists()
        output_content = output_file.read_text(encoding='utf-8')
        assert "test_schema.test_table" in output_content
    
    def test_mutual_exclusivity_config_and_input(self, temp_dir):
        """Test para verificar exclusividad mutua entre --config y --input"""
        # Crear archivo TOML de configuración
        config_file = temp_dir / "config.toml"
        config_content = """[mergesourcefile]
input = "input.sql"
output = "output.sql"
"""
        config_file.write_text(config_content, encoding='utf-8')
        
        # Crear archivo de entrada
        input_file = temp_dir / "input.sql"
        input_file.write_text("SELECT 1;", encoding='utf-8')
        
        # Intentar ejecutar con --config y --input simultáneamente
        result = subprocess.run([
            sys.executable, "-m", "MergeSourceFile.main",
            "--config", str(config_file),
            "--input", str(input_file),
            "--output", "output.sql"
        ], capture_output=True, text=True, cwd=str(temp_dir))
        
        # Debe fallar con error
        assert result.returncode != 0
        # Verificar mensaje de error
        assert "no se pueden usar" in result.stderr or "cannot be used" in result.stderr
    
    def test_mutual_exclusivity_config_and_output(self, temp_dir):
        """Test para verificar exclusividad mutua entre --config y --output"""
        # Crear archivo TOML de configuración
        config_file = temp_dir / "config.toml"
        config_content = """[mergesourcefile]
input = "input.sql"
output = "output.sql"
"""
        config_file.write_text(config_content, encoding='utf-8')
        
        # Intentar ejecutar con --config y --output simultáneamente
        result = subprocess.run([
            sys.executable, "-m", "MergeSourceFile.main",
            "--config", str(config_file),
            "--output", "other_output.sql"
        ], capture_output=True, text=True, cwd=str(temp_dir))
        
        # Debe fallar con error
        assert result.returncode != 0
        # Verificar mensaje de error
        assert "no se pueden usar" in result.stderr or "cannot be used" in result.stderr
    
    def test_deprecation_warning_for_cli_params(self, temp_dir):
        """Test para verificar warning de deprecación en parámetros de línea de comandos"""
        # Crear archivo de entrada
        input_file = temp_dir / "input.sql"
        input_file.write_text("SELECT 1;", encoding='utf-8')
        
        # Archivo de salida
        output_file = temp_dir / "output.sql"
        
        # Ejecutar con parámetros de línea de comandos tradicionales
        result = subprocess.run([
            sys.executable, "-m", "MergeSourceFile.main",
            "--input", str(input_file),
            "--output", str(output_file)
        ], capture_output=True, text=True)
        
        # Debe completar exitosamente
        assert result.returncode == 0
        
        # Debe mostrar warning de deprecación
        assert "WARNING" in result.stderr or "ADVERTENCIA" in result.stderr or "descontinuad" in result.stderr
    
    def test_config_file_not_found(self, temp_dir):
        """Test para manejo de archivo de configuración inexistente"""
        # Intentar ejecutar con archivo de configuración inexistente
        result = subprocess.run([
            sys.executable, "-m", "MergeSourceFile.main",
            "--config", str(temp_dir / "nonexistent.toml")
        ], capture_output=True, text=True)
        
        # Debe fallar con error
        assert result.returncode != 0
        assert "no encontrado" in result.stdout or "not found" in result.stdout
    
    def test_invalid_toml_syntax(self, temp_dir):
        """Test para manejo de sintaxis TOML inválida"""
        # Crear archivo TOML con sintaxis inválida
        config_file = temp_dir / "invalid.toml"
        config_file.write_text("This is not valid TOML syntax {{{", encoding='utf-8')
        
        # Intentar ejecutar con archivo de configuración inválido
        result = subprocess.run([
            sys.executable, "-m", "MergeSourceFile.main",
            "--config", str(config_file)
        ], capture_output=True, text=True)
        
        # Debe fallar con error
        assert result.returncode != 0
        assert "TOML" in result.stdout or "configuraci" in result.stdout
    
    def test_missing_required_fields_in_toml(self, temp_dir):
        """Test para manejo de campos requeridos faltantes en TOML"""
        # Crear archivo TOML sin campos requeridos
        config_file = temp_dir / "incomplete.toml"
        config_content = """[mergesourcefile]
# Missing input and output
skip_var = true
"""
        config_file.write_text(config_content, encoding='utf-8')
        
        # Intentar ejecutar con archivo de configuración incompleto
        result = subprocess.run([
            sys.executable, "-m", "MergeSourceFile.main",
            "--config", str(config_file)
        ], capture_output=True, text=True)
        
        # Debe fallar con error
        assert result.returncode != 0
        assert "input" in result.stdout or "output" in result.stdout
    
    def test_config_short_option(self, temp_dir):
        """Test para verificar que -c funciona como abreviación de --config"""
        # Crear archivo TOML de configuración
        config_file = temp_dir / "config.toml"
        config_content = """[mergesourcefile]
input = "input.sql"
output = "output.sql"
"""
        config_file.write_text(config_content, encoding='utf-8')
        
        # Crear archivo de entrada
        input_file = temp_dir / "input.sql"
        input_file.write_text("SELECT 1 FROM dual;", encoding='utf-8')
        
        # Ejecutar con -c (versión corta)
        result = subprocess.run([
            sys.executable, "-m", "MergeSourceFile.main",
            "-c", str(config_file)
        ], capture_output=True, text=True, cwd=str(temp_dir))
        
        assert result.returncode == 0
        
        # Verificar que el archivo de salida fue creado
        output_file = temp_dir / "output.sql"
        assert output_file.exists()
    
    def test_config_with_relative_paths(self, temp_dir):
        """Test para verificar que las rutas relativas en TOML funcionan correctamente"""
        # Crear subdirectorio
        subdir = temp_dir / "sql_files"
        subdir.mkdir()
        
        # Crear archivo TOML de configuración en el directorio raíz
        config_file = temp_dir / "config.toml"
        config_content = """[mergesourcefile]
input = "sql_files/input.sql"
output = "sql_files/output.sql"
"""
        config_file.write_text(config_content, encoding='utf-8')
        
        # Crear archivo de entrada en subdirectorio
        input_file = subdir / "input.sql"
        input_file.write_text("SELECT 1 FROM dual;", encoding='utf-8')
        
        # Ejecutar con --config desde el directorio raíz
        result = subprocess.run([
            sys.executable, "-m", "MergeSourceFile.main",
            "--config", str(config_file)
        ], capture_output=True, text=True, cwd=str(temp_dir))
        
        assert result.returncode == 0
        
        # Verificar que el archivo de salida fue creado en el subdirectorio
        output_file = subdir / "output.sql"
        assert output_file.exists()
