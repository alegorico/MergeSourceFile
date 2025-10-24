"""
Tests para el motor de plantillas TemplateEngine.

Tests para la funcionalidad core de Jinja2 y sistema de extensiones.
"""
import pytest
import json
from pathlib import Path


class TestTemplateEngine:
    """Tests para la clase TemplateEngine"""

    def test_engine_initialization_basic(self):
        """Test que el motor se inicializa con configuración básica"""
        from MergeSourceFile.template_engine import TemplateEngine
        
        config = {
            'project': {'input': 'test.sql', 'output': 'out.sql'},
            'jinja2': {'enabled': True}
        }
        
        engine = TemplateEngine(config)
        
        assert engine.config == config
        assert engine.jinja_config == {'enabled': True}
        assert len(engine.extension_manager.get_extension_names()) == 0

    def test_engine_loads_sqlplus_extension(self):
        """Test que el motor carga la extensión sqlplus cuando está configurada"""
        from MergeSourceFile.template_engine import TemplateEngine
        
        config = {
            'project': {'input': 'test.sql', 'output': 'out.sql'},
            'jinja2': {
                'enabled': True,
                'extensions': ['sqlplus']
            }
        }
        
        engine = TemplateEngine(config)
        
        assert engine.extension_manager.has_extensions()
        assert 'sqlplus' in engine.extension_manager.get_extension_names()

    def test_engine_warns_on_unknown_extension(self):
        """Test que el motor lanza error con extensiones desconocidas"""
        from MergeSourceFile.template_engine import TemplateEngine
        
        config = {
            'project': {'input': 'test.sql', 'output': 'out.sql'},
            'jinja2': {
                'enabled': True,
                'extensions': ['unknown_extension']
            }
        }
        
        with pytest.raises(ValueError, match="Extensión no registrada"):
            TemplateEngine(config)

    def test_process_simple_template(self, temp_dir):
        """Test procesamiento de plantilla Jinja2 simple"""
        from MergeSourceFile.template_engine import TemplateEngine
        
        # Crear archivo de entrada
        input_file = temp_dir / "input.sql"
        input_file.write_text("SELECT {{ value }} FROM dual;", encoding='utf-8')
        
        config = {
            'project': {'input': str(input_file), 'output': 'out.sql'},
            'jinja2': {'enabled': True}
        }
        
        engine = TemplateEngine(config)
        result = engine.process_file(str(input_file), {'value': 42})
        
        assert result == "SELECT 42 FROM dual;"

    def test_process_template_with_multiple_variables(self, temp_dir):
        """Test procesamiento con múltiples variables"""
        from MergeSourceFile.template_engine import TemplateEngine
        
        input_file = temp_dir / "input.sql"
        input_file.write_text("SELECT {{ col1 }}, {{ col2 }} FROM {{ table }};", encoding='utf-8')
        
        config = {
            'project': {'input': str(input_file), 'output': 'out.sql'},
            'jinja2': {'enabled': True}
        }
        
        engine = TemplateEngine(config)
        result = engine.process_file(
            str(input_file),
            {'col1': 'id', 'col2': 'name', 'table': 'users'}
        )
        
        assert result == "SELECT id, name FROM users;"

    def test_process_template_with_control_structures(self, temp_dir):
        """Test procesamiento con estructuras de control Jinja2"""
        from MergeSourceFile.template_engine import TemplateEngine
        
        input_file = temp_dir / "input.sql"
        input_file.write_text("""
{% for item in items %}
SELECT {{ item }};
{% endfor %}
""".strip(), encoding='utf-8')
        
        config = {
            'project': {'input': str(input_file), 'output': 'out.sql'},
            'jinja2': {'enabled': True}
        }
        
        engine = TemplateEngine(config)
        result = engine.process_file(str(input_file), {'items': [1, 2, 3]})
        
        assert "SELECT 1;" in result
        assert "SELECT 2;" in result
        assert "SELECT 3;" in result

    def test_sql_escape_filter(self, temp_dir):
        """Test filtro personalizado sql_escape"""
        from MergeSourceFile.template_engine import TemplateEngine
        
        input_file = temp_dir / "input.sql"
        input_file.write_text("SELECT {{ value | sql_escape }};", encoding='utf-8')
        
        config = {
            'project': {'input': str(input_file), 'output': 'out.sql'},
            'jinja2': {'enabled': True}
        }
        
        engine = TemplateEngine(config)
        result = engine.process_file(str(input_file), {'value': "O'Reilly"})
        
        assert result == "SELECT O''Reilly;"

    def test_strftime_filter(self, temp_dir):
        """Test filtro personalizado strftime"""
        from MergeSourceFile.template_engine import TemplateEngine
        from datetime import datetime
        
        input_file = temp_dir / "input.sql"
        input_file.write_text("SELECT '{{ date | strftime }}';", encoding='utf-8')
        
        config = {
            'project': {'input': str(input_file), 'output': 'out.sql'},
            'jinja2': {'enabled': True}
        }
        
        engine = TemplateEngine(config)
        test_date = datetime(2025, 10, 24)
        result = engine.process_file(str(input_file), {'date': test_date})
        
        assert result == "SELECT '2025-10-24';"

    def test_custom_variable_delimiters(self, temp_dir):
        """Test delimitadores personalizados de variables"""
        from MergeSourceFile.template_engine import TemplateEngine
        
        input_file = temp_dir / "input.sql"
        input_file.write_text("SELECT {[ value ]} FROM dual;", encoding='utf-8')
        
        config = {
            'project': {'input': str(input_file), 'output': 'out.sql'},
            'jinja2': {
                'enabled': True,
                'variable_start_string': '{[',
                'variable_end_string': ']}'
            }
        }
        
        engine = TemplateEngine(config)
        result = engine.process_file(str(input_file), {'value': 42})
        
        assert result == "SELECT 42 FROM dual;"

    def test_strict_undefined_raises_error(self, temp_dir):
        """Test que strict_undefined lanza error en variables no definidas"""
        from MergeSourceFile.template_engine import TemplateEngine
        
        input_file = temp_dir / "input.sql"
        input_file.write_text("SELECT {{ undefined_var }} FROM dual;", encoding='utf-8')
        
        config = {
            'project': {'input': str(input_file), 'output': 'out.sql'},
            'jinja2': {
                'enabled': True,
                'strict_undefined': True
            }
        }
        
        engine = TemplateEngine(config)
        
        with pytest.raises(Exception, match="undefined_var"):
            engine.process_file(str(input_file), {})

    def test_process_with_sqlplus_extension(self, temp_dir):
        """Test procesamiento con extensión SQLPlus habilitada"""
        from MergeSourceFile.template_engine import TemplateEngine
        
        # Crear archivo incluido
        included = temp_dir / "included.sql"
        included.write_text("SELECT 'from_include';", encoding='utf-8')
        
        # Crear archivo principal con inclusión
        input_file = temp_dir / "main.sql"
        input_file.write_text(f"@{included.name}\nSELECT '{{{{ value }}}}';\n", encoding='utf-8')
        
        config = {
            'project': {'input': str(input_file), 'output': 'out.sql'},
            'jinja2': {
                'enabled': True,
                'extensions': ['sqlplus'],
                'sqlplus': {
                    'process_includes': True,
                    'process_defines': False
                }
            }
        }
        
        engine = TemplateEngine(config)
        result = engine.process_file(str(input_file), {'value': 'jinja2_value'})
        
        # Verificar que la extensión SQLPlus procesó la inclusión
        assert "SELECT 'from_include';" in result
        # Verificar que Jinja2 procesó las variables
        assert "SELECT 'jinja2_value';" in result

    def test_process_file_not_found(self):
        """Test que se lanza error cuando el archivo no existe"""
        from MergeSourceFile.template_engine import TemplateEngine
        
        config = {
            'project': {'input': 'nonexistent.sql', 'output': 'out.sql'},
            'jinja2': {'enabled': True}
        }
        
        engine = TemplateEngine(config)
        
        with pytest.raises(FileNotFoundError):
            engine.process_file('nonexistent.sql', {})

    def test_template_syntax_error(self, temp_dir):
        """Test que se reportan errores de sintaxis Jinja2"""
        from MergeSourceFile.template_engine import TemplateEngine
        
        input_file = temp_dir / "input.sql"
        input_file.write_text("SELECT {{ unclosed", encoding='utf-8')
        
        config = {
            'project': {'input': str(input_file), 'output': 'out.sql'},
            'jinja2': {'enabled': True}
        }
        
        engine = TemplateEngine(config)
        
        with pytest.raises(Exception, match="Jinja2"):
            engine.process_file(str(input_file), {})
