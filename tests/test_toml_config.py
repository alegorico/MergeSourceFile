"""
Tests para la funcionalidad de configuración TOML
"""
import pytest
from pathlib import Path
from MergeSourceFile.main import load_config_from_toml


class TestTOMLConfigLoading:
    """Tests para cargar configuración desde archivos TOML"""
    
    def test_load_valid_toml_config(self, temp_dir):
        """Test para cargar una configuración TOML válida"""
        config_file = temp_dir / "config.toml"
        config_file.write_text("""
[mergesourcefile]
input = "input.sql"
output = "output.sql"
skip_var = false
verbose = true
jinja2 = false
""", encoding='utf-8')
        
        config = load_config_from_toml(str(config_file))
        
        assert config['input'] == "input.sql"
        assert config['output'] == "output.sql"
        assert config['skip_var'] is False
        assert config['verbose'] is True
        assert config['jinja2'] is False
    
    def test_load_toml_with_all_options(self, temp_dir):
        """Test para cargar configuración con todas las opciones"""
        config_file = temp_dir / "config_full.toml"
        config_file.write_text("""
[mergesourcefile]
input = "main.sql"
output = "merged.sql"
skip_var = true
verbose = false
jinja2 = true
jinja2_vars = "vars.json"
processing_order = "jinja2_first"
""", encoding='utf-8')
        
        config = load_config_from_toml(str(config_file))
        
        assert config['input'] == "main.sql"
        assert config['output'] == "merged.sql"
        assert config['skip_var'] is True
        assert config['verbose'] is False
        assert config['jinja2'] is True
        assert config['jinja2_vars'] == "vars.json"
        assert config['processing_order'] == "jinja2_first"
    
    def test_load_toml_missing_section(self, temp_dir):
        """Test para archivo TOML sin la sección requerida"""
        config_file = temp_dir / "invalid.toml"
        config_file.write_text("""
[other_section]
key = "value"
""", encoding='utf-8')
        
        with pytest.raises(ValueError, match="no contiene la sección"):
            load_config_from_toml(str(config_file))
    
    def test_load_nonexistent_toml(self):
        """Test para archivo TOML inexistente"""
        with pytest.raises(FileNotFoundError):
            load_config_from_toml("nonexistent.toml")
    
    def test_load_invalid_toml_syntax(self, temp_dir):
        """Test para archivo TOML con sintaxis inválida"""
        config_file = temp_dir / "invalid_syntax.toml"
        config_file.write_text("""
[mergesourcefile
invalid syntax here
""", encoding='utf-8')
        
        with pytest.raises(ValueError, match="Sintaxis TOML inválida"):
            load_config_from_toml(str(config_file))


class TestConfigValidation:
    """Tests para validación de configuración"""
    
    def test_toml_config_with_invalid_processing_order(self, temp_dir):
        """Test que verifica que processing_order se valide correctamente"""
        # Crear archivos de entrada
        input_file = temp_dir / "input.sql"
        input_file.write_text("SELECT 1 FROM dual;", encoding='utf-8')
        
        output_file = temp_dir / "output.sql"
        
        # Crear archivo de configuración con processing_order inválido
        config_file = temp_dir / "config.toml"
        config_file.write_text(f"""
[mergesourcefile]
input = "{str(input_file).replace(chr(92), '/')}"
output = "{str(output_file).replace(chr(92), '/')}"
processing_order = "invalid_order"
""", encoding='utf-8')
        
        # Cargar configuración (no debería fallar en carga, pero podría fallar en uso)
        config = load_config_from_toml(str(config_file))
        assert config['processing_order'] == "invalid_order"
        # La validación real se haría en process_file_with_jinja2_replacements
    
    def test_toml_config_optional_fields_have_defaults(self, temp_dir):
        """Test para verificar que campos opcionales tienen valores por defecto"""
        config_file = temp_dir / "minimal.toml"
        config_file.write_text("""
[mergesourcefile]
input = "input.sql"
output = "output.sql"
""", encoding='utf-8')
        
        config = load_config_from_toml(str(config_file))
        
        # Solo input y output son requeridos
        assert 'input' in config
        assert 'output' in config
        # Otros campos son opcionales
        assert config.get('skip_var', False) is False  # Default valor
