"""
Test para la funcionalidad de exclusión mutua entre sistemas de inclusión.

Verifica que cuando SQLPlus includes está activo, Jinja2 includes se deshabilitan
automáticamente para evitar conflictos.
"""
import pytest
import tempfile
from pathlib import Path
from MergeSourceFile.template_engine import TemplateEngine


class TestIncludeConflictResolution:
    """Tests para resolución de conflictos entre sistemas de inclusión"""

    def test_sqlplus_includes_disable_jinja2_includes(self):
        """Test que SQLPlus includes deshabilita automáticamente Jinja2 includes"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Crear archivo incluido
            included_file = temp_path / "included.sql"
            included_file.write_text("SELECT 'from_included';", encoding='utf-8')
            
            # Crear archivo principal con Jinja2 include (debería fallar)
            main_file = temp_path / "main.sql"
            main_file.write_text(
                f'{{% include "{included_file.name}" %}}\n'
                'SELECT \'{{ message }}\';',
                encoding='utf-8'
            )
            
            # Configuración con SQLPlus includes activo
            config = {
                'project': {'input': str(main_file), 'output': 'out.sql'},
                'jinja2': {
                    'extensions': ['sqlplus'],
                    'sqlplus': {
                        'process_includes': True,
                        'process_defines': False
                    }
                }
            }
            
            engine = TemplateEngine(config)
            
            # Debería fallar con mensaje específico sobre includes deshabilitados
            with pytest.raises(Exception) as exc_info:
                engine.process_file(str(main_file), {'message': 'test'})
            
            assert "includes de Jinja2" in str(exc_info.value)
            assert "deshabilitados" in str(exc_info.value)
            assert "SQLPlus" in str(exc_info.value)

    def test_jinja2_includes_work_when_sqlplus_disabled(self):
        """Test que Jinja2 includes funcionan cuando SQLPlus no está activo"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Crear archivo incluido
            included_file = temp_path / "included.sql"
            included_file.write_text("SELECT 'from_jinja_include';", encoding='utf-8')
            
            # Crear archivo principal con Jinja2 include
            main_file = temp_path / "main.sql"
            main_file.write_text(
                f'{{% include "{included_file.name}" %}}\n'
                'SELECT \'{{ message }}\';',
                encoding='utf-8'
            )
            
            # Configuración SIN SQLPlus includes
            config = {
                'project': {'input': str(main_file), 'output': 'out.sql'},
                'jinja2': {
                    'extensions': [],  # Sin extensiones SQLPlus
                }
            }
            
            engine = TemplateEngine(config)
            result = engine.process_file(str(main_file), {'message': 'test'})
            
            # Verificar que ambos includes y variables funcionan
            assert "SELECT 'from_jinja_include';" in result
            assert "SELECT 'test';" in result

    def test_sqlplus_variables_still_work_with_includes_disabled(self):
        """Test que las variables SQLPlus funcionan independientemente de los includes"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Crear archivo principal con variables SQLPlus y Jinja2
            main_file = temp_path / "main.sql"
            main_file.write_text(
                'DEFINE schema=prod_schema\n'
                'SELECT * FROM &schema..{{ table_name }};',
                encoding='utf-8'
            )
            
            # Configuración con SQLPlus includes activo (pero sin usar includes)
            config = {
                'project': {'input': str(main_file), 'output': 'out.sql'},
                'jinja2': {
                    'extensions': ['sqlplus'],
                    'sqlplus': {
                        'process_includes': True,
                        'process_defines': True
                    }
                }
            }
            
            engine = TemplateEngine(config)
            result = engine.process_file(str(main_file), {'table_name': 'users'})
            
            # Verificar que las variables se procesaron correctamente
            assert "SELECT * FROM prod_schema.users;" in result
            # No debería haber referencias sin resolver
            assert "&schema" not in result
            assert "{{ table_name }}" not in result

    def test_sqlplus_includes_only_disabled_when_configured(self):
        """Test que Jinja2 includes solo se deshabilitan cuando SQLPlus includes está explícitamente activo"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Crear archivo incluido
            included_file = temp_path / "included.sql"
            included_file.write_text("SELECT 'from_jinja_include';", encoding='utf-8')
            
            # Crear archivo principal con Jinja2 include
            main_file = temp_path / "main.sql"
            main_file.write_text(
                f'{{% include "{included_file.name}" %}}\n'
                'SELECT \'{{ message }}\';',
                encoding='utf-8'
            )
            
            # Configuración con SQLPlus extension pero includes deshabilitados
            config = {
                'project': {'input': str(main_file), 'output': 'out.sql'},
                'jinja2': {
                    'extensions': ['sqlplus'],
                    'sqlplus': {
                        'process_includes': False,  # Explícitamente deshabilitado
                        'process_defines': True
                    }
                }
            }
            
            engine = TemplateEngine(config)
            result = engine.process_file(str(main_file), {'message': 'test'})
            
            # Jinja2 includes deberían funcionar cuando SQLPlus includes está deshabilitado
            assert "SELECT 'from_jinja_include';" in result
            assert "SELECT 'test';" in result