"""
Tests para config_loader - Carga y normalización de configuración.
"""
import pytest
from pathlib import Path
from MergeSourceFile.core import load_config


class TestConfigLoaderBasics:
    """Tests básicos de carga de configuración"""

    def test_load_hierarchical_config(self, temp_dir):
        """Test carga de configuración jerárquica moderna"""
        config_file = temp_dir / "config.toml"
        config_file.write_text("""
[project]
input = "input.sql"
output = "output.sql"
verbose = true
execution_order = ["jinja2", "sqlplus_includes", "sqlplus_vars"]

[plugins.sqlplus]
enabled = true
skip_var = false

[plugins.jinja2]
enabled = true
variables_file = "vars.json"
""", encoding='utf-8')

        config = load_config(str(config_file))

        assert config['project']['input'] == "input.sql"
        assert config['project']['output'] == "output.sql"
        assert config['project']['verbose'] is True
        assert config['plugins']['sqlplus']['enabled'] is True
        assert config['plugins']['jinja2']['variables_file'] == "vars.json"
        assert config['project']['execution_order'] == ["jinja2", "sqlplus_includes", "sqlplus_vars"]

    def test_missing_config_file_raises_error(self):
        """Test que archivo no existente lanza FileNotFoundError"""
        with pytest.raises(FileNotFoundError):
            load_config("nonexistent.toml")

    def test_invalid_toml_syntax_raises_error(self, temp_dir):
        """Test que sintaxis TOML inválida lanza error"""
        config_file = temp_dir / "bad.toml"
        config_file.write_text("this is [not valid toml", encoding='utf-8')

        with pytest.raises(Exception):  # tomllib.TOMLDecodeError
            load_config(str(config_file))


class TestConfigNormalization:
    """Tests para normalización de configuración"""

    def test_normalize_minimal_config(self, temp_dir):
        """Test normalización con configuración mínima"""
        config_file = temp_dir / "minimal.toml"
        config_file.write_text("""
[project]
input = "test.sql"
output = "output.sql"
""", encoding='utf-8')

        config = load_config(str(config_file))

        # Debe tener valores configurados
        assert config['project']['input'] == "test.sql"
        assert config['project']['output'] == "output.sql"
        assert config['project']['verbose'] is False
        # En el nuevo diseño, los plugins no se crean por defecto
        # solo existen si el usuario los configura explícitamente
        assert 'plugins' in config
        assert config['project']['execution_order'] == []

    def test_custom_execution_order_preserved(self, temp_dir):
        """Test que orden personalizado se preserva"""
        config_file = temp_dir / "custom.toml"
        config_file.write_text("""
[project]
input = "test.sql"
output = "output.sql"
execution_order = ["jinja2", "sqlplus_vars"]
""", encoding='utf-8')

        config = load_config(str(config_file))

        assert config['project']['execution_order'] == ['jinja2', 'sqlplus_vars']


class TestConfigValidation:
    """Tests para validación de configuración"""

    def test_missing_input_file_detected(self, temp_dir):
        """Test que falta input se detecta en validación"""
        config_file = temp_dir / "noinput.toml"
        config_file.write_text("""
[project]
output = "out.sql"
""", encoding='utf-8')

        # Debe lanzar ValueError porque falta input
        with pytest.raises(ValueError, match="falta parámetro 'input'"):
            load_config(str(config_file))

    def test_output_empty_string_is_rejected(self, temp_dir):
        """Test que output vacío es rechazado en la validación"""
        config_file = temp_dir / "emptyoutput.toml"
        config_file.write_text("""
[project]
input = "test.sql"
output = ""
""", encoding='utf-8')

        # Debe fallar la validación porque output está vacío
        with pytest.raises(ValueError, match="falta parámetro 'output'"):
            load_config(str(config_file))

    def test_jinja2_enabled_without_vars_file_allowed(self, temp_dir):
        """Test que Jinja2 sin variables_file es válido"""
        config_file = temp_dir / "jinja2.toml"
        config_file.write_text("""
[project]
input = "test.sql"
output = "output.sql"

[plugins.jinja2]
enabled = true
""", encoding='utf-8')

        config = load_config(str(config_file))

        assert config['plugins']['jinja2']['enabled'] is True
        assert config['plugins']['jinja2'].get('variables_file') is None

    def test_plugin_disabled_explicitly(self, temp_dir):
        """Test deshabilitar plugin explícitamente"""
        config_file = temp_dir / "disabled.toml"
        config_file.write_text("""
[project]
input = "test.sql"
output = "output.sql"

[plugins.sqlplus]
enabled = false
""", encoding='utf-8')

        config = load_config(str(config_file))

        assert config['plugins']['sqlplus']['enabled'] is False


class TestConfigEdgeCases:
    """Tests para casos límite"""

    def test_empty_config_file(self, temp_dir):
        """Test archivo de configuración vacío lanza error"""
        config_file = temp_dir / "empty.toml"
        config_file.write_text("", encoding='utf-8')

        # Debe lanzar error porque falta input
        with pytest.raises(ValueError, match="falta parámetro 'input'"):
            load_config(str(config_file))

    def test_config_with_comments(self, temp_dir):
        """Test que comentarios TOML se ignoran correctamente"""
        config_file = temp_dir / "comments.toml"
        config_file.write_text("""
# Este es un comentario
[project]
input = "test.sql"  # Comentario inline
# Otro comentario
output = "out.sql"
""", encoding='utf-8')

        config = load_config(str(config_file))

        assert config['project']['input'] == "test.sql"
        assert config['project']['output'] == "out.sql"

    def test_config_with_extra_fields_ignored(self, temp_dir):
        """Test que campos extra se ignoran sin error"""
        config_file = temp_dir / "extra.toml"
        config_file.write_text("""
[project]
input = "test.sql"
output = "output.sql"
unknown_field = "value"

[unknown_section]
foo = "bar"
""", encoding='utf-8')

        config = load_config(str(config_file))

        assert config['project']['input'] == "test.sql"
        # Los campos desconocidos pueden estar presentes pero no afectan
