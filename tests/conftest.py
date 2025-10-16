import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Crear un directorio temporal para las pruebas"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_sql_file(temp_dir):
    """Crear un archivo SQL de ejemplo para pruebas"""
    sql_content = """-- Archivo de prueba
DEFINE var1='valor1'
DEFINE var2='valor2'

SELECT '&var1' as col1, '&var2' as col2 FROM dual;
"""
    sql_file = temp_dir / "test.sql"
    sql_file.write_text(sql_content, encoding='utf-8')
    return sql_file


@pytest.fixture
def sql_with_includes(temp_dir):
    """Crear archivos SQL con inclusiones para pruebas"""
    # Archivo principal
    main_content = """-- Archivo principal
@include1.sql
@@include2.sql
SELECT * FROM tabla_principal;
"""
    main_file = temp_dir / "main.sql"
    main_file.write_text(main_content, encoding='utf-8')
    
    # Archivo incluido 1
    include1_content = """-- Include 1
CREATE TABLE tabla1 (id NUMBER);
"""
    include1_file = temp_dir / "include1.sql"
    include1_file.write_text(include1_content, encoding='utf-8')
    
    # Archivo incluido 2
    include2_content = """-- Include 2
CREATE TABLE tabla2 (id NUMBER);
"""
    include2_file = temp_dir / "include2.sql"
    include2_file.write_text(include2_content, encoding='utf-8')
    
    return {
        'main': main_file,
        'include1': include1_file,
        'include2': include2_file
    }