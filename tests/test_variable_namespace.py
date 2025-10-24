# MIT License
# 
# Copyright (c) 2023 Alejandro G.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Tests para separación de namespace de variables SQLPlus y Jinja2.

Verifica la funcionalidad de extracto de variables DEFINE y su conversión 
a namespace sql_ para evitar conflictos con variables Jinja2.
"""

import pytest
import tempfile
from pathlib import Path
from MergeSourceFile.template_engine import TemplateEngine
from MergeSourceFile.extensions.sqlplus import process_sqlplus


class TestVariableNamespace:
    """Tests para separación de namespace de variables SQLPlus"""
    
    def test_extract_define_variables(self):
        """Test que variables DEFINE se extraen correctamente"""
        content = """
DEFINE env='production'
DEFINE schema='prod_schema'
SELECT '&env', '&schema' FROM dual;
"""
        
        result_content, extracted_vars = process_sqlplus(
            content=content.strip(),
            input_file="test.sql",
            base_path=".",
            config={'process_includes': False, 'process_defines': True},
            verbose=False
        )
        
        # Verificar que las variables se extrajeron
        assert extracted_vars == {
            'env': 'production',
            'schema': 'prod_schema'
        }
        
        # Verificar que el contenido se procesó correctamente
        assert "SELECT 'production', 'prod_schema' FROM dual;" in result_content
    
    def test_namespace_separation_in_template_engine(self):
        """Test que el template engine aplica separación de namespace sql_"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Crear archivo con variables SQLPlus y Jinja2
            main_file = temp_path / "main.sql"
            main_file.write_text("""
DEFINE schema=prod
SELECT * FROM &schema..{{ table_name }};
SELECT '{{ sql_schema }}' AS extracted_define;
""".strip(), encoding='utf-8')
            
            # Configuración con extensión SQLPlus
            config = {
                'project': {'input': str(main_file), 'output': 'out.sql'},
                'jinja2': {
                    'extensions': ['sqlplus'],
                    'sqlplus': {
                        'process_includes': False,
                        'process_defines': True
                    }
                }
            }
            
            engine = TemplateEngine(config)
            result = engine.process_file(str(main_file), {'table_name': 'users'})
            
            # Verificar que la variable SQLPlus se procesó normalmente
            assert "SELECT * FROM prod.users;" in result
            
            # Verificar que la variable extraída está disponible con namespace sql_
            assert "SELECT 'prod' AS extracted_define;" in result
    
    def test_variable_conflict_warning(self, caplog):
        """Test que se genera warning cuando hay conflicto de variables"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Crear archivo con variable conflictiva
            main_file = temp_path / "main.sql"
            main_file.write_text("""
DEFINE schema=sqlplus_value
SELECT * FROM &schema..{{ table_name }};
SELECT '{{ schema }}' AS jinja_var;
SELECT '{{ sql_schema }}' AS sqlplus_var;
""".strip(), encoding='utf-8')
            
            config = {
                'project': {'input': str(main_file), 'output': 'out.sql'},
                'jinja2': {
                    'extensions': ['sqlplus'],
                    'sqlplus': {
                        'process_includes': False,
                        'process_defines': True
                    }
                }
            }
            
            engine = TemplateEngine(config)
            
            # Variables Jinja2 que entran en conflicto
            result = engine.process_file(str(main_file), {
                'table_name': 'users',
                'schema': 'jinja_value'  # Conflicto con DEFINE schema
            })
            
            # Verificar que se genera warning
            assert "CONFLICTO DE VARIABLES" in caplog.text
            assert "'schema'" in caplog.text
            
            # Verificar que cada variable mantiene su valor correcto
            assert "SELECT * FROM sqlplus_value.users;" in result  # SQLPlus DEFINE
            assert "SELECT 'jinja_value' AS jinja_var;" in result  # Jinja2 variable
            assert "SELECT 'sqlplus_value' AS sqlplus_var;" in result  # Namespace sql_
    
    def test_multiple_define_variables_with_namespace(self):
        """Test con múltiples variables DEFINE usando namespace"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            main_file = temp_path / "main.sql"
            main_file.write_text("""
DEFINE env=prod
DEFINE db=oracle
DEFINE schema=myschema
-- Variables originales SQLPlus
SELECT '&env', '&db', '&schema' FROM dual;
-- Variables en namespace Jinja2
SELECT '{{ sql_env }}', '{{ sql_db }}', '{{ sql_schema }}' FROM dual;
-- Variable mixta
SELECT '{{ sql_env }}_{{ suffix }}' FROM dual;
""".strip(), encoding='utf-8')
            
            config = {
                'project': {'input': str(main_file), 'output': 'out.sql'},
                'jinja2': {
                    'extensions': ['sqlplus'],
                    'sqlplus': {
                        'process_includes': False,
                        'process_defines': True
                    }
                }
            }
            
            engine = TemplateEngine(config)
            result = engine.process_file(str(main_file), {'suffix': 'final'})
            
            # Verificar sustituciones SQLPlus
            assert "SELECT 'prod', 'oracle', 'myschema' FROM dual;" in result
            
            # Verificar variables con namespace sql_
            assert "SELECT 'prod', 'oracle', 'myschema' FROM dual;" in result
            
            # Verificar variable mixta
            assert "SELECT 'prod_final' FROM dual;" in result
    
    def test_no_extraction_when_defines_disabled(self):
        """Test que no se extraen variables cuando process_defines está deshabilitado"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            main_file = temp_path / "main.sql"
            main_file.write_text("""
DEFINE env=prod
SELECT '&env' FROM dual;
SELECT '{{ sql_env | default("not_found") }}' FROM dual;
""".strip(), encoding='utf-8')
            
            config = {
                'project': {'input': str(main_file), 'output': 'out.sql'},
                'jinja2': {
                    'extensions': ['sqlplus'],
                    'sqlplus': {
                        'process_includes': False,
                        'process_defines': False  # Deshabilitado
                    }
                }
            }
            
            engine = TemplateEngine(config)
            result = engine.process_file(str(main_file), {})
            
            # DEFINE no se procesó, permanece literal
            assert "DEFINE env=prod" in result
            assert "&env" in result
            
            # Variable sql_ no existe, usa default
            assert "SELECT 'not_found' FROM dual;" in result