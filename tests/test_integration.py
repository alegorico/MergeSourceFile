"""Tests de integración end-to-end."""
import pytest
import yaml
from pathlib import Path
from MergeSourceFile.core import main


class TestIntegrationEndToEnd:
    """Tests de integración completos usando main()"""

    def test_simple_jinja2_processing(self, temp_dir):
        """Test procesamiento simple con Jinja2"""
        # Crear archivo de entrada
        input_file = temp_dir / "input.sql"
        input_file.write_text("SELECT {{ value }} FROM dual;", encoding='utf-8')
        output_file = temp_dir / "output.sql"

        # Crear archivo de variables
        vars_file = temp_dir / "vars.yaml"
        vars_file.write_text(yaml.dump({'value': 42}), encoding='utf-8')

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
        vars_file = temp_dir / "vars.yaml"
        vars_file.write_text(yaml.dump({
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

        # Variables YAML para Jinja2
        vars_file = temp_dir / "vars.yaml"
        vars_file.write_text(yaml.dump({
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
        vars_file = temp_dir / "vars.yaml"
        vars_file.write_text(yaml.dump({'value': 'new'}), encoding='utf-8')

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

    def test_independent_src_and_config_locations(self, temp_dir):
        """Test de desacople entre src y config, directorios independientes"""
        import os
        
        # Crear directorios
        config_dir = temp_dir / "config"
        src_dir = temp_dir / "src"
        build_dir = temp_dir / "build"
        
        config_dir.mkdir()
        src_dir.mkdir()
        build_dir.mkdir()

        # Crear archivo fuente en src
        input_file = src_dir / "schema.sql"
        input_file.write_text("CREATE TABLE {{ table_name }} (id INT);", encoding='utf-8')

        # Crear archivo de variables en config
        vars_file = config_dir / "vars.yaml"
        vars_file.write_text("table_name: users", encoding='utf-8')

        # Crear config en config
        config_file = config_dir / "MKFSource.toml"
        # Usamos rutas relativas al archivo de configuración
        config_file.write_text("""
[project]
input = "../src/schema.sql"
output = "../build/output.sql"

[jinja2]
enabled = true
variables_file = "vars.yaml"
""", encoding='utf-8')

        # Simulamos que ejecutamos desde la raíz del proyecto usando MSF_CONFIG
        os.environ['MSF_CONFIG'] = str(config_file)
        
        # Guardar el CWD original y cambiar a temp_dir (raíz del proyecto simulado)
        original_cwd = os.getcwd()
        os.chdir(str(temp_dir))
        
        try:
            # Ejecutamos main sin argumentos, leerá MSF_CONFIG
            result = main()
            
            # Verificar éxito
            assert result == 0
            
            # Verificar que el output se generó en el build_dir correcto
            output_file = build_dir / "output.sql"
            assert output_file.exists()
            assert "CREATE TABLE users (id INT);" in output_file.read_text(encoding='utf-8')
        finally:
            # Restaurar estado
            os.chdir(original_cwd)
            if 'MSF_CONFIG' in os.environ:
                del os.environ['MSF_CONFIG']

    def test_msf_config_env_var_override(self, temp_dir):
        """Test que demuestra que la configuración puede cargarse desde la variable MSF_CONFIG con un nombre no estándar"""
        import os
        
        # Crear archivo de entrada
        input_file = temp_dir / "input.sql"
        input_file.write_text("SELECT 1 FROM dual;", encoding='utf-8')
        output_file = temp_dir / "output.sql"

        # Crear archivo de configuración con nombre NO por defecto
        custom_config_file = temp_dir / "custom_pipeline_config.toml"
        custom_config_file.write_text(f"""
[project]
input = "{str(input_file).replace(chr(92), '/')}"
output = "{str(output_file).replace(chr(92), '/')}"
""", encoding='utf-8')

        # Asignar la variable de entorno
        os.environ['MSF_CONFIG'] = str(custom_config_file)
        
        try:
            # Ejecutar main sin argumentos, debe leer el archivo desde la variable
            result = main()
            
            # Verificar
            assert result == 0
            assert output_file.exists()
            assert "SELECT 1 FROM dual;" in output_file.read_text(encoding='utf-8')
        finally:
            # Limpiar el entorno
            if 'MSF_CONFIG' in os.environ:
                del os.environ['MSF_CONFIG']
