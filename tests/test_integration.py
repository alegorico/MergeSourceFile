"""Tests de integración end-to-end."""
import pytest
import json
from pathlib import Path
from MergeSourceFile import main


class TestIntegrationEndToEnd:
    """Tests de integración completos usando main()"""

    def test_simple_jinja2_processing(self, temp_dir):
        """Test procesamiento simple con Jinja2"""
        # Crear archivo de entrada
        input_file = temp_dir / "input.sql"
        input_file.write_text("SELECT {{ value }} FROM dual;", encoding='utf-8')
        output_file = temp_dir / "output.sql"

        # Crear archivo de variables
        vars_file = temp_dir / "vars.json"
        vars_file.write_text(json.dumps({'value': 42}), encoding='utf-8')

        # Crear archivo de configuración con rutas usando forward slashes
        config_file = temp_dir / "config.toml"
        config_file.write_text(f"""
[project]
input = "{str(input_file).replace(chr(92), '/')}"
output = "{str(output_file).replace(chr(92), '/')}"

[jinja2]
enabled = true
variables_file = "{str(vars_file).replace(chr(92), '/')}"
""", encoding='utf-8')

        # Ejecutar
        result = main(str(config_file))

        # Verificar resultado
        assert result == 0
        assert output_file.exists()
        content = output_file.read_text(encoding='utf-8')
        assert "SELECT 42 FROM dual;" in content

    def test_sqlplus_includes_integration(self, temp_dir):
        """Test integración con inclusiones SQL*Plus"""
        # Crear archivo incluido
        included = temp_dir / "included.sql"
        included.write_text("SELECT 'included' FROM dual;", encoding='utf-8')

        # Crear archivo principal
        main_file = temp_dir / "main.sql"
        main_file.write_text(f"@{included.name}\nSELECT 'main' FROM dual;", encoding='utf-8')
        output_file = temp_dir / "output.sql"

        # Config con extensión sqlplus
        config_file = temp_dir / "config.toml"
        config_file.write_text(f"""
[project]
input = "{str(main_file).replace(chr(92), '/')}"
output = "{str(output_file).replace(chr(92), '/')}"

[jinja2]
enabled = true
extensions = ["sqlplus"]

[jinja2.sqlplus]
process_includes = true
process_defines = false
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

        # Config con extensión sqlplus
        config_file = temp_dir / "config.toml"
        config_file.write_text(f"""
[project]
input = "{str(input_file).replace(chr(92), '/')}"
output = "{str(output_file).replace(chr(92), '/')}"

[jinja2]
enabled = true
extensions = ["sqlplus"]

[jinja2.sqlplus]
process_includes = false
process_defines = true
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

        # Config con Jinja2
        config_file = temp_dir / "config.toml"
        config_file.write_text(f"""
[project]
input = "{str(input_file).replace(chr(92), '/')}"
output = "{str(output_file).replace(chr(92), '/')}"

[jinja2]
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

    def test_full_pipeline_sqlplus_and_jinja2(self, temp_dir):
        """Test pipeline completo: SQLPlus (extensión) + Jinja2"""
        # Crear archivo incluido con DEFINE
        included = temp_dir / "config.sql"
        included.write_text("DEFINE schema='prod_schema'", encoding='utf-8')

        # Crear archivo principal que usa tanto inclusiones como variables Jinja2
        main_file = temp_dir / "main.sql"
        main_file.write_text(f"""
-- Environment: {{{{ env }}}}
@{included.name}
CREATE TABLE &schema..{{{{ table_name }}}} (id INT);
""", encoding='utf-8')

        # Variables JSON para Jinja2
        vars_file = temp_dir / "vars.json"
        vars_file.write_text(json.dumps({
            'env': 'production',
            'table_name': 'users'
        }), encoding='utf-8')

        # Config con extensión sqlplus completa
        output_file = temp_dir / "output.sql"
        config_file = temp_dir / "config.toml"
        config_file.write_text(f"""
[project]
input = "{str(main_file).replace(chr(92), '/')}"
output = "{str(output_file).replace(chr(92), '/')}"

[jinja2]
enabled = true
extensions = ["sqlplus"]
variables_file = "{str(vars_file).replace(chr(92), '/')}"

[jinja2.sqlplus]
process_includes = true
process_defines = true
""", encoding='utf-8')

        # Ejecutar
        main(str(config_file))

        # Verificar que todo se procesó correctamente
        output = output_file.read_text(encoding='utf-8')
        assert "-- Environment: production" in output
        assert "CREATE TABLE prod_schema.users (id INT);" in output
        assert "DEFINE" not in output
        assert "@" not in output

    def test_backup_creation(self, temp_dir):
        """Test que se crea backup cuando está habilitado"""
        # Crear archivo de salida existente
        output_file = temp_dir / "output.sql"
        output_file.write_text("-- Old content", encoding='utf-8')

        # Crear archivo de entrada
        input_file = temp_dir / "input.sql"
        input_file.write_text("SELECT {{ value }} FROM dual;", encoding='utf-8')

        # Variables
        vars_file = temp_dir / "vars.json"
        vars_file.write_text(json.dumps({'value': 'new'}), encoding='utf-8')

        # Config con backup habilitado
        config_file = temp_dir / "config.toml"
        config_file.write_text(f"""
[project]
input = "{str(input_file).replace(chr(92), '/')}"
output = "{str(output_file).replace(chr(92), '/')}"
create_backup = true

[jinja2]
enabled = true
variables_file = "{str(vars_file).replace(chr(92), '/')}"
""", encoding='utf-8')

        # Ejecutar
        main(str(config_file))

        # Verificar que el backup existe
        backup_file = temp_dir / "output.sql.bak"
        assert backup_file.exists()
        assert backup_file.read_text(encoding='utf-8') == "-- Old content"

        # Verificar nuevo contenido
        assert "SELECT new FROM dual;" in output_file.read_text(encoding='utf-8')

    def test_missing_input_file_error(self, temp_dir):
        """Test que falta archivo de entrada genera error"""
        output_file = temp_dir / "output.sql"

        config_file = temp_dir / "config.toml"
        config_file.write_text(f"""
[project]
input = "nonexistent.sql"
output = "{str(output_file).replace(chr(92), '/')}"

[jinja2]
enabled = true
""", encoding='utf-8')

        # Ejecutar - debe fallar
        result = main(str(config_file))
        
        assert result == 1  # Código de error
