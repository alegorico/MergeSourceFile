"""
Tests para plugins SQL*Plus - SQLPlusIncludesPlugin y SQLPlusVarsPlugin.
"""
import pytest
from pathlib import Path
from MergeSourceFile import ProcessingContext
from MergeSourceFile.plugins import get_available_plugins

# Get plugin classes
PLUGINS = get_available_plugins()
SQLPlusIncludesPlugin = PLUGINS['sqlplus_includes']
SQLPlusVarsPlugin = PLUGINS['sqlplus_vars']


class TestSQLPlusIncludesPlugin:
    """Tests para SQLPlusIncludesPlugin"""

    def test_plugin_name(self):
        """Test que plugin tiene el nombre correcto"""
        plugin = SQLPlusIncludesPlugin({})
        assert plugin.name == "sqlplus_includes"

    def test_plugin_enabled_by_default(self):
        """Test que plugin está habilitado por defecto"""
        plugin = SQLPlusIncludesPlugin({})
        assert plugin.is_enabled() is True

    def test_plugin_can_be_disabled(self):
        """Test que plugin se puede deshabilitar"""
        plugin = SQLPlusIncludesPlugin({'enabled': False})
        assert plugin.is_enabled() is False

    def test_simple_file_without_includes(self, temp_dir):
        """Test archivo simple sin inclusiones"""
        main_file = temp_dir / "main.sql"
        main_file.write_text("SELECT 1 FROM dual;", encoding='utf-8')

        plugin = SQLPlusIncludesPlugin({})
        context = ProcessingContext()
        context.input_file = str(main_file)
        context.base_path = temp_dir

        result = plugin.process(context)

        assert "SELECT 1 FROM dual;" in result.content

    def test_file_with_single_at_include(self, temp_dir):
        """Test inclusión con @ (relativo a archivo actual)"""
        # Archivo incluido
        included = temp_dir / "included.sql"
        included.write_text("-- Included content\nSELECT 'included';", encoding='utf-8')

        # Archivo principal
        main_file = temp_dir / "main.sql"
        main_file.write_text("@included.sql\nSELECT 'main';", encoding='utf-8')

        plugin = SQLPlusIncludesPlugin({})
        context = ProcessingContext()
        context.input_file = str(main_file)
        context.base_path = temp_dir

        result = plugin.process(context)

        assert "-- Included content" in result.content
        assert "SELECT 'included';" in result.content
        assert "SELECT 'main';" in result.content
        assert result.content.index("included") < result.content.index("main")

    def test_file_with_double_at_include(self, temp_dir):
        """Test inclusión con @@ (relativo a script inicial)"""
        # Archivo incluido
        included = temp_dir / "included.sql"
        included.write_text("SELECT 'double at';", encoding='utf-8')

        # Archivo principal
        main_file = temp_dir / "main.sql"
        main_file.write_text("@@included.sql", encoding='utf-8')

        plugin = SQLPlusIncludesPlugin({})
        context = ProcessingContext()
        context.input_file = str(main_file)
        context.base_path = temp_dir

        result = plugin.process(context)

        assert "SELECT 'double at';" in result.content

    def test_nested_includes(self, temp_dir):
        """Test inclusiones anidadas"""
        # Level 2
        level2 = temp_dir / "level2.sql"
        level2.write_text("SELECT 'level2';", encoding='utf-8')

        # Level 1 incluye a level2
        level1 = temp_dir / "level1.sql"
        level1.write_text("@level2.sql\nSELECT 'level1';", encoding='utf-8')

        # Main incluye a level1
        main_file = temp_dir / "main.sql"
        main_file.write_text("@level1.sql\nSELECT 'main';", encoding='utf-8')

        plugin = SQLPlusIncludesPlugin({})
        context = ProcessingContext()
        context.input_file = str(main_file)
        context.base_path = temp_dir

        result = plugin.process(context)

        assert "SELECT 'level2';" in result.content
        assert "SELECT 'level1';" in result.content
        assert "SELECT 'main';" in result.content
        # Orden: level2 -> level1 -> main
        assert result.content.index("level2") < result.content.index("level1")
        assert result.content.index("level1") < result.content.index("main")

    def test_nonexistent_include_raises_error(self, temp_dir):
        """Test que archivo incluido inexistente lanza error"""
        main_file = temp_dir / "main.sql"
        main_file.write_text("@nonexistent.sql", encoding='utf-8')

        plugin = SQLPlusIncludesPlugin({})
        context = ProcessingContext()
        context.input_file = str(main_file)
        context.base_path = temp_dir

        with pytest.raises(FileNotFoundError):
            plugin.process(context)

    def test_multiple_includes_same_file(self, temp_dir):
        """Test incluir el mismo archivo múltiples veces"""
        included = temp_dir / "common.sql"
        included.write_text("SELECT 'common';", encoding='utf-8')

        main_file = temp_dir / "main.sql"
        main_file.write_text("@common.sql\n@common.sql", encoding='utf-8')

        plugin = SQLPlusIncludesPlugin({})
        context = ProcessingContext()
        context.input_file = str(main_file)
        context.base_path = temp_dir

        result = plugin.process(context)

        # El archivo debe incluirse dos veces
        assert result.content.count("SELECT 'common';") == 2

    def test_include_with_comments(self, temp_dir):
        """Test que comentarios se preservan"""
        included = temp_dir / "with_comments.sql"
        included.write_text("-- Comment in included\nSELECT 1;", encoding='utf-8')

        main_file = temp_dir / "main.sql"
        main_file.write_text("-- Main comment\n@with_comments.sql", encoding='utf-8')

        plugin = SQLPlusIncludesPlugin({})
        context = ProcessingContext()
        context.input_file = str(main_file)
        context.base_path = temp_dir

        result = plugin.process(context)

        assert "-- Main comment" in result.content
        assert "-- Comment in included" in result.content


class TestSQLPlusVarsPlugin:
    """Tests para SQLPlusVarsPlugin"""

    def test_plugin_name(self):
        """Test que plugin tiene el nombre correcto"""
        plugin = SQLPlusVarsPlugin({})
        assert plugin.name == "sqlplus_vars"

    def test_plugin_enabled_by_default(self):
        """Test que plugin está habilitado por defecto"""
        plugin = SQLPlusVarsPlugin({})
        assert plugin.is_enabled() is True

    def test_plugin_respects_skip_var(self):
        """Test que skip_var=True hace que el plugin esté habilitado pero no procese"""
        plugin = SQLPlusVarsPlugin({'skip_var': True})
        # El plugin sigue habilitado, pero skip_var indica que no debe procesar
        assert plugin.config.get('skip_var') is True

    def test_simple_define_substitution(self):
        """Test sustitución simple de DEFINE"""
        content = """DEFINE var1='value1'
SELECT '&var1';"""

        plugin = SQLPlusVarsPlugin({})
        context = ProcessingContext()
        context.content = content

        result = plugin.process(context)

        assert "SELECT 'value1';" in result.content
        assert "DEFINE" not in result.content

    def test_define_without_quotes(self):
        """Test DEFINE sin comillas (valores simples)"""
        content = """DEFINE num=123
DEFINE name=john
SELECT &num, '&name';"""

        plugin = SQLPlusVarsPlugin({})
        context = ProcessingContext()
        context.content = content

        result = plugin.process(context)

        assert "SELECT 123, 'john';" in result.content

    def test_define_with_quotes(self):
        """Test DEFINE con comillas (valores con espacios)"""
        content = """DEFINE msg='Hello World'
SELECT '&msg';"""

        plugin = SQLPlusVarsPlugin({})
        context = ProcessingContext()
        context.content = content

        result = plugin.process(context)

        assert "SELECT 'Hello World';" in result.content

    def test_multiple_variables(self):
        """Test múltiples variables"""
        content = """DEFINE v1='a'
DEFINE v2='b'
DEFINE v3='c'
SELECT '&v1', '&v2', '&v3';"""

        plugin = SQLPlusVarsPlugin({})
        context = ProcessingContext()
        context.content = content

        result = plugin.process(context)

        assert "SELECT 'a', 'b', 'c';" in result.content

    def test_variable_redefinition(self):
        """Test redefinición de variable"""
        content = """DEFINE var='first'
SELECT '&var';
DEFINE var='second'
SELECT '&var';"""

        plugin = SQLPlusVarsPlugin({})
        context = ProcessingContext()
        context.content = content

        result = plugin.process(context)

        assert "SELECT 'first';" in result.content
        assert "SELECT 'second';" in result.content

    def test_undefine_variable(self):
        """Test UNDEFINE elimina variable y usar después lanza error"""
        content = """DEFINE var='value'
UNDEFINE var;
SELECT '&var';"""

        plugin = SQLPlusVarsPlugin({})
        context = ProcessingContext()
        context.content = content

        with pytest.raises(ValueError, match="se usa antes de ser definida"):
            plugin.process(context)

    def test_undefined_variable_raises_error(self):
        """Test que usar variable no definida lanza error"""
        content = "SELECT '&undefined_var';"

        plugin = SQLPlusVarsPlugin({})
        context = ProcessingContext()
        context.content = content

        with pytest.raises(ValueError, match="se usa antes de ser definida"):
            plugin.process(context)

    def test_variable_with_dots(self):
        """Test variables con puntos (ej: esquema.tabla)"""
        content = """DEFINE schema_table='dbo.users'
SELECT * FROM &schema_table;"""

        plugin = SQLPlusVarsPlugin({})
        context = ProcessingContext()
        context.content = content

        result = plugin.process(context)

        assert "SELECT * FROM dbo.users;" in result.content

    def test_decimal_values(self):
        """Test valores decimales"""
        content = """DEFINE pi=3.14159
SELECT &pi;"""

        plugin = SQLPlusVarsPlugin({})
        context = ProcessingContext()
        context.content = content

        result = plugin.process(context)

        assert "SELECT 3.14159;" in result.content

    def test_hyphenated_values(self):
        """Test valores con guiones"""
        content = """DEFINE date='2025-10-23'
SELECT '&date';"""

        plugin = SQLPlusVarsPlugin({})
        context = ProcessingContext()
        context.content = content

        result = plugin.process(context)

        assert "SELECT '2025-10-23';" in result.content

    def test_alphanumeric_with_underscores(self):
        """Test valores alfanuméricos con guiones bajos"""
        content = """DEFINE id=user_123
SELECT '&id';"""

        plugin = SQLPlusVarsPlugin({})
        context = ProcessingContext()
        context.content = content

        result = plugin.process(context)

        assert "SELECT 'user_123';" in result.content

    def test_empty_string_define(self):
        """Test DEFINE con string vacío"""
        content = """DEFINE empty=''
SELECT '&empty';"""

        plugin = SQLPlusVarsPlugin({})
        context = ProcessingContext()
        context.content = content

        result = plugin.process(context)

        assert "SELECT '';" in result.content

    def test_comments_preserved(self):
        """Test que comentarios se preservan"""
        content = """-- Definir variable
DEFINE var='value'
-- Usar variable
SELECT '&var';"""

        plugin = SQLPlusVarsPlugin({})
        context = ProcessingContext()
        context.content = content

        result = plugin.process(context)

        assert "-- Definir variable" in result.content
        assert "-- Usar variable" in result.content
        assert "SELECT 'value';" in result.content

    def test_mixed_define_formats(self):
        """Test mezcla de formatos con y sin comillas"""
        content = """DEFINE quoted='with quotes'
DEFINE unquoted=without
SELECT '&quoted', '&unquoted';"""

        plugin = SQLPlusVarsPlugin({})
        context = ProcessingContext()
        context.content = content

        result = plugin.process(context)

        assert "SELECT 'with quotes', 'without';" in result.content


class TestPluginIntegration:
    """Tests de integración entre plugins"""

    def test_includes_then_vars(self, temp_dir):
        """Test orden: includes primero, luego variables"""
        # Archivo con variable
        included = temp_dir / "vars.sql"
        included.write_text("DEFINE db='production'", encoding='utf-8')

        # Main incluye archivo y usa variable
        main_file = temp_dir / "main.sql"
        main_file.write_text("@vars.sql\nSELECT '&db';", encoding='utf-8')

        # Setup plugins
        includes_plugin = SQLPlusIncludesPlugin({})
        vars_plugin = SQLPlusVarsPlugin({})

        # Execute includes first
        context = ProcessingContext()
        context.input_file = str(main_file)
        context.base_path = temp_dir
        context = includes_plugin.process(context)

        # Then process variables
        context = vars_plugin.process(context)

        assert "SELECT 'production';" in context.content
        assert "@vars.sql" not in context.content

    def test_vars_without_includes(self, temp_dir):
        """Test solo procesamiento de variables (skip_var=False)"""
        main_file = temp_dir / "main.sql"
        main_file.write_text("DEFINE env='dev'\nSELECT '&env';", encoding='utf-8')

        includes_plugin = SQLPlusIncludesPlugin({})
        vars_plugin = SQLPlusVarsPlugin({})

        context = ProcessingContext()
        context.input_file = str(main_file)
        context.base_path = temp_dir

        # Execute both
        context = includes_plugin.process(context)
        context = vars_plugin.process(context)

        assert "SELECT 'dev';" in context.content
