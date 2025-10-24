"""
Tests para la extensión SQLPlus.

Tests para las funciones de pre-procesamiento SQLPlus:
- Resolución de inclusiones @ y @@
- Procesamiento de variables DEFINE/UNDEFINE
"""
import pytest
from pathlib import Path


class TestSQLPlusIncludes:
    """Tests para procesamiento de inclusiones @ y @@"""

    def test_process_sqlplus_without_includes(self, temp_dir):
        """Test que archivos sin inclusiones no se modifican"""
        from MergeSourceFile.extensions.sqlplus import process_sqlplus
        
        content = "SELECT 1 FROM dual;"
        input_file = temp_dir / "test.sql"
        input_file.write_text(content, encoding='utf-8')
        
        result = process_sqlplus(
            content=content,
            input_file=str(input_file),
            base_path=str(temp_dir),
            config={'process_includes': True, 'process_defines': False},
            verbose=False
        )
        
        assert result == "SELECT 1 FROM dual;\n"

    def test_process_single_at_include(self, temp_dir):
        """Test inclusión con @ (relativo a base_path)"""
        from MergeSourceFile.extensions.sqlplus import process_sqlplus
        
        # Archivo incluido
        included = temp_dir / "included.sql"
        included.write_text("SELECT 'included';", encoding='utf-8')
        
        # Archivo principal
        main_file = temp_dir / "main.sql"
        main_content = f"@{included.name}\nSELECT 'main';"
        main_file.write_text(main_content, encoding='utf-8')
        
        result = process_sqlplus(
            content=main_content,
            input_file=str(main_file),
            base_path=str(temp_dir),
            config={'process_includes': True, 'process_defines': False},
            verbose=False
        )
        
        assert "SELECT 'included';" in result
        assert "SELECT 'main';" in result
        # Verificar orden
        assert result.index("included") < result.index("main")

    def test_process_double_at_include(self, temp_dir):
        """Test inclusión con @@ (relativo a archivo padre)"""
        from MergeSourceFile.extensions.sqlplus import process_sqlplus
        
        # Crear subdirectorio
        subdir = temp_dir / "subdir"
        subdir.mkdir()
        
        # Archivo incluido en mismo subdirectorio (para @@)
        included = subdir / "included.sql"
        included.write_text("SELECT 'root';", encoding='utf-8')
        
        # Archivo principal en subdirectorio
        main_file = subdir / "main.sql"
        main_content = f"@@{included.name}\nSELECT 'sub';"
        main_file.write_text(main_content, encoding='utf-8')
        
        result = process_sqlplus(
            content=main_content,
            input_file=str(main_file),
            base_path=str(temp_dir),
            config={'process_includes': True, 'process_defines': False},
            verbose=False
        )
        
        assert "SELECT 'root';" in result
        assert "SELECT 'sub';" in result

    def test_nested_includes(self, temp_dir):
        """Test inclusiones anidadas multinivel"""
        from MergeSourceFile.extensions.sqlplus import process_sqlplus
        
        # Nivel 3
        level3 = temp_dir / "level3.sql"
        level3.write_text("SELECT 'level3';", encoding='utf-8')
        
        # Nivel 2
        level2 = temp_dir / "level2.sql"
        level2.write_text(f"@{level3.name}\nSELECT 'level2';", encoding='utf-8')
        
        # Nivel 1
        level1 = temp_dir / "level1.sql"
        level1_content = f"@{level2.name}\nSELECT 'level1';"
        level1.write_text(level1_content, encoding='utf-8')
        
        result = process_sqlplus(
            content=level1_content,
            input_file=str(level1),
            base_path=str(temp_dir),
            config={'process_includes': True, 'process_defines': False},
            verbose=False
        )
        
        assert "SELECT 'level3';" in result
        assert "SELECT 'level2';" in result
        assert "SELECT 'level1';" in result
        # Verificar orden correcto
        assert result.index("level3") < result.index("level2") < result.index("level1")

    def test_include_file_not_found(self, temp_dir):
        """Test que se lanza error cuando archivo incluido no existe"""
        from MergeSourceFile.extensions.sqlplus import process_sqlplus
        
        main_file = temp_dir / "main.sql"
        main_content = "@nonexistent.sql"
        main_file.write_text(main_content, encoding='utf-8')
        
        with pytest.raises(FileNotFoundError, match="nonexistent.sql"):
            process_sqlplus(
                content=main_content,
                input_file=str(main_file),
                base_path=str(temp_dir),
                config={'process_includes': True, 'process_defines': False},
                verbose=False
            )

    def test_skip_includes_when_disabled(self, temp_dir):
        """Test que las inclusiones no se procesan cuando está deshabilitado"""
        from MergeSourceFile.extensions.sqlplus import process_sqlplus
        
        included = temp_dir / "included.sql"
        included.write_text("SELECT 'included';", encoding='utf-8')
        
        main_file = temp_dir / "main.sql"
        main_content = f"@{included.name}"
        main_file.write_text(main_content, encoding='utf-8')
        
        result = process_sqlplus(
            content=main_content,
            input_file=str(main_file),
            base_path=str(temp_dir),
            config={'process_includes': False, 'process_defines': False},
            verbose=False
        )
        
        # No debería procesar la inclusión
        assert "@" in result
        assert "SELECT 'included';" not in result


class TestSQLPlusDefines:
    """Tests para procesamiento de variables DEFINE/UNDEFINE"""

    def test_simple_define_and_substitution(self):
        """Test definición y sustitución simple de variable"""
        from MergeSourceFile.extensions.sqlplus import _process_defines
        
        content = """
DEFINE env='production'
SELECT '&env' FROM dual;
""".strip()
        
        result = _process_defines(content, verbose=False)
        
        assert "SELECT 'production' FROM dual;" in result
        assert "DEFINE" not in result

    def test_multiple_defines(self):
        """Test múltiples definiciones de variables"""
        from MergeSourceFile.extensions.sqlplus import _process_defines
        
        content = """
DEFINE env='prod'
DEFINE db='mydb'
DEFINE schema='public'
SELECT '&env', '&db', '&schema';
""".strip()
        
        result = _process_defines(content, verbose=False)
        
        assert "SELECT 'prod', 'mydb', 'public';" in result

    def test_define_without_quotes(self):
        """Test DEFINE con valor sin comillas"""
        from MergeSourceFile.extensions.sqlplus import _process_defines
        
        content = """
DEFINE count=42
SELECT &count FROM dual;
""".strip()
        
        result = _process_defines(content, verbose=False)
        
        assert "SELECT 42 FROM dual;" in result

    def test_variable_with_concatenation(self):
        """Test variable con concatenación (..)"""
        from MergeSourceFile.extensions.sqlplus import _process_defines
        
        content = """
DEFINE prefix='tbl'
SELECT * FROM &prefix..users;
""".strip()
        
        result = _process_defines(content, verbose=False)
        
        assert "SELECT * FROM tbl.users;" in result

    def test_undefine_variable(self):
        """Test que UNDEFINE elimina la variable"""
        from MergeSourceFile.extensions.sqlplus import _process_defines
        
        content = """
DEFINE temp='value'
SELECT '&temp';
UNDEFINE temp;
""".strip()
        
        result = _process_defines(content, verbose=False)
        
        assert "SELECT 'value';" in result
        assert "UNDEFINE" not in result

    def test_variable_used_before_define_raises_error(self):
        """Test que usar variable antes de definirla lanza error"""
        from MergeSourceFile.extensions.sqlplus import _process_defines
        
        content = """
SELECT '&undefined';
DEFINE undefined='value'
""".strip()
        
        with pytest.raises(ValueError, match="undefined.*antes de ser definida"):
            _process_defines(content, verbose=False)

    def test_comments_are_preserved(self):
        """Test que los comentarios se preservan sin procesar"""
        from MergeSourceFile.extensions.sqlplus import _process_defines
        
        content = """
DEFINE var='value'
-- This is a comment with &var
SELECT '&var';
""".strip()
        
        result = _process_defines(content, verbose=False)
        
        assert "-- This is a comment with &var" in result
        assert "SELECT 'value';" in result

    def test_variable_reused_multiple_times(self):
        """Test que una variable se puede usar múltiples veces"""
        from MergeSourceFile.extensions.sqlplus import _process_defines
        
        content = """
DEFINE table='users'
SELECT * FROM &table;
INSERT INTO &table VALUES (1);
UPDATE &table SET active=1;
""".strip()
        
        result = _process_defines(content, verbose=False)
        
        assert result.count("users") == 3
        assert "&table" not in result

    def test_invalid_define_syntax_is_ignored(self):
        """Test que sintaxis DEFINE inválida se ignora"""
        from MergeSourceFile.extensions.sqlplus import _process_defines
        
        content = """
DEFINE invalid syntax here
SELECT 1;
""".strip()
        
        # No debería lanzar error, solo ignorar
        result = _process_defines(content, verbose=False)
        assert "SELECT 1;" in result

    def test_skip_defines_when_disabled(self):
        """Test que DEFINE no se procesa cuando está deshabilitado"""
        from MergeSourceFile.extensions.sqlplus import process_sqlplus
        
        content = """
DEFINE var='value'
SELECT '&var';
""".strip()
        
        result = process_sqlplus(
            content=content,
            input_file="test.sql",
            base_path=".",
            config={'process_includes': False, 'process_defines': False},
            verbose=False
        )
        
        # No debería procesar DEFINE
        assert "DEFINE" in result
        assert "&var" in result


class TestSQLPlusIntegration:
    """Tests de integración de inclusiones + variables"""

    def test_includes_and_defines_together(self, temp_dir):
        """Test que inclusiones y variables funcionan juntas"""
        from MergeSourceFile.extensions.sqlplus import process_sqlplus
        
        # Archivo incluido con variable
        included = temp_dir / "included.sql"
        included.write_text("SELECT '&env' FROM included;", encoding='utf-8')
        
        # Archivo principal
        main_file = temp_dir / "main.sql"
        main_content = f"""
DEFINE env='production'
@{included.name}
SELECT '&env' FROM main;
""".strip()
        main_file.write_text(main_content, encoding='utf-8')
        
        result = process_sqlplus(
            content=main_content,
            input_file=str(main_file),
            base_path=str(temp_dir),
            config={'process_includes': True, 'process_defines': True},
            verbose=False
        )
        
        # Verificar que ambos se procesaron
        assert "SELECT 'production' FROM included;" in result
        assert "SELECT 'production' FROM main;" in result
        assert "DEFINE" not in result
        assert "&env" not in result

    def test_define_in_included_file(self, temp_dir):
        """Test que DEFINE en archivo incluido afecta al principal"""
        from MergeSourceFile.extensions.sqlplus import process_sqlplus
        
        # Archivo incluido define variable
        included = temp_dir / "defs.sql"
        included.write_text("DEFINE shared='from_include'", encoding='utf-8')
        
        # Archivo principal usa la variable
        main_file = temp_dir / "main.sql"
        main_content = f"""
@{included.name}
SELECT '&shared';
""".strip()
        main_file.write_text(main_content, encoding='utf-8')
        
        result = process_sqlplus(
            content=main_content,
            input_file=str(main_file),
            base_path=str(temp_dir),
            config={'process_includes': True, 'process_defines': True},
            verbose=False
        )
        
        assert "SELECT 'from_include';" in result
