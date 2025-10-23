"""
Tests para resource_io - Lectura y escritura de archivos (ResourceLoader y ResourceWriter).
"""
import pytest
from pathlib import Path
from MergeSourceFile import ResourceLoader


class TestResourceLoader:
    """Tests para ResourceLoader"""

    def test_write_text_file_with_empty_path_raises_error(self):
        """Test que path vacío lanza ValueError"""
        with pytest.raises(ValueError, match="file_path.*no puede estar vacío"):
            ResourceLoader.write_text_file("", "content")

    def test_write_text_file_with_whitespace_only_path_raises_error(self):
        """Test que path con solo espacios lanza ValueError"""
        with pytest.raises(ValueError, match="file_path.*no puede estar vacío"):
            ResourceLoader.write_text_file("   ", "content")

    def test_write_text_file_with_valid_path(self, temp_dir):
        """Test que escritura con path válido funciona"""
        output_file = temp_dir / "output.txt"
        ResourceLoader.write_text_file(str(output_file), "test content")
        
        assert output_file.exists()
        assert output_file.read_text(encoding='utf-8') == "test content"

    def test_read_text_file(self, temp_dir):
        """Test lectura de archivo de texto"""
        input_file = temp_dir / "input.txt"
        input_file.write_text("test content", encoding='utf-8')
        
        content = ResourceLoader.read_text_file(str(input_file))
        
        assert content == "test content"
