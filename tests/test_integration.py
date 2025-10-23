"""Tests de integración end-to-end."""
import pytest
import tempfile
import json
from pathlib import Path
from MergeSourceFile import main


class TestIntegrationEndToEnd:
    """Tests de integración completos usando main()"""

    def test_simple_sql_file_processing(self, temp_dir):
        """Test procesamiento simple de archivo SQL"""
        # Crear archivo de entrada
        input_file = temp_dir / "input.sql"
        input_file.write_text("SELECT 1 FROM dual;", encoding='utf-8')
        output_file = temp_dir / "output.sql"

        # Crear archivo de configuración con rutas usando forward slashes
        config_file = temp_dir / "config.toml"
        config_file.write_text(f"""
[project]
input = "{str(input_file).replace(chr(92), '/')}"
output = "{str(output_file).replace(chr(92), '/')}"
execution_order = ["sqlplus_includes", "sqlplus_vars"]

[plugins.sqlplus_includes]
enabled = true

[plugins.sqlplus_vars]
enabled = true
""", encoding='utf-8')

        # Ejecutar
        result = main(str(config_file))

        # Verificar resultado
        assert result == 0
        assert output_file.exists()
        content = output_file.read_text(encoding='utf-8')
        assert "SELECT 1 FROM dual;" in content

    def test_sqlplus_includes_integration(self, temp_dir):
        """Test integración con inclusiones SQL*Plus"""
        # Crear archivo incluido
        included = temp_dir / "included.sql"
        included.write_text("SELECT 'included' FROM dual;", encoding='utf-8')

        # Crear archivo principal
        main_file = temp_dir / "main.sql"
        main_file.write_text(f"@{included.name}\nSELECT 'main' FROM dual;", encoding='utf-8')
        output_file = temp_dir / "output.sql"

        # Config con rutas forward slashes
        config_file = temp_dir / "config.toml"
        config_file.write_text(f"""
[project]
input = "{str(main_file).replace(chr(92), '/')}"
output = "{str(output_file).replace(chr(92), '/')}"
execution_order = ["sqlplus_includes", "sqlplus_vars"]

[plugins.sqlplus_includes]
enabled = true

[plugins.sqlplus_vars]
enabled = true
""", encoding='utf-8')

        # Ejecutar
        main(str(config_file))

        # Verificar
        output = output_file.read_text(encoding='utf-8')
        assert "SELECT 'included' FROM dual;" in output
        assert "SELECT 'main' FROM dual;" in output

    def test_sqlplus_variables_integration(self, temp_dir):
        """Test integración con variables SQL*Plus"""
        # Crear archivo
        input_file = temp_dir / "input.sql"
        input_file.write_text("""
DEFINE env='production'
DEFINE db='mydb'
SELECT '&env', '&db' FROM dual;
""", encoding='utf-8')
        output_file = temp_dir / "output.sql"

        # Config con rutas forward slashes
        config_file = temp_dir / "config.toml"
        config_file.write_text(f"""
[project]
input = "{str(input_file).replace(chr(92), '/')}"
output = "{str(output_file).replace(chr(92), '/')}"
execution_order = ["sqlplus_includes", "sqlplus_vars"]

[plugins.sqlplus_includes]
enabled = true

[plugins.sqlplus_vars]
enabled = true
""", encoding='utf-8')

        # Ejecutar
        main(str(config_file))

        # Verificar
        output = output_file.read_text(encoding='utf-8')
        assert "SELECT 'production', 'mydb' FROM dual;" in output
        assert "DEFINE" not in output

    def test_jinja2_integration(self, temp_dir):
        """Test integración con plantillas Jinja2"""
        # Crear archivo de variables
        vars_file = temp_dir / "vars.json"
        vars_file.write_text(json.dumps({
            'table_name': 'users',
            'columns': ['id', 'name', 'email']
        }), encoding='utf-8')

        # Crear archivo SQL
        input_file = temp_dir / "input.sql"
        input_file.write_text("""
CREATE TABLE {{ table_name }} (
    {% for col in columns %}
    {{ col }} VARCHAR(255){{ "," if not loop.last else "" }}
    {% endfor %}
);
""", encoding='utf-8')
        output_file = temp_dir / "output.sql"

        # Config con rutas forward slashes
        config_file = temp_dir / "config.toml"
        config_file.write_text(f"""
[project]
input = "{str(input_file).replace(chr(92), '/')}"
output = "{str(output_file).replace(chr(92), '/')}"
execution_order = ["jinja2"]

[plugins.jinja2]
enabled = true
variables_file = "{str(vars_file).replace(chr(92), '/')}"
""", encoding='utf-8')

        # Ejecutar
        main(str(config_file))

        # Verificar
        output = output_file.read_text(encoding='utf-8')
        assert "CREATE TABLE users" in output
        assert "id VARCHAR(255)," in output
        assert "name VARCHAR(255)," in output
        assert "email VARCHAR(255)" in output

    def test_full_pipeline_integration(self, temp_dir):
        """Test pipeline completo: Jinja2 + includes + variables"""
        # Crear archivo de configuración SQL
        config_sql = temp_dir / "config.sql"
        config_sql.write_text("DEFINE schema='{{ env }}_schema'", encoding='utf-8')

        # Crear archivo principal
        main_file = temp_dir / "main.sql"
        main_file.write_text(f"""
-- Environment: {{{{ env }}}}
@{config_sql.name}
CREATE TABLE &schema..{{{{ table_name }}}} (id INT);
""", encoding='utf-8')

        # Variables JSON
        vars_file = temp_dir / "vars.json"
        vars_file.write_text(json.dumps({
            'env': 'prod',
            'table_name': 'users'
        }), encoding='utf-8')

        # Config con orden específico y rutas forward slashes
        output_file = temp_dir / "output.sql"
        config_file = temp_dir / "config.toml"
        config_file.write_text(f"""
[project]
input = "{str(main_file).replace(chr(92), '/')}"
output = "{str(output_file).replace(chr(92), '/')}"
execution_order = ["sqlplus_includes", "jinja2", "sqlplus_vars"]

[plugins.sqlplus_includes]
enabled = true

[plugins.sqlplus_vars]
enabled = true

[plugins.jinja2]
enabled = true
variables_file = "{str(vars_file).replace(chr(92), '/')}"
""", encoding='utf-8')

        # Ejecutar
        main(str(config_file))

        # Verificar
        output = output_file.read_text(encoding='utf-8')
        assert "-- Environment: prod" in output
        assert "CREATE TABLE prod_schema.users (id INT);" in output
        assert "DEFINE" not in output

    def test_skip_var_option(self, temp_dir):
        """Test opción skip_var deshabilita procesamiento de variables"""
        input_file = temp_dir / "input.sql"
        input_file.write_text("DEFINE var='value'\nSELECT '&var';", encoding='utf-8')
        output_file = temp_dir / "output.sql"

        config_file = temp_dir / "config.toml"
        config_file.write_text(f"""
[project]
input = "{str(input_file).replace(chr(92), '/')}"
output = "{str(output_file).replace(chr(92), '/')}"
execution_order = ["sqlplus_includes", "sqlplus_vars"]

[plugins.sqlplus_includes]
enabled = true

[plugins.sqlplus_vars]
enabled = true
skip_var = true
""", encoding='utf-8')

        # Ejecutar
        main(str(config_file))

        # Verificar - las variables NO deben procesarse
        output = output_file.read_text(encoding='utf-8')
        assert "DEFINE var='value'" in output
        assert "&var" in output

    def test_empty_output_is_rejected(self, temp_dir, caplog):
        """Test que output vacío es rechazado en la validación de configuración"""
        # Crear archivo de entrada
        input_file = temp_dir / "input.sql"
        input_file.write_text("SELECT 1 FROM dual;", encoding='utf-8')

        # Crear configuración con output vacío
        config_file = temp_dir / "config.toml"
        config_file.write_text(f"""
[project]
input = "{str(input_file).replace(chr(92), '/')}"
output = ""
""", encoding='utf-8')

        # Ejecutar - debe fallar en la validación de configuración
        result = main(str(config_file))
        
        # Debe retornar código de error porque la validación rechaza output vacío
        assert result == 1  # Debe retornar error
        
        # Verificar que el error fue logueado
        assert any("Error de configuración" in record.message for record in caplog.records)
        assert any("output" in record.message.lower() for record in caplog.records)
