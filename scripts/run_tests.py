#!/usr/bin/env python3
"""
Script para ejecutar tests específicos de MergeSourceFile
"""
import subprocess  
import sys
from pathlib import Path

def run_tests():
    """Ejecutar tests principales"""
    project_root = Path(__file__).parent.parent  # Go up one level from scripts/
    python_exe = project_root / ".venv" / "Scripts" / "python.exe"
    
    print("🧪 Ejecutando tests de MergeSourceFile...")
    print("=" * 50)
    
    # Tests que funcionan correctamente (solo tests unitarios para producción)
    working_tests = [
        "tests/test_main.py"  # Todos los tests unitarios principales
    ]
    
    for test in working_tests:
        print(f"\n▶️  Ejecutando: {test}")
        result = subprocess.run([
            str(python_exe), "-m", "pytest", "-v", test
        ], cwd=project_root)
        
        if result.returncode != 0:
            print(f"❌ Test falló: {test}")
        else:
            print(f"✅ Test pasó: {test}")
    
    print("\n" + "=" * 50)
    print("📊 Generando reporte de cobertura...")
    
    # Ejecutar todos los tests unitarios con cobertura
    subprocess.run([
        str(python_exe), "-m", "pytest", 
        "--cov=MergeSourceFile", 
        "--cov-report=html",
        "--cov-report=term-missing",
        "tests/test_main.py"
    ], cwd=project_root)
    
    print("✅ Tests completados!")
    print(f"📄 Reporte HTML disponible en: {project_root / 'htmlcov' / 'index.html'}")

if __name__ == "__main__":
    run_tests()