"""
Tests para el sistema de plugins - ProcessingContext, PluginRegistry, ProcessorPipeline.
"""
import pytest
from pathlib import Path
from abc import ABC
from MergeSourceFile import (
    ProcessingContext,
    ProcessorPlugin,
    PluginRegistry,
    ProcessorPipeline
)
from MergeSourceFile.plugins import get_available_plugins

# Get plugin classes for testing
PLUGINS = get_available_plugins()


class TestProcessingContext:
    """Tests para ProcessingContext"""

    def test_context_initialization(self):
        """Test que context se inicializa con valores por defecto"""
        context = ProcessingContext()

        assert context.input_file == ""
        assert context.content == ""
        assert context.base_path == "."
        assert context.variables == {}
        assert context.verbose is False
        assert context.metadata == {}

    def test_context_with_custom_values(self):
        """Test context con valores personalizados"""
        context = ProcessingContext()
        context.input_file = "test.sql"
        context.content = "SELECT 1;"
        context.base_path = Path("/custom/path")
        context.variables = {'key': 'value'}
        context.verbose = True
        context.metadata = {'custom': 'data'}

        assert context.input_file == "test.sql"
        assert context.content == "SELECT 1;"
        assert context.base_path == Path("/custom/path")
        assert context.variables == {'key': 'value'}
        assert context.verbose is True
        assert context.metadata == {'custom': 'data'}

    def test_context_variables_are_mutable(self):
        """Test que variables en context se pueden modificar"""
        context = ProcessingContext()
        context.variables['foo'] = 'bar'
        context.variables['count'] = 42

        assert context.variables['foo'] == 'bar'
        assert context.variables['count'] == 42


class TestPluginRegistry:
    """Tests para PluginRegistry"""

    def test_registry_initialization(self):
        """Test que registry se inicializa vacío"""
        registry = PluginRegistry()

        assert len(registry._plugins) == 0

    def test_register_plugin(self):
        """Test registrar plugin en registry"""
        SQLPlusIncludesPlugin = PLUGINS['sqlplus_includes']

        registry = PluginRegistry()
        plugin = SQLPlusIncludesPlugin({})

        registry.register(plugin)

        assert registry.get('sqlplus_includes') == plugin

    def test_register_multiple_plugins(self):
        """Test registrar múltiples plugins"""
        SQLPlusIncludesPlugin = PLUGINS['sqlplus_includes']
        SQLPlusVarsPlugin = PLUGINS['sqlplus_vars']

        registry = PluginRegistry()
        includes_plugin = SQLPlusIncludesPlugin({})
        vars_plugin = SQLPlusVarsPlugin({})

        registry.register(includes_plugin)
        registry.register(vars_plugin)

        assert registry.get('sqlplus_includes') == includes_plugin
        assert registry.get('sqlplus_vars') == vars_plugin

    def test_get_nonexistent_plugin_raises_keyerror(self):
        """Test que obtener plugin inexistente lanza KeyError"""
        registry = PluginRegistry()

        with pytest.raises(KeyError, match="nonexistent"):
            registry.get('nonexistent')

    def test_register_duplicate_plugin_name_replaces(self):
        """Test que registrar plugin con nombre duplicado reemplaza"""
        SQLPlusIncludesPlugin = PLUGINS['sqlplus_includes']

        registry = PluginRegistry()
        plugin1 = SQLPlusIncludesPlugin({})
        plugin2 = SQLPlusIncludesPlugin({'skip_var': True})

        registry.register(plugin1)
        registry.register(plugin2)

        # El segundo debe reemplazar al primero
        assert registry.get('sqlplus_includes') == plugin2


class TestProcessorPipeline:
    """Tests para ProcessorPipeline"""

    def test_pipeline_initialization(self):
        """Test inicialización de pipeline"""
        registry = PluginRegistry()
        pipeline = ProcessorPipeline(registry, ['sqlplus_includes'])

        assert pipeline.registry == registry
        assert pipeline.execution_order == ['sqlplus_includes']

    def test_pipeline_execute_single_plugin(self, temp_dir):
        """Test ejecución de pipeline con un solo plugin"""
        SQLPlusIncludesPlugin = PLUGINS['sqlplus_includes']

        # Crear archivo de prueba
        main_file = temp_dir / "main.sql"
        main_file.write_text("SELECT 1;", encoding='utf-8')

        # Setup
        registry = PluginRegistry()
        plugin = SQLPlusIncludesPlugin({})
        registry.register(plugin)

        context = ProcessingContext()
        context.input_file = str(main_file)
        context.base_path = temp_dir

        pipeline = ProcessorPipeline(registry, ['sqlplus_includes'])

        # Execute
        result = pipeline.execute(context)

        assert "SELECT 1;" in result.content

    def test_pipeline_execute_multiple_plugins(self, temp_dir):
        """Test ejecución de pipeline con múltiples plugins"""
        SQLPlusIncludesPlugin = PLUGINS['sqlplus_includes']
        SQLPlusVarsPlugin = PLUGINS['sqlplus_vars']

        # Crear archivo
        main_file = temp_dir / "main.sql"
        main_file.write_text("""
DEFINE var1='value1'
SELECT '&var1';
""", encoding='utf-8')

        # Setup
        registry = PluginRegistry()
        includes_plugin = SQLPlusIncludesPlugin({})
        vars_plugin = SQLPlusVarsPlugin({})
        registry.register(includes_plugin)
        registry.register(vars_plugin)

        context = ProcessingContext()
        context.input_file = str(main_file)
        context.base_path = temp_dir

        pipeline = ProcessorPipeline(registry, ['sqlplus_includes', 'sqlplus_vars'])

        # Execute
        result = pipeline.execute(context)

        assert "SELECT 'value1';" in result.content
        assert "DEFINE" not in result.content  # Las definiciones deben procesarse

    def test_pipeline_execution_order_matters(self, temp_dir):
        """Test que el orden de ejecución importa"""
        SQLPlusIncludesPlugin = PLUGINS['sqlplus_includes']
        Jinja2Plugin = PLUGINS['jinja2']

        # Archivo con template Jinja2
        main_file = temp_dir / "main.sql"
        main_file.write_text("SELECT {{ value }};", encoding='utf-8')

        # Setup registry
        registry = PluginRegistry()
        includes_plugin = SQLPlusIncludesPlugin({})
        jinja2_plugin = Jinja2Plugin({})
        registry.register(includes_plugin)
        registry.register(jinja2_plugin)

        # Context con variables
        context = ProcessingContext()
        context.input_file = str(main_file)
        context.base_path = temp_dir
        context.variables = {'value': 42}

        # Execute con orden: includes -> jinja2
        pipeline = ProcessorPipeline(registry, ['sqlplus_includes', 'jinja2'])
        result = pipeline.execute(context)

        assert "SELECT 42;" in result.content

    def test_pipeline_with_disabled_plugin(self, temp_dir):
        """Test que plugins deshabilitados se saltan"""
        SQLPlusIncludesPlugin = PLUGINS['sqlplus_includes']

        main_file = temp_dir / "main.sql"
        main_file.write_text("SELECT 1;", encoding='utf-8')

        # Plugin deshabilitado
        registry = PluginRegistry()
        plugin = SQLPlusIncludesPlugin({'enabled': False})
        registry.register(plugin)

        context = ProcessingContext()
        context.input_file = str(main_file)
        context.base_path = temp_dir

        pipeline = ProcessorPipeline(registry, ['sqlplus_includes'])
        result = pipeline.execute(context)

        # El contenido debe estar vacío porque el plugin no se ejecutó
        assert result.content == ""

    def test_pipeline_with_nonexistent_plugin_continues(self, temp_dir):
        """Test que pipeline continúa si plugin no existe"""
        SQLPlusIncludesPlugin = PLUGINS['sqlplus_includes']

        main_file = temp_dir / "main.sql"
        main_file.write_text("SELECT 1;", encoding='utf-8')

        registry = PluginRegistry()
        plugin = SQLPlusIncludesPlugin({})
        registry.register(plugin)

        context = ProcessingContext()
        context.input_file = str(main_file)
        context.base_path = temp_dir

        # Orden incluye plugin inexistente
        pipeline = ProcessorPipeline(registry, ['nonexistent', 'sqlplus_includes'])
        result = pipeline.execute(context)

        # Debe ejecutar el plugin que existe
        assert "SELECT 1;" in result.content


class TestProcessorPluginInterface:
    """Tests para la interfaz ProcessorPlugin (ABC)"""

    def test_processor_plugin_is_abstract(self):
        """Test que ProcessorPlugin es una clase abstracta"""
        assert issubclass(ProcessorPlugin, ABC)

    def test_cannot_instantiate_processor_plugin_directly(self):
        """Test que no se puede instanciar ProcessorPlugin directamente"""
        with pytest.raises(TypeError):
            ProcessorPlugin({})

    def test_plugin_must_implement_process(self):
        """Test que subclase debe implementar process()"""
        class IncompletePlugin(ProcessorPlugin):
            @property
            def name(self):
                return "incomplete"

        with pytest.raises(TypeError):
            IncompletePlugin({})

    def test_plugin_must_implement_name(self):
        """Test que subclase debe implementar name property"""
        class IncompletePlugin(ProcessorPlugin):
            def process(self, context):
                return context

        with pytest.raises(TypeError):
            IncompletePlugin({})

    def test_valid_plugin_implementation(self):
        """Test implementación válida de plugin"""
        class ValidPlugin(ProcessorPlugin):
            @property
            def name(self):
                return "valid"

            def process(self, context):
                context.content = "processed"
                return context

        plugin = ValidPlugin({})
        context = ProcessingContext()
        result = plugin.process(context)

        assert result.content == "processed"
        assert plugin.name == "valid"

    def test_plugin_is_enabled_by_default(self):
        """Test que plugin está habilitado por defecto"""
        class SimplePlugin(ProcessorPlugin):
            @property
            def name(self):
                return "simple"

            def process(self, context):
                return context

        plugin = SimplePlugin({})
        assert plugin.is_enabled() is True

    def test_plugin_can_be_disabled_via_config(self):
        """Test que plugin se puede deshabilitar por configuración"""
        class ConfigurablePlugin(ProcessorPlugin):
            @property
            def name(self):
                return "configurable"

            def process(self, context):
                return context

        plugin = ConfigurablePlugin({'enabled': False})
        assert plugin.is_enabled() is False
