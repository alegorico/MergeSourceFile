import pytest
from MergeSourceFile import ProcessingContext
from MergeSourceFile.plugins import get_available_plugins

# Get plugin classes
PLUGINS = get_available_plugins()
Jinja2Plugin = PLUGINS['jinja2']
SQLPlusVarsPlugin = PLUGINS['sqlplus_vars']

class TestJinja2Plugin:
    def test_plugin_name(self):
        plugin = Jinja2Plugin({})
        assert plugin.name == 'jinja2'

    def test_simple_substitution(self):
        plugin = Jinja2Plugin({'enabled': True})
        context = ProcessingContext()
        context.content = 'SELECT {{ value }};'
        context.variables = {'value': 42}
        result = plugin.process(context)
        assert 'SELECT 42;' in result.content
