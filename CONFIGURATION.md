# MergeSourceFile Configuration Guide

## Configuration File Reference (v2.0.0)

MergeSourceFile v2.0.0 introduces a **plugin-based architecture** with a new hierarchical configuration format. The tool reads from a file named `MKFSource.toml` located in the current directory.

## Configuration Requirements

### Legend
- 🔴 **OBLIGATORIO**: Este parámetro DEBE estar presente en el archivo
- 🟢 **OPCIONAL**: Este parámetro puede omitirse (se usa valor por defecto)
- 🔵 **REQUERIDO**: Esta sección DEBE existir en el archivo
- 🟡 **CONDICIONAL**: Requerido solo si se cumplen ciertas condiciones

### Structure Overview

```toml
[project]                          # 🔵 REQUERIDO
input = "..."                      # 🔴 OBLIGATORIO
output = "..."                     # 🔴 OBLIGATORIO
verbose = false                    # 🟢 OPCIONAL (default: false)
create_backup = false              # 🟢 OPCIONAL (default: false)

[plugins.nombre_plugin]            # 🟢 OPCIONAL (toda la sección)
enabled = true                     # 🔴 OBLIGATORIO si defines el plugin

```

## Quick Start

1. Create `MKFSource.toml` in your project directory:
   ```bash
   # Create a new configuration file
   touch MKFSource.toml
   ```

2. **Minimum viable configuration** (processes SQL*Plus includes and variables):
   ```toml
   [project]
   input = "main.sql"              # 🔴 OBLIGATORIO
   output = "output.sql"           # 🔴 OBLIGATORIO
   execution_order = ["sqlplus_includes", "sqlplus_vars"]  # 🔴 OBLIGATORIO
   
   [plugins.sqlplus_includes]
   enabled = true                  # 🔴 OBLIGATORIO
   
   [plugins.sqlplus_vars]
   enabled = true                  # 🔴 OBLIGATORIO
   ```

3. Run the tool (no arguments needed, reads from `MKFSource.toml`):
   ```bash
   mergesourcefile
   ```
   
   **Note**: The tool only reads from `MKFSource.toml` in the current directory. There are no command-line parameters.

## What Changed in v2.0.0

**BREAKING CHANGES**:
- ❌ **Legacy format removed**: `[mergesourcefile]` section no longer supported
- ✅ **New hierarchical format**: `[project]`, `[plugins.*]` sections
- ✅ **Plugin architecture**: Modular, extensible processing system
- ✅ **Configurable pipeline**: Custom execution order for plugins
- ✅ **Separate plugin configs**: Individual configuration for each plugin

**Migration from v1.x to v2.0.0**:
```toml
# Old format (v1.x - NO LONGER SUPPORTED)
[mergesourcefile]
input = "main.sql"
output = "output.sql"
jinja2 = true
jinja2_vars = "vars.json"
skip_var = false
processing_order = "default"

# New format (v2.0.0 - REQUIRED)
[project]
input = "main.sql"
output = "output.sql"
verbose = false

[plugins.sqlplus]
enabled = true
skip_var = false

[plugins.jinja2]
enabled = true
variables_file = "vars.json"

# execution_order moved to [project] section: execution_order = ["sqlplus_includes", "jinja2", "sqlplus_vars"]
```

## Configuration File Structure

### Complete Example with All Options

```toml
# MKFSource.toml - Configuration for MergeSourceFile v2.0.0
# This file must be located in the current directory

[project]
# 🔴 OBLIGATORIO: Archivos de entrada y salida
input = "main.sql"                  # Archivo SQL de entrada a procesar
output = "merged_output.sql"        # Archivo de salida con el resultado

# 🟢 OPCIONAL: Opciones generales
verbose = true                      # Muestra logs detallados (default: false)
create_backup = false               # Crea backup antes de sobrescribir (default: false)

# 🟢 OPCIONAL: Plugins - Solo define los que necesites
[plugins.sqlplus_includes]
enabled = true                      # 🔴 OBLIGATORIO si defines esta sección

[plugins.sqlplus_vars]
enabled = true                      # 🔴 OBLIGATORIO si defines esta sección
skip_var = false                    # 🟢 OPCIONAL (default: false)

[plugins.jinja2]
enabled = true                      # 🔴 OBLIGATORIO si defines esta sección
variables_file = "variables.json"   # 🟢 OPCIONAL: archivo JSON con variables

# 🔴 OBLIGATORIO: Pipeline (si definiste algún plugin)
# execution_order moved to [project] section: execution_order = ["sqlplus_includes", "jinja2", "sqlplus_vars"]
```

## Configuration Parameters

### [project] Section - 🔵 REQUERIDO

Esta sección **DEBE existir** en todo archivo de configuración.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `input` | string | 🔴 **Sí** | N/A | Archivo SQL de entrada a procesar |
| `output` | string | 🔴 **Sí** | N/A | Archivo de salida con el resultado procesado |
| `verbose` | boolean | 🟢 No | `false` | Muestra información detallada del procesamiento |
| `create_backup` | boolean | 🟢 No | `false` | Crea backup (.backup) antes de sobrescribir |

**Validaciones**:
- ❌ `input` y `output` no pueden estar vacíos
- ❌ El archivo de entrada debe existir (validado en tiempo de ejecución)

### [plugins.sqlplus_includes] Section - 🟢 OPCIONAL

Plugin para resolver inclusiones `@` y `@@` de SQL*Plus.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `enabled` | boolean | 🔴 **Sí** (si defines sección) | N/A | Activa/desactiva el plugin |

### [plugins.sqlplus_vars] Section - 🟢 OPCIONAL

Plugin para sustitución de variables `DEFINE`/`UNDEFINE`.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `enabled` | boolean | 🔴 **Sí** (si defines sección) | N/A | Activa/desactiva el plugin |
| `skip_var` | boolean | 🟢 No | `false` | Omite procesamiento de variables |

### [plugins.jinja2] Section - 🟢 OPCIONAL

Plugin para procesamiento de plantillas Jinja2.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `enabled` | boolean | 🔴 **Sí** (si defines sección) | N/A | Activa/desactiva el plugin |
| `variables_file` | string | 🟢 No | `null` | Archivo JSON con variables para Jinja2 |

### Processing Order Strategies

Elige el orden de ejecución según tu flujo de trabajo:

```toml
# Estrategia 1: Por defecto (Includes → Jinja2 → Variables)
# Usa cuando: Los archivos incluidos pueden contener plantillas Jinja2
execution_order = ["sqlplus_includes", "jinja2", "sqlplus_vars"]

# Estrategia 2: Jinja2 primero (Jinja2 → Includes → Variables)
# Usa cuando: Jinja2 determina qué archivos incluir
execution_order = ["jinja2", "sqlplus_includes", "sqlplus_vars"]

# Estrategia 3: Solo SQL*Plus (Includes → Variables)
# Usa cuando: No necesitas Jinja2
execution_order = ["sqlplus_includes", "sqlplus_vars"]

# Estrategia 4: Solo Jinja2
# Usa cuando: Solo procesas plantillas
execution_order = ["jinja2"]
```

## Usage Examples

### Minimum Configuration (Solo SQL*Plus)
```toml
[project]
input = "database_schema.sql"       # 🔴 OBLIGATORIO
output = "deployment_script.sql"    # 🔴 OBLIGATORIO

[plugins.sqlplus_includes]
enabled = true                      # 🔴 OBLIGATORIO

[plugins.sqlplus_vars]
enabled = true                      # 🔴 OBLIGATORIO

# execution_order moved to [project] section: execution_order = ["sqlplus_includes", "sqlplus_vars"]  # 🔴 OBLIGATORIO
```

### With Jinja2 Templates
```toml
[project]
input = "template.sql"              # 🔴 OBLIGATORIO
output = "generated.sql"             # 🔴 OBLIGATORIO

[plugins.sqlplus_includes]
enabled = true                       # 🔴 OBLIGATORIO

[plugins.sqlplus_vars]
enabled = true                       # 🔴 OBLIGATORIO

[plugins.jinja2]
enabled = true                       # 🔴 OBLIGATORIO
variables_file = "production_vars.json"  # 🟢 OPCIONAL

# execution_order moved to [project] section: execution_order = ["jinja2", "sqlplus_includes", "sqlplus_vars"]  # 🔴 OBLIGATORIO
```

### Verbose Debugging
```toml
[project]
input = "debug.sql"                  # 🔴 OBLIGATORIO
output = "debug_output.sql"          # 🔴 OBLIGATORIO
verbose = true                       # 🟢 OPCIONAL: activar logs detallados

[plugins.sqlplus_includes]
enabled = true                       # 🔴 OBLIGATORIO

[plugins.sqlplus_vars]
enabled = true                       # 🔴 OBLIGATORIO
skip_var = false                     # 🟢 OPCIONAL (default: false)

# execution_order moved to [project] section: execution_order = ["sqlplus_includes", "sqlplus_vars"]  # 🔴 OBLIGATORIO
```

### Skip Variable Processing
```toml
[project]
input = "static_script.sql"          # 🔴 OBLIGATORIO
output = "merged_static.sql"         # 🔴 OBLIGATORIO

[plugins.sqlplus_includes]
enabled = true                       # 🔴 OBLIGATORIO

[plugins.sqlplus_vars]
enabled = true                       # 🔴 OBLIGATORIO
skip_var = true                      # 🟢 OPCIONAL: omitir DEFINE/UNDEFINE

# execution_order moved to [project] section: execution_order = ["sqlplus_includes", "sqlplus_vars"]  # 🔴 OBLIGATORIO
```

### Advanced: Solo Jinja2 (Sin SQL*Plus)
```toml
[project]
input = "app_template.sql"           # 🔴 OBLIGATORIO
output = "app_generated.sql"         # 🔴 OBLIGATORIO
create_backup = true                 # 🟢 OPCIONAL: crear .backup antes de sobrescribir
execution_order = ["jinja2"]

[plugins.jinja2]
enabled = true                       # 🔴 OBLIGATORIO
variables_file = "app_config.json"   # 🟢 OPCIONAL         # 🔴 OBLIGATORIO
```

## Running MergeSourceFile

```powershell
# Ejecuta en el directorio que contiene MKFSource.toml
mergesourcefile

# La herramienta realizará:
# 1. Buscar MKFSource.toml en el directorio actual
# 2. Leer la configuración
# 3. Procesar tus archivos SQL según los plugins habilitados
# 4. Generar el resultado en el archivo de salida especificado
```

## Best Practices

1. **Control de versiones**: Incluye `MKFSource.toml` en tu repositorio Git
2. **Configuraciones por entorno**: Crea archivos separados para diferentes entornos (`MKFSource.dev.toml`, `MKFSource.prod.toml`)
3. **Documentación inline**: Añade comentarios en el TOML para explicar configuraciones complejas
4. **Validación con verbose**: Prueba con `verbose = true` para verificar el orden de procesamiento
5. **Un archivo por proyecto**: Mantén un `MKFSource.toml` por configuración de build
6. **Minimiza plugins**: Solo habilita los plugins que realmente necesites
7. **Backups en producción**: Usa `create_backup = true` cuando sobrescribas archivos críticos

## Troubleshooting

### Missing Configuration File
```
ERROR: No se encontró el archivo de configuración
======================================================================
Archivo buscado: MKFSource.toml
Directorio actual: C:\Users\usuario\proyecto

Para usar MergeSourceFile, necesitas crear un archivo 'MKFSource.toml'
en el directorio desde donde ejecutas el comando.
```
**Solución**: Crea un archivo `MKFSource.toml` en el directorio actual.

### Missing Required Parameters
```
ERROR: Falta el parámetro 'input' requerido en la configuración
======================================================================
El parámetro 'input' es obligatorio y no está definido.

Tu archivo MKFSource.toml debe incluir:

  [project]
  input = "tu_archivo_entrada.sql"
  output = "archivo_salida.sql"
```
**Solución**: Añade los campos 🔴 OBLIGATORIOS (`input` y `output`) a la sección `[project]`.

### Missing Pipeline Configuration
```
ERROR: execution_order está vacío pero hay plugins habilitados
```
**Solución**: Si definiste plugins en `
execution_order = ["sqlplus_includes", "sqlplus_vars"]

[plugins.*]`, debes especificar el orden de ejecución:
```toml
```

### Plugin Not Found
```
ERROR: Plugin 'mi_plugin' en execution_order no está disponible
======================================================================
Plugins disponibles: sqlplus_includes, jinja2, sqlplus_vars
```
**Solución**: Verifica que el nombre del plugin sea correcto y esté en la lista de plugins disponibles.

### Invalid TOML Syntax
```
ValueError: Error al parsear el archivo TOML: ...
```
**Solución**: Valida la sintaxis TOML. Causas comunes:
- Comillas faltantes en strings
- Secciones mal formateadas
- Valores booleanos incorrectos (usa `true`/`false` en minúsculas)

### File Not Found
```
FileNotFoundError: El archivo de entrada no existe: main.sql
```
**Solución**: Verifica que el archivo especificado en `input` exista en la ruta indicada.

## Configuration Validation

MergeSourceFile valida automáticamente tu configuración:

- **Campos obligatorios**: Verifica que `input` y `output` estén en `[project]`
- **Existencia de archivos**: Los archivos de entrada se verifican en tiempo de ejecución
- **Compatibilidad de parámetros**: Se rechaza `execution_order` con plugins no disponibles
- **Validación de tipos**: Parámetros booleanos y strings se validan automáticamente
- **Plugins habilitados**: Verifica que los plugins en `execution_order` tengan `enabled = true`

**Nota**: La herramienta lee configuración **exclusivamente** de `MKFSource.toml` en el directorio actual. No hay parámetros de línea de comandos para especificar archivos alternativos.

## Configuration Examples by Use Case

### 1. Deployment Script Assembly (SQL*Plus Only)
```toml
# Caso de uso: Ensamblar múltiples archivos SQL en un script de despliegue
[project]
input = "deploy_master.sql"          # 🔴 OBLIGATORIO
output = "deploy_production.sql"     # 🔴 OBLIGATORIO
create_backup = true                 # 🟢 OPCIONAL: protege salidas existentes

[plugins.sqlplus_includes]
enabled = true                       # 🔴 OBLIGATORIO

[plugins.sqlplus_vars]
enabled = true                       # 🔴 OBLIGATORIO

# execution_order moved to [project] section: execution_order = ["sqlplus_includes", "sqlplus_vars"]  # 🔴 OBLIGATORIO
```

### 2. Template Generation (Jinja2 + SQL*Plus)
```toml
# Caso de uso: Generar SQL desde plantillas con variables de entorno
[project]
input = "schema_template.sql"        # 🔴 OBLIGATORIO
output = "schema_prod.sql"           # 🔴 OBLIGATORIO
verbose = true                       # 🟢 OPCIONAL: debug durante desarrollo

[plugins.jinja2]
enabled = true                       # 🔴 OBLIGATORIO
variables_file = "prod_config.json"  # 🟢 OPCIONAL: variables externas

[plugins.sqlplus_includes]
enabled = true                       # 🔴 OBLIGATORIO

[plugins.sqlplus_vars]
enabled = true                       # 🔴 OBLIGATORIO

[project]
# Primero Jinja2 para generar código SQL, luego incluir archivos, finalmente variables
execution_order = ["jinja2", "sqlplus_includes", "sqlplus_vars"]  # 🔴 OBLIGATORIO
```

### 3. Pure Template Processing (Solo Jinja2)
### 3. Pure Template Processing (Solo Jinja2)
```toml
# Caso de uso: Generación de SQL dinámico solo con plantillas (sin SQL*Plus)
[project]
input = "query_template.sql"         # 🔴 OBLIGATORIO
output = "query_generated.sql"       # 🔴 OBLIGATORIO
execution_order = ["jinja2"]

[plugins.jinja2]
enabled = true                       # 🔴 OBLIGATORIO
variables_file = "query_params.json" # 🟢 OPCIONAL         # 🔴 OBLIGATORIO
```

---

## Summary: Quick Reference

| **Elemento** | **¿Es Obligatorio?** | **Cuándo** |
|-------------|---------------------|-----------|
| `[project]` | 🔴 **Sí, siempre** | Toda configuración debe tener esta sección |
| `[project].input` | 🔴 **Sí, siempre** | Debe especificar el archivo de entrada |
| `[project].output` | 🔴 **Sí, siempre** | Debe especificar el archivo de salida |
| `[project].verbose` | 🟢 No | Solo si necesitas logs detallados |
| `[project].create_backup` | 🟢 No | Solo si quieres respaldo automático |
| `[plugins.*]` | 🟢 No | Solo define los plugins que necesites |
| `[plugins.*].enabled` | 🔴 **Sí, si defines plugin** | Debe estar en cada sección `[plugins.*]` que crees |
| `[project].execution_order` | 🔴 **Sí** (si usas plugins) | Orden de ejecución de plugins |

### Minimum Valid Configuration (Sin Plugins)
```toml
[project]
input = "input.sql"
output = "output.sql"
```
✅ **Válido**: No procesa nada, solo copia el archivo.

### Minimum Useful Configuration (Con Plugins)
```toml
[project]
input = "master.sql"
output = "merged.sql"
execution_order = ["sqlplus_includes"]

[plugins.sqlplus_includes]
enabled = true
```
✅ **Válido**: Procesa inclusiones `@` y `@@`.

---

Para más detalles, consulta los documentos:
- `docs_trabajo/config.example.toml` - Ejemplo completo comentado
- `EXAMPLES.md` - Casos de uso detallados
- `API_DOCUMENTATION.md` - Referencia de la API interna

### Multiple Configurations for Different Environments

Maintain separate configuration files and copy the appropriate one before running:

```bash
# Development build
cp MKFSource.dev.toml MKFSource.toml
mergesourcefile

# Production build  
cp MKFSource.prod.toml MKFSource.toml
mergesourcefile

# Or use a script to automate
./build.sh dev    # Copies MKFSource.dev.toml and runs mergesourcefile
./build.sh prod   # Copies MKFSource.prod.toml and runs mergesourcefile
```

**Note**: The tool only reads from `MKFSource.toml` in the current directory. There is no `--config` parameter.

## Related Documentation

- [README.md](README.md) - General usage and installation
- [EXAMPLES.md](EXAMPLES.md) - Practical usage examples
- [CHANGELOG.md](CHANGELOG.md) - Version history and changes