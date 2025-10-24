# MergeSourceFile Configuration Guide

## Configuration File Reference (v2.0.0)

MergeSourceFile v2.0.0 uses a **Jinja2-centric architecture** with optional extensions. Configuration is stored in `MKFSource.toml` using the TOML format. The tool reads from a file named `MKFSource.toml` located in the current directory.



## Configuration Requirements

### Legend

- 🔴 **OBLIGATORIO**: Este parámetro DEBE estar presente en el archivo
- 🟢 **OPCIONAL**: Este parámetro puede omitirse (se usa valor por defecto)
- 🔵 **REQUERIDO**: Esta sección DEBE existir en el archivo
- 🟡 **CONDICIONAL**: Requerido solo si se cumplen ciertas condiciones

### Structure Overview

```toml
[project]
input = "template.sql"
output = "output.sql"

```toml

[jinja2][project]                          # 🔵 REQUERIDO

enabled = trueinput = "..."                      # 🔴 OBLIGATORIO

```output = "..."                     # 🔴 OBLIGATORIO

verbose = false                    # 🟢 OPCIONAL (default: false)

### With SQLPlus Extensioncreate_backup = false              # 🟢 OPCIONAL (default: false)



Add SQLPlus compatibility (includes and variables):[plugins.nombre_plugin]            # 🟢 OPCIONAL (toda la sección)

enabled = true                     # 🔴 OBLIGATORIO si defines el plugin

```toml

[project]```

input_file = "main.sql"

output_file = "output.sql"## Quick Start



[jinja2]1. Create `MKFSource.toml` in your project directory:

enabled = true   ```bash

   # Create a new configuration file

[jinja2.extensions]   touch MKFSource.toml

sqlplus = true   ```



[jinja2.extensions.sqlplus]2. **Minimum viable configuration** (processes SQL*Plus includes and variables):

process_includes = true   ```toml

process_defines = true   [project]

```   input = "main.sql"              # 🔴 OBLIGATORIO

   output = "output.sql"           # 🔴 OBLIGATORIO

### With Jinja2 Variables   execution_order = ["sqlplus_includes", "sqlplus_vars"]  # 🔴 OBLIGATORIO

   

Use external variable files:   [plugins.sqlplus_includes]

   enabled = true                  # 🔴 OBLIGATORIO

```toml   

[project]   [plugins.sqlplus_vars]

input_file = "template.sql"   enabled = true                  # 🔴 OBLIGATORIO

output_file = "output.sql"   ```



[jinja2]3. Run the tool (no arguments needed, reads from `MKFSource.toml`):

enabled = true   ```bash

vars_file = "variables.json"   mergesourcefile

   ```

[jinja2.extensions.sqlplus]   

process_includes = true   **Note**: The tool only reads from `MKFSource.toml` in the current directory. There are no command-line parameters.

process_defines = true

```## What Changed in v2.0.0



## Configuration Sections**BREAKING CHANGES**:

- ❌ **Legacy format removed**: `[mergesourcefile]` section no longer supported

### `[project]` Section- ✅ **New hierarchical format**: `[project]`, `[plugins.*]` sections

- ✅ **Plugin architecture**: Modular, extensible processing system

Project-level settings that control input/output and general behavior.- ✅ **Configurable pipeline**: Custom execution order for plugins

- ✅ **Separate plugin configs**: Individual configuration for each plugin

#### Parameters

**Migration from v1.x to v2.0.0**:

| Parameter | Type | Required | Default | Description |```toml

|-----------|------|----------|---------|-------------|# Old format (v1.x - NO LONGER SUPPORTED)

| `input_file` | string | ✅ Yes | - | Path to input SQL/template file |[mergesourcefile]

| `output_file` | string | ✅ Yes | - | Path to output file |input = "main.sql"

| `backup` | boolean | No | `false` | Create backup before writing output |output = "output.sql"

| `verbose` | boolean | No | `false` | Enable verbose logging |jinja2 = true

jinja2_vars = "vars.json"

#### Exampleskip_var = false

processing_order = "default"

```toml

[project]# New format (v2.0.0 - REQUIRED)

input_file = "templates/main.sql"[project]

output_file = "build/output.sql"input = "main.sql"

backup = trueoutput = "output.sql"

verbose = falseverbose = false

```

[plugins.sqlplus]

### `[jinja2]` Sectionenabled = true

skip_var = false

Core Jinja2 template engine configuration.

[plugins.jinja2]

#### Parametersenabled = true

variables_file = "vars.json"

| Parameter | Type | Required | Default | Description |

|-----------|------|----------|---------|-------------|# execution_order moved to [project] section: execution_order = ["sqlplus_includes", "jinja2", "sqlplus_vars"]

| `enabled` | boolean | No | `true` | Enable Jinja2 (always true) |```

| `vars_file` | string | No | - | JSON file with template variables |

| `variable_start_string` | string | No | `"{{` | Jinja2 variable start delimiter |## Configuration File Structure

| `variable_end_string` | string | No | `"}}"` | Jinja2 variable end delimiter |

| `block_start_string` | string | No | `"{%"` | Jinja2 block start delimiter |### Complete Example with All Options

| `block_end_string` | string | No | `"%}"` | Jinja2 block end delimiter |

| `comment_start_string` | string | No | `"{#"` | Jinja2 comment start delimiter |```toml

| `comment_end_string` | string | No | `"#}"` | Jinja2 comment end delimiter |# MKFSource.toml - Configuration for MergeSourceFile v2.0.0

| `strict_undefined` | boolean | No | `false` | Raise error on undefined variables |# This file must be located in the current directory



#### Example[project]

# 🔴 OBLIGATORIO: Archivos de entrada y salida

```tomlinput = "main.sql"                  # Archivo SQL de entrada a procesar

[jinja2]output = "merged_output.sql"        # Archivo de salida con el resultado

enabled = true

vars_file = "config/variables.json"# 🟢 OPCIONAL: Opciones generales

variable_start_string = "{{"verbose = true                      # Muestra logs detallados (default: false)

variable_end_string = "}}"create_backup = false               # Crea backup antes de sobrescribir (default: false)

strict_undefined = false

```# 🟢 OPCIONAL: Plugins - Solo define los que necesites

[plugins.sqlplus_includes]

#### Variables File Formatenabled = true                      # 🔴 OBLIGATORIO si defines esta sección



The `vars_file` should be a JSON file:[plugins.sqlplus_vars]

enabled = true                      # 🔴 OBLIGATORIO si defines esta sección

```jsonskip_var = false                    # 🟢 OPCIONAL (default: false)

{

  "database": "production",[plugins.jinja2]

  "schema": "app_schema",enabled = true                      # 🔴 OBLIGATORIO si defines esta sección

  "table_prefix": "tbl_",variables_file = "variables.json"   # 🟢 OPCIONAL: archivo JSON con variables

  "version": "2.0.0",

  "timestamp": "2025-10-24"# 🔴 OBLIGATORIO: Pipeline (si definiste algún plugin)

}# execution_order moved to [project] section: execution_order = ["sqlplus_includes", "jinja2", "sqlplus_vars"]

``````



Use in template:## Configuration Parameters

```sql

-- Database: {{ database }}### [project] Section - 🔵 REQUERIDO

-- Schema: {{ schema }}

CREATE TABLE {{ table_prefix }}users (Esta sección **DEBE existir** en todo archivo de configuración.

    id NUMBER PRIMARY KEY,

    version VARCHAR2(10) DEFAULT '{{ version }}'| Parameter | Type | Required | Default | Description |

);|-----------|------|----------|---------|-------------|

```| `input` | string | 🔴 **Sí** | N/A | Archivo SQL de entrada a procesar |

| `output` | string | 🔴 **Sí** | N/A | Archivo de salida con el resultado procesado |

### `[jinja2.extensions]` Section| `verbose` | boolean | 🟢 No | `false` | Muestra información detallada del procesamiento |

| `create_backup` | boolean | 🟢 No | `false` | Crea backup (.backup) antes de sobrescribir |

Enable optional preprocessing extensions.

**Validaciones**:

#### Parameters- ❌ `input` y `output` no pueden estar vacíos

- ❌ El archivo de entrada debe existir (validado en tiempo de ejecución)

| Parameter | Type | Required | Default | Description |

|-----------|------|----------|---------|-------------|### [plugins.sqlplus_includes] Section - 🟢 OPCIONAL

| `sqlplus` | boolean | No | `false` | Enable SQLPlus compatibility extension |

Plugin para resolver inclusiones `@` y `@@` de SQL*Plus.

#### Example

| Parameter | Type | Required | Default | Description |

```toml|-----------|------|----------|---------|-------------|

[jinja2.extensions]| `enabled` | boolean | 🔴 **Sí** (si defines sección) | N/A | Activa/desactiva el plugin |

sqlplus = true

```### [plugins.sqlplus_vars] Section - 🟢 OPCIONAL



### `[jinja2.extensions.sqlplus]` SectionPlugin para sustitución de variables `DEFINE`/`UNDEFINE`.



SQLPlus extension configuration (only relevant if `sqlplus = true` above).| Parameter | Type | Required | Default | Description |

|-----------|------|----------|---------|-------------|

#### Parameters| `enabled` | boolean | 🔴 **Sí** (si defines sección) | N/A | Activa/desactiva el plugin |

| `skip_var` | boolean | 🟢 No | `false` | Omite procesamiento de variables |

| Parameter | Type | Required | Default | Description |

|-----------|------|----------|---------|-------------|### [plugins.jinja2] Section - 🟢 OPCIONAL

| `process_includes` | boolean | No | `true` | Process @ and @@ include directives |

| `process_defines` | boolean | No | `true` | Process DEFINE/UNDEFINE and &variables |Plugin para procesamiento de plantillas Jinja2.



#### Example| Parameter | Type | Required | Default | Description |

|-----------|------|----------|---------|-------------|

```toml| `enabled` | boolean | 🔴 **Sí** (si defines sección) | N/A | Activa/desactiva el plugin |

[jinja2.extensions.sqlplus]| `variables_file` | string | 🟢 No | `null` | Archivo JSON con variables para Jinja2 |

process_includes = true   # Process @file and @@file

process_defines = true    # Process DEFINE and &variables### Processing Order Strategies

```

Elige el orden de ejecución según tu flujo de trabajo:

## Complete Configuration Example

```toml

```toml# Estrategia 1: Por defecto (Includes → Jinja2 → Variables)

# ============================================================================# Usa cuando: Los archivos incluidos pueden contener plantillas Jinja2

# MergeSourceFile v2.0.0 Configurationexecution_order = ["sqlplus_includes", "jinja2", "sqlplus_vars"]

# ============================================================================

# Estrategia 2: Jinja2 primero (Jinja2 → Includes → Variables)

# --- Project Settings ---# Usa cuando: Jinja2 determina qué archivos incluir

[project]execution_order = ["jinja2", "sqlplus_includes", "sqlplus_vars"]

input_file = "src/main.sql"

output_file = "build/merged_output.sql"# Estrategia 3: Solo SQL*Plus (Includes → Variables)

backup = true           # Create backup of output file# Usa cuando: No necesitas Jinja2

verbose = true          # Enable detailed loggingexecution_order = ["sqlplus_includes", "sqlplus_vars"]



# --- Jinja2 Template Engine ---# Estrategia 4: Solo Jinja2

[jinja2]# Usa cuando: Solo procesas plantillas

enabled = trueexecution_order = ["jinja2"]

vars_file = "config/variables.json"```



# Custom delimiters (optional)## Usage Examples

variable_start_string = "{{"

variable_end_string = "}}"### Minimum Configuration (Solo SQL*Plus)

block_start_string = "{%"```toml

block_end_string = "%}"[project]

comment_start_string = "{#"input = "database_schema.sql"       # 🔴 OBLIGATORIO

comment_end_string = "#}"output = "deployment_script.sql"    # 🔴 OBLIGATORIO



# Strict mode: error on undefined variables[plugins.sqlplus_includes]

strict_undefined = falseenabled = true                      # 🔴 OBLIGATORIO



# --- Extensions ---[plugins.sqlplus_vars]

[jinja2.extensions]enabled = true                      # 🔴 OBLIGATORIO

sqlplus = true          # Enable SQLPlus compatibility

# execution_order moved to [project] section: execution_order = ["sqlplus_includes", "sqlplus_vars"]  # 🔴 OBLIGATORIO

[jinja2.extensions.sqlplus]```

process_includes = true  # Process @file and @@file directives

process_defines = true   # Process DEFINE var='value' and &var### With Jinja2 Templates

``````toml

[project]

## Configuration Use Casesinput = "template.sql"              # 🔴 OBLIGATORIO

output = "generated.sql"             # 🔴 OBLIGATORIO

### Use Case 1: Pure Jinja2 Templates

[plugins.sqlplus_includes]

**Scenario**: You only need Jinja2 templating with variables.enabled = true                       # 🔴 OBLIGATORIO



```toml[plugins.sqlplus_vars]

[project]enabled = true                       # 🔴 OBLIGATORIO

input_file = "template.sql"

output_file = "output.sql"[plugins.jinja2]

enabled = true                       # 🔴 OBLIGATORIO

[jinja2]variables_file = "production_vars.json"  # 🟢 OPCIONAL

enabled = true

vars_file = "vars.json"# execution_order moved to [project] section: execution_order = ["jinja2", "sqlplus_includes", "sqlplus_vars"]  # 🔴 OBLIGATORIO

``````



**Input** (`template.sql`):### Verbose Debugging

```sql```toml

-- Environment: {{ environment }}[project]

{% if environment == "production" %}input = "debug.sql"                  # 🔴 OBLIGATORIO

ALTER SYSTEM SET sga_target = 8G;output = "debug_output.sql"          # 🔴 OBLIGATORIO

{% else %}verbose = true                       # 🟢 OPCIONAL: activar logs detallados

ALTER SYSTEM SET sga_target = 2G;

{% endif %}[plugins.sqlplus_includes]

```enabled = true                       # 🔴 OBLIGATORIO



**Variables** (`vars.json`):[plugins.sqlplus_vars]

```jsonenabled = true                       # 🔴 OBLIGATORIO

{skip_var = false                     # 🟢 OPCIONAL (default: false)

  "environment": "production"

}# execution_order moved to [project] section: execution_order = ["sqlplus_includes", "sqlplus_vars"]  # 🔴 OBLIGATORIO

``````



### Use Case 2: SQLPlus Includes Only### Skip Variable Processing

```toml

**Scenario**: Legacy SQLPlus scripts with `@` includes, no templating.[project]

input = "static_script.sql"          # 🔴 OBLIGATORIO

```tomloutput = "merged_static.sql"         # 🔴 OBLIGATORIO

[project]

input_file = "main.sql"[plugins.sqlplus_includes]

output_file = "merged.sql"enabled = true                       # 🔴 OBLIGATORIO



[jinja2][plugins.sqlplus_vars]

enabled = trueenabled = true                       # 🔴 OBLIGATORIO

skip_var = true                      # 🟢 OPCIONAL: omitir DEFINE/UNDEFINE

[jinja2.extensions]

sqlplus = true# execution_order moved to [project] section: execution_order = ["sqlplus_includes", "sqlplus_vars"]  # 🔴 OBLIGATORIO

```

[jinja2.extensions.sqlplus]

process_includes = true### Advanced: Solo Jinja2 (Sin SQL*Plus)

process_defines = false```toml

```[project]

input = "app_template.sql"           # 🔴 OBLIGATORIO

**Input** (`main.sql`):output = "app_generated.sql"         # 🔴 OBLIGATORIO

```sqlcreate_backup = true                 # 🟢 OPCIONAL: crear .backup antes de sobrescribir

@scripts/create_tables.sqlexecution_order = ["jinja2"]

@scripts/create_indexes.sql

@@local_config.sql[plugins.jinja2]

```enabled = true                       # 🔴 OBLIGATORIO

variables_file = "app_config.json"   # 🟢 OPCIONAL         # 🔴 OBLIGATORIO

### Use Case 3: SQLPlus Variables Only```



**Scenario**: Legacy scripts with DEFINE variables.## Running MergeSourceFile



```toml```powershell

[project]# Ejecuta en el directorio que contiene MKFSource.toml

input_file = "deploy.sql"mergesourcefile

output_file = "deploy_expanded.sql"

# La herramienta realizará:

[jinja2]# 1. Buscar MKFSource.toml en el directorio actual

enabled = true# 2. Leer la configuración

# 3. Procesar tus archivos SQL según los plugins habilitados

[jinja2.extensions]# 4. Generar el resultado en el archivo de salida especificado

sqlplus = true```



[jinja2.extensions.sqlplus]## Best Practices

process_includes = false

process_defines = true1. **Control de versiones**: Incluye `MKFSource.toml` en tu repositorio Git

```2. **Configuraciones por entorno**: Crea archivos separados para diferentes entornos (`MKFSource.dev.toml`, `MKFSource.prod.toml`)

3. **Documentación inline**: Añade comentarios en el TOML para explicar configuraciones complejas

**Input** (`deploy.sql`):4. **Validación con verbose**: Prueba con `verbose = true` para verificar el orden de procesamiento

```sql5. **Un archivo por proyecto**: Mantén un `MKFSource.toml` por configuración de build

DEFINE schema='HR'6. **Minimiza plugins**: Solo habilita los plugins que realmente necesites

DEFINE version='2.0'7. **Backups en producción**: Usa `create_backup = true` cuando sobrescribas archivos críticos



CREATE TABLE &schema..employees (## Troubleshooting

    id NUMBER,

    version VARCHAR2(10) DEFAULT '&version'### Missing Configuration File

);```

```ERROR: No se encontró el archivo de configuración

======================================================================

### Use Case 4: Full Stack (Includes + Variables + Jinja2)Archivo buscado: MKFSource.toml

Directorio actual: C:\Users\usuario\proyecto

**Scenario**: Complex deployment with all features.

Para usar MergeSourceFile, necesitas crear un archivo 'MKFSource.toml'

```tomlen el directorio desde donde ejecutas el comando.

[project]```

input_file = "deploy/master.sql"**Solución**: Crea un archivo `MKFSource.toml` en el directorio actual.

output_file = "build/deployment.sql"

backup = true### Missing Required Parameters

verbose = true```

ERROR: Falta el parámetro 'input' requerido en la configuración

[jinja2]======================================================================

enabled = trueEl parámetro 'input' es obligatorio y no está definido.

vars_file = "config/env.json"

strict_undefined = trueTu archivo MKFSource.toml debe incluir:



[jinja2.extensions]  [project]

sqlplus = true  input = "tu_archivo_entrada.sql"

  output = "archivo_salida.sql"

[jinja2.extensions.sqlplus]```

process_includes = true**Solución**: Añade los campos 🔴 OBLIGATORIOS (`input` y `output`) a la sección `[project]`.

process_defines = true

```### Missing Pipeline Configuration

```

**Processing order**:ERROR: execution_order está vacío pero hay plugins habilitados

1. SQLPlus includes (`@`/`@@`) are expanded```

2. SQLPlus DEFINE variables (`&var`) are substituted**Solución**: Si definiste plugins en `

3. Jinja2 templates (`{{ var }}`, `{% if %}`) are renderedexecution_order = ["sqlplus_includes", "sqlplus_vars"]



### Use Case 5: Custom Delimiters[plugins.*]`, debes especificar el orden de ejecución:

```toml

**Scenario**: Jinja2 delimiters conflict with your SQL code.```



```toml### Plugin Not Found

[project]```

input_file = "template.sql"ERROR: Plugin 'mi_plugin' en execution_order no está disponible

output_file = "output.sql"======================================================================

Plugins disponibles: sqlplus_includes, jinja2, sqlplus_vars

[jinja2]```

enabled = true**Solución**: Verifica que el nombre del plugin sea correcto y esté en la lista de plugins disponibles.

vars_file = "vars.json"

### Invalid TOML Syntax

# Use <% %> style delimiters instead```

variable_start_string = "<%"ValueError: Error al parsear el archivo TOML: ...

variable_end_string = "%>"```

block_start_string = "<%#"**Solución**: Valida la sintaxis TOML. Causas comunes:

block_end_string = "#%>"- Comillas faltantes en strings

```- Secciones mal formateadas

- Valores booleanos incorrectos (usa `true`/`false` en minúsculas)

**Input** (`template.sql`):

```sql### File Not Found

-- Normal JSON operators work fine now: data->>'key'```

SELECT <% table_name %> FROM <% schema %>;FileNotFoundError: El archivo de entrada no existe: main.sql

<%# for col in columns #%>```

    , <% col %>**Solución**: Verifica que el archivo especificado en `input` exista en la ruta indicada.

<%# endfor #%>

```## Configuration Validation



## Migration from v1.xMergeSourceFile valida automáticamente tu configuración:



### Configuration Changes- **Campos obligatorios**: Verifica que `input` y `output` estén en `[project]`

- **Existencia de archivos**: Los archivos de entrada se verifican en tiempo de ejecución

**OLD (v1.x - NO LONGER SUPPORTED)**:- **Compatibilidad de parámetros**: Se rechaza `execution_order` con plugins no disponibles

```toml- **Validación de tipos**: Parámetros booleanos y strings se validan automáticamente

[mergesourcefile]- **Plugins habilitados**: Verifica que los plugins en `execution_order` tengan `enabled = true`

input = "main.sql"

output = "output.sql"**Nota**: La herramienta lee configuración **exclusivamente** de `MKFSource.toml` en el directorio actual. No hay parámetros de línea de comandos para especificar archivos alternativos.

jinja2 = true

jinja2_vars = "vars.json"## Configuration Examples by Use Case

skip_var = false

```### 1. Deployment Script Assembly (SQL*Plus Only)

```toml

**NEW (v2.0.0 - REQUIRED)**:# Caso de uso: Ensamblar múltiples archivos SQL en un script de despliegue

```toml[project]

[project]input = "deploy_master.sql"          # 🔴 OBLIGATORIO

input_file = "main.sql"output = "deploy_production.sql"     # 🔴 OBLIGATORIO

output_file = "output.sql"create_backup = true                 # 🟢 OPCIONAL: protege salidas existentes



[jinja2][plugins.sqlplus_includes]

enabled = trueenabled = true                       # 🔴 OBLIGATORIO

vars_file = "vars.json"

[plugins.sqlplus_vars]

[jinja2.extensions]enabled = true                       # 🔴 OBLIGATORIO

sqlplus = true

# execution_order moved to [project] section: execution_order = ["sqlplus_includes", "sqlplus_vars"]  # 🔴 OBLIGATORIO

[jinja2.extensions.sqlplus]```

process_defines = true

process_includes = true### 2. Template Generation (Jinja2 + SQL*Plus)

``````toml

# Caso de uso: Generar SQL desde plantillas con variables de entorno

### Key Differences[project]

input = "schema_template.sql"        # 🔴 OBLIGATORIO

| v1.x | v2.0.0 | Notes |output = "schema_prod.sql"           # 🔴 OBLIGATORIO

|------|--------|-------|verbose = true                       # 🟢 OPCIONAL: debug durante desarrollo

| `[mergesourcefile]` | `[project]` | Section renamed |

| `input` | `input_file` | Parameter renamed |[plugins.jinja2]

| `output` | `output_file` | Parameter renamed |enabled = true                       # 🔴 OBLIGATORIO

| `jinja2 = true` | `[jinja2]` section | Now a full section |variables_file = "prod_config.json"  # 🟢 OPCIONAL: variables externas

| `jinja2_vars` | `vars_file` | Parameter renamed |

| `skip_var` | `process_defines` | Inverted logic |[plugins.sqlplus_includes]

| N/A | `[jinja2.extensions]` | New extension system |enabled = true                       # 🔴 OBLIGATORIO

| `processing_order` | Fixed order | No longer configurable |

[plugins.sqlplus_vars]

## Environment Variablesenabled = true                       # 🔴 OBLIGATORIO



MergeSourceFile does **not** currently support environment variable substitution in configuration files. All values must be literal.[project]

# Primero Jinja2 para generar código SQL, luego incluir archivos, finalmente variables

**Not supported**:execution_order = ["jinja2", "sqlplus_includes", "sqlplus_vars"]  # 🔴 OBLIGATORIO

```toml```

[project]

input_file = "${INPUT_FILE}"  # ❌ Won't work### 3. Pure Template Processing (Solo Jinja2)

```### 3. Pure Template Processing (Solo Jinja2)

```toml

**Workaround**: Generate configuration dynamically:# Caso de uso: Generación de SQL dinámico solo con plantillas (sin SQL*Plus)

```bash[project]

# Generate config from templateinput = "query_template.sql"         # 🔴 OBLIGATORIO

sed "s/INPUT_PLACEHOLDER/$INPUT_FILE/g" MKFSource.toml.template > MKFSource.tomloutput = "query_generated.sql"       # 🔴 OBLIGATORIO

mergesourcefileexecution_order = ["jinja2"]

```

[plugins.jinja2]

## Configuration Validationenabled = true                       # 🔴 OBLIGATORIO

variables_file = "query_params.json" # 🟢 OPCIONAL         # 🔴 OBLIGATORIO

MergeSourceFile validates configuration on startup:```



### Required Parameters---

```

✅ [project].input_file## Summary: Quick Reference

✅ [project].output_file

```| **Elemento** | **¿Es Obligatorio?** | **Cuándo** |

|-------------|---------------------|-----------|

### Optional Parameters (with defaults)| `[project]` | 🔴 **Sí, siempre** | Toda configuración debe tener esta sección |

```| `[project].input` | 🔴 **Sí, siempre** | Debe especificar el archivo de entrada |

[project].backup = false| `[project].output` | 🔴 **Sí, siempre** | Debe especificar el archivo de salida |

[project].verbose = false| `[project].verbose` | 🟢 No | Solo si necesitas logs detallados |

[jinja2].enabled = true| `[project].create_backup` | 🟢 No | Solo si quieres respaldo automático |

[jinja2].strict_undefined = false| `[plugins.*]` | 🟢 No | Solo define los plugins que necesites |

[jinja2.extensions].sqlplus = false| `[plugins.*].enabled` | 🔴 **Sí, si defines plugin** | Debe estar en cada sección `[plugins.*]` que crees |

[jinja2.extensions.sqlplus].process_includes = true| `[project].execution_order` | 🔴 **Sí** (si usas plugins) | Orden de ejecución de plugins |

[jinja2.extensions.sqlplus].process_defines = true

```### Minimum Valid Configuration (Sin Plugins)

```toml

### Error Messages[project]

input = "input.sql"

**Missing required field**:output = "output.sql"

``````

ValueError: Campo requerido 'input_file' no encontrado en configuración✅ **Válido**: No procesa nada, solo copia el archivo.

```

### Minimum Useful Configuration (Con Plugins)

**File not found**:```toml

```[project]

FileNotFoundError: Archivo de configuración no encontrado: MKFSource.tomlinput = "master.sql"

```output = "merged.sql"

execution_order = ["sqlplus_includes"]

**Invalid TOML syntax**:

```[plugins.sqlplus_includes]

ValueError: Error al parsear archivo de configuración: Expected '=' after a key in a key/value pair (at line 5, column 10)enabled = true

``````

✅ **Válido**: Procesa inclusiones `@` y `@@`.

## Best Practices

---

### 1. Use Explicit Configuration

```tomlPara más detalles, consulta los documentos:

# ✅ Good: Explicit and clear- `docs_trabajo/config.example.toml` - Ejemplo completo comentado

[jinja2.extensions.sqlplus]- `EXAMPLES.md` - Casos de uso detallados

process_includes = true- `API_DOCUMENTATION.md` - Referencia de la API interna

process_defines = true

### Multiple Configurations for Different Environments

# ❌ Bad: Relying on defaults

[jinja2.extensions.sqlplus]Maintain separate configuration files and copy the appropriate one before running:

# (implicit defaults)

``````bash

# Development build

### 2. Version Your Configurationcp MKFSource.dev.toml MKFSource.toml

```tomlmergesourcefile

# Add metadata as comments

# MergeSourceFile v2.0.0 Configuration# Production build  

# Project: MyApp Database Schemacp MKFSource.prod.toml MKFSource.toml

# Last Updated: 2025-10-24mergesourcefile

# Author: DevOps Team

# Or use a script to automate

[project]./build.sh dev    # Copies MKFSource.dev.toml and runs mergesourcefile

input_file = "schema.sql"./build.sh prod   # Copies MKFSource.prod.toml and runs mergesourcefile

output_file = "build/schema_merged.sql"```

```

**Note**: The tool only reads from `MKFSource.toml` in the current directory. There is no `--config` parameter.

### 3. Separate Environments

```bash## Related Documentation

# Different configs for different environments

MKFSource.dev.toml- [README.md](README.md) - General usage and installation

MKFSource.test.toml- [EXAMPLES.md](EXAMPLES.md) - Practical usage examples

MKFSource.prod.toml- [CHANGELOG.md](CHANGELOG.md) - Version history and changes

# Copy appropriate one
cp MKFSource.prod.toml MKFSource.toml
mergesourcefile
```

### 4. Document Your Variables
```json
{
  "_comment": "Variables for production deployment",
  "environment": "production",
  "db_host": "prod-db-01.example.com",
  "schema": "PROD_SCHEMA",
  "version": "2.0.0"
}
```

### 5. Use Backup for Critical Files
```toml
[project]
input_file = "critical_schema.sql"
output_file = "critical_schema.sql"  # Overwriting source
backup = true  # ✅ Always backup when overwriting
```

## Troubleshooting

### Configuration Not Found
```
FileNotFoundError: Archivo de configuración no encontrado: MKFSource.toml
```

**Solution**: Create `MKFSource.toml` in current directory:
```bash
pwd  # Verify you're in the right directory
ls MKFSource.toml  # Check file exists
```

### Variable File Not Found
```
FileNotFoundError: Variables file not found: vars.json
```

**Solution**: Check path relative to working directory:
```bash
# If vars.json is in config/ subdirectory
[jinja2]
vars_file = "config/vars.json"  # ✅ Relative path
```

### Undefined Variable
```
jinja2.exceptions.UndefinedError: 'table_name' is undefined
```

**Solution**: Add variable to vars_file or use `strict_undefined = false`:
```toml
[jinja2]
strict_undefined = false  # Allow undefined variables
```

### SQLPlus Extension Not Working
```
# @ directives not being processed
```

**Solution**: Enable SQLPlus extension:
```toml
[jinja2.extensions]
sqlplus = true

[jinja2.extensions.sqlplus]
process_includes = true
```

## Configuration Schema Reference

```toml
# ============================================================================
# Complete Configuration Schema (all possible parameters)
# ============================================================================

[project]
input_file = ""         # string, required
output_file = ""        # string, required
backup = false          # boolean, optional (default: false)
verbose = false         # boolean, optional (default: false)

[jinja2]
enabled = true          # boolean, optional (default: true, always true in practice)
vars_file = ""          # string, optional (default: none)
variable_start_string = "{{"      # string, optional
variable_end_string = "}}"        # string, optional
block_start_string = "{%"         # string, optional
block_end_string = "%}"           # string, optional
comment_start_string = "{#"       # string, optional
comment_end_string = "#}"         # string, optional
strict_undefined = false          # boolean, optional (default: false)

[jinja2.extensions]
sqlplus = false         # boolean, optional (default: false)

[jinja2.extensions.sqlplus]
process_includes = true  # boolean, optional (default: true)
process_defines = true   # boolean, optional (default: true)
```

## References

- [Architecture Documentation](ARCHITECTURE.md) - System design and components
- [API Documentation](API_DOCUMENTATION.md) - Python API reference
- [Examples](EXAMPLES.md) - Usage examples and patterns
- [Changelog](CHANGELOG.md) - Version history and migration notes

---

**Last Updated**: October 2025  
**Version**: 2.0.0  
**Configuration Format**: TOML
