# Guía para Publicar en PyPI

Esta guía explica cómo publicar el paquete MergeSourceFile en PyPI (Python Package Index).

## Requisitos Previos

1. **Cuenta en PyPI**: Crear una cuenta en [https://pypi.org/](https://pypi.org/)
2. **Cuenta en TestPyPI** (opcional pero recomendado): Crear una cuenta en [https://test.pypi.org/](https://test.pypi.org/) para pruebas
3. **Token de API**: Configurar un token de API en PyPI para autenticación segura

## Archivos de Configuración Necesarios

El proyecto ya incluye todos los archivos necesarios para PyPI:

- ✅ `pyproject.toml` - Configuración moderna del paquete
- ✅ `README.md` - Documentación del proyecto
- ✅ `LICENSE` - Licencia MIT
- ✅ `MANIFEST.in` - Archivos adicionales a incluir
- ✅ `MergeSourceFile/__init__.py` - Versión y metadatos del paquete

## Construcción del Paquete

### 1. Instalar herramientas de construcción

```bash
pip install build twine
```

### 2. Construir el paquete

```bash
python -m build --no-isolation
```

Esto creará dos archivos en el directorio `dist/`:
- `MergeSourceFile-1.0.0.tar.gz` (distribución fuente)
- `MergeSourceFile-1.0.0-py3-none-any.whl` (distribución wheel)

### 3. Verificar el paquete

```bash
twine check dist/*
```

## Publicación en PyPI

### Opción 1: Publicar en TestPyPI (Recomendado para la primera vez)

TestPyPI es un entorno de prueba que permite verificar que todo funciona correctamente antes de la publicación real.

```bash
twine upload --repository testpypi dist/*
```

Luego, probar la instalación desde TestPyPI:

```bash
pip install --index-url https://test.pypi.org/simple/ MergeSourceFile
```

### Opción 2: Publicar en PyPI (Producción)

Una vez verificado en TestPyPI, publicar en el PyPI real:

```bash
twine upload dist/*
```

Se solicitará el nombre de usuario y el token de API (usar `__token__` como nombre de usuario).

## Instalación del Paquete Publicado

Una vez publicado en PyPI, los usuarios pueden instalar el paquete con:

```bash
pip install MergeSourceFile
```

## Uso del Paquete Instalado

```bash
mergesourcefile --input input.sql --output output.sql
```

## Actualización de Versiones

Para publicar una nueva versión:

1. Actualizar el número de versión en `MergeSourceFile/__init__.py` y `pyproject.toml`
2. Reconstruir el paquete: `python -m build --no-isolation`
3. Verificar: `twine check dist/*`
4. Publicar: `twine upload dist/*`

## Versionado Semántico

El proyecto sigue el versionado semántico (SemVer):

- **MAJOR** (1.x.x): Cambios incompatibles con versiones anteriores
- **MINOR** (x.1.x): Nueva funcionalidad compatible con versiones anteriores
- **PATCH** (x.x.1): Correcciones de errores compatibles con versiones anteriores

Versión actual: `1.0.0`

## Configuración del Token de API de PyPI

### Crear un Token de API

1. Ir a [https://pypi.org/manage/account/](https://pypi.org/manage/account/)
2. Ir a la sección "API tokens"
3. Crear un nuevo token (se recomienda scope limitado al proyecto)
4. Copiar el token generado

### Configurar el Token Localmente

Crear o editar `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-tu-token-aquí

[testpypi]
username = __token__
password = pypi-tu-token-testpypi-aquí
```

**Importante**: Nunca compartir o versionar el archivo `.pypirc` ya que contiene credenciales.

## Verificación de Compatibilidad con PyPI

El paquete ha sido verificado y cumple con todos los requisitos de PyPI:

✅ **Metadata completa**: Nombre, versión, descripción, autor, licencia
✅ **README.md**: Documentación clara y completa
✅ **LICENSE**: Licencia MIT incluida
✅ **Clasificadores**: Tags apropiados para PyPI
✅ **Entry points**: Comando CLI configurado
✅ **Versión Python**: Compatible con Python >=3.8
✅ **Estructura correcta**: Paquete bien estructurado
✅ **Validación twine**: Pasa todas las verificaciones

## Comandos Rápidos

```bash
# Limpiar archivos anteriores
rm -rf dist/ build/ *.egg-info/

# Construir
python -m build --no-isolation

# Verificar
twine check dist/*

# Publicar en TestPyPI
twine upload --repository testpypi dist/*

# Publicar en PyPI
twine upload dist/*
```

## Recursos Adicionales

- [Guía oficial de empaquetado de Python](https://packaging.python.org/tutorials/packaging-projects/)
- [Documentación de PyPI](https://pypi.org/help/)
- [Especificación de pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)
