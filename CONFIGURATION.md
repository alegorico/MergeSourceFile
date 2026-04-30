# MergeSourceFile Configuration Guide

## Overview

MergeSourceFile v2.0.0 features a **streamlined unified architecture** with centralized extension management. Configuration is stored in `MKFSource.toml` using the TOML format. The tool reads from a file named `MKFSource.toml` located in the current directory.

### 🚀 Quick Command Reference

```bash
# Use the short command (recommended)
msf

# Or the full command name
mergesourcefile
```

### ⚠️ Important: Include System Conflict Resolution

MergeSourceFile implements **automatic conflict resolution** between include systems:

- **SQLPlus includes active** (`process_includes = true`) → Jinja2 `{% include %}` **DISABLED**
- **SQLPlus includes inactive** → Jinja2 `{% include %}` **ENABLED**

This prevents conflicts between `@file.sql` (SQLPlus) and `{% include "file.sql" %}` (Jinja2) systems.

## Configuration Requirements

### Legend

- 🔴 **REQUIRED**: This parameter MUST be present in the file
- 🟢 **OPTIONAL**: This parameter can be omitted (default value will be used)
- 🔵 **REQUIRED**: This section MUST exist in the file
- 🟡 **CONDITIONAL**: Required only if certain conditions are met

## Quick Start

### 1. Minimal Configuration (Jinja2 only)

The simplest possible configuration:

```toml
[project]
input = "template.sql"
output = "output.sql"

[jinja2]
enabled = true
```

### 2. With SQLPlus Extension

Add SQLPlus compatibility (includes and variables):

```toml
[project]
input = "main.sql"
output = "output.sql"

[jinja2]
enabled = true

[jinja2.extensions]
sqlplus = true

[jinja2.extensions.sqlplus]
resolve_includes = true
resolve_variables = true
```

### 3. With External Variables

Use external variable files:

```toml
[project]
input = "template.sql"
output = "output.sql"

[jinja2]
enabled = true
variables_file = "variables.yaml"

[jinja2.extensions]
sqlplus = true
```

## Configuration Sections

### `[project]` Section 🔵

Project-level settings that control input/output and general behavior.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `input` | string | 🔴 Yes | - | Path to input SQL/template file |
| `output` | string | 🔴 Yes | - | Path to output file |
| `verbose` | boolean | 🟢 No | `false` | Enable verbose logging |
| `create_backup` | boolean | 🟢 No | `false` | Create backup before writing output |

#### Example

```toml
[project]
input = "templates/main.sql"
output = "build/output.sql"
verbose = true
create_backup = true
```

### `[jinja2]` Section 🔵

Core Jinja2 template engine configuration.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `enabled` | boolean | 🔴 Yes | `true` | Enable Jinja2 processing |
| `variables_file` | string | 🟢 No | - | YAML file with template variables |
| `variable_start_string` | string | 🟢 No | `"{{` | Jinja2 variable start delimiter |
| `variable_end_string` | string | 🟢 No | `"}}"` | Jinja2 variable end delimiter |
| `block_start_string` | string | 🟢 No | `"{%"` | Jinja2 block start delimiter |
| `block_end_string` | string | 🟢 No | `"%}"` | Jinja2 block end delimiter |
| `comment_start_string` | string | 🟢 No | `"{#"` | Jinja2 comment start delimiter |
| `comment_end_string` | string | 🟢 No | `"#}"` | Jinja2 comment end delimiter |
| `strict_undefined` | boolean | 🟢 No | `false` | Raise error on undefined variables |

#### Example

```toml
[jinja2]
enabled = true
variables_file = "vars.yaml"
variable_start_string = "{{"
variable_end_string = "}}"
strict_undefined = true
```

### `[jinja2.extensions]` Section 🟢

Optional extensions configuration.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `sqlplus` | boolean | 🟢 No | `false` | Enable SQLPlus compatibility |

#### Example

```toml
[jinja2.extensions]
sqlplus = true
```

### `[jinja2.extensions.sqlplus]` Section 🟡

SQLPlus extension configuration. Only required if `sqlplus = true`.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `process_includes` | boolean | 🟢 No | `true` | Process `@` and `@@` file inclusions |
| `process_defines` | boolean | 🟢 No | `true` | Process `DEFINE` and `UNDEFINE` commands |

#### ⚠️ Include System Behavior

When `process_includes = true`:
- ✅ SQLPlus includes (`@file`, `@@file`) work normally
- ❌ Jinja2 includes (`{% include "file" %}`) are **DISABLED** to prevent conflicts

When `process_includes = false`:
- ❌ SQLPlus includes are ignored
- ✅ Jinja2 includes work normally

#### Example

```toml
[jinja2.extensions.sqlplus]
process_includes = true    # SQLPlus includes active, Jinja2 includes disabled
process_defines = true     # Process DEFINE/UNDEFINE variables
```

## Complete Configuration Examples

### Example 1: Basic Jinja2 Processing

```toml
[project]
input = "template.sql"
output = "output.sql"
verbose = false

[jinja2]
enabled = true
variables_file = "production.yaml"
```

### Example 2: SQLPlus Migration

```toml
[project]
input = "legacy_main.sql"
output = "modernized_output.sql"
verbose = true
create_backup = true

[jinja2]
enabled = true

[jinja2.extensions]
sqlplus = true

[jinja2.extensions.sqlplus]
process_includes = true    # SQLPlus includes enabled, Jinja2 includes disabled
process_defines = true     # Process DEFINE/UNDEFINE variables
```

### Example 3: Advanced Template Processing

```toml
[project]
input = "advanced_template.sql"
output = "generated_schema.sql"
verbose = true

[jinja2]
enabled = true
variables_file = "schema_vars.yaml"
variable_start_string = "${"
variable_end_string = "}"
block_start_string = "<%"
block_end_string = "%>"
strict_undefined = true

[jinja2.extensions]
sqlplus = true

[jinja2.extensions.sqlplus]
process_includes = false   # SQLPlus includes disabled, Jinja2 includes enabled
process_defines = false    # Only Jinja2 variables
```

## Dynamic Configuration & Environments

MergeSourceFile v2.0.4+ includes powerful features to integrate with CI/CD pipelines and task runners like `invoke`.

### 1. `MSF_CONFIG` Environment Variable

Instead of running from the directory where `MKFSource.toml` is located, you can define the `MSF_CONFIG` environment variable to point to any configuration file. This is ideal for supporting multiple environments.

```bash
# Set configuration for a specific environment
export MSF_CONFIG="./configs/production.toml"
msf
```

### 2. Environment Variable Interpolation

You can use environment variables directly inside your TOML configuration files using the `${VAR_NAME}` or `$VAR_NAME` syntax. These will be interpolated before the configuration is processed.

```toml
[project]
input = "${PROJECT_ROOT}/src/main.sql"
output = "${BUILD_DIR}/generated_${ENV}.sql"

[jinja2]
enabled = true
variables_file = "${PROJECT_ROOT}/vars/${ENV}.yaml"
```

### 3. Smart Relative Paths

If you use relative paths in your TOML configuration, they will **always be resolved relative to the directory where the TOML file is located**, NOT the current working directory from where you executed the command.

This allows you to safely place your configs in subdirectories:
```
my_project/
├── configs/
│   └── dev.toml      (input = "../src/schema.sql")
└── src/
    └── schema.sql
```
Running `MSF_CONFIG=configs/dev.toml msf` from the root will correctly resolve the input file to `./src/schema.sql`.

### 4. `.env` File Support

If you install the optional `python-dotenv` dependency (`pip install MergeSourceFile[dotenv]`), MergeSourceFile will automatically load variables from a `.env` file in your current directory before processing.

```env
# .env file
MSF_CONFIG=./configs/dev.toml
PROJECT_ROOT=/abs/path/to/project
```

## Variables File Format

When using `variables_file`, create a YAML file with your template variables:

### Example `variables.yaml`

```yaml
database: PROD_DB
schema: APP_SCHEMA
environment: production
version: 2.0.0
features:
  logging: true
  auditing: false
  encryption: true
tables:
  - name: users
    prefix: usr
  - name: products
    prefix: prd
  - name: orders
    prefix: ord
```

## Include System Management

### Understanding Include Systems

MergeSourceFile supports two include systems that serve different purposes:

1. **SQLPlus includes** (`@file`, `@@file`): Physical file expansion (legacy compatibility)
2. **Jinja2 includes** (`{% include "file" %}`): Template-based inclusion (modern approach)

### Conflict Resolution

To prevent ambiguity and conflicts, MergeSourceFile implements **automatic exclusion** between systems:

| Configuration | SQLPlus Includes | Jinja2 Includes | Use Case |
|---------------|------------------|-----------------|----------|
| No extensions | ❌ Disabled | ✅ **Active** | Modern Jinja2 only |
| `process_includes = true` | ✅ **Active** | ❌ Disabled | Legacy SQLPlus compatibility |
| `process_includes = false` | ❌ Disabled | ✅ **Active** | Jinja2 with SQLPlus variables only |

### Configuration Examples

#### Pure Jinja2 (Recommended for new projects)
```toml
[project]
input = "template.sql"
output = "output.sql"

[jinja2]
enabled = true
# No SQLPlus extension = Jinja2 includes work normally
```

**Template usage:**
```sql
{% include "config/database.sql" %}
{% include "functions/utilities.sql" %}

SELECT * FROM {{ schema }}.{{ table }};
```

#### Legacy SQLPlus Support
```toml
[project]
input = "legacy.sql"
output = "output.sql"

[jinja2]
enabled = true
extensions = ["sqlplus"]

[jinja2.sqlplus]
process_includes = true    # Enables @file, disables {% include %}
process_defines = true     # Enables DEFINE variables
```

**Template usage:**
```sql
@config/database.sql
@@functions/utilities.sql

SELECT * FROM {{ schema }}.{{ table }};
```

#### Hybrid Approach (Variables only)
```toml
[project]
input = "hybrid.sql"
output = "output.sql"

[jinja2]
enabled = true
extensions = ["sqlplus"]

[jinja2.sqlplus]
process_includes = false   # Disables @file, enables {% include %}
process_defines = true     # Keeps DEFINE variables for migration
```

**Template usage:**
```sql
DEFINE schema=production_schema

{% include "config/database.sql" %}

SELECT * FROM &schema.{{ table }};
```

### Error Messages

If you use the wrong include system, you'll get clear error messages:

**Using `{% include %}` when SQLPlus includes are active:**
```
Error: Los includes de Jinja2 están deshabilitados porque la extensión 
SQLPlus está manejando las inclusiones. Use '@archivo' en lugar de 
'{% include "archivo" %}'
```

### Migration Strategy

1. **New projects**: Use pure Jinja2 includes
2. **Legacy migration**: Start with SQLPlus includes, gradually convert to Jinja2
3. **Hybrid approach**: Use SQLPlus variables with Jinja2 includes during transition

## Variable Namespace Management

### Understanding Variable Systems

MergeSourceFile handles two variable systems that can potentially conflict:

1. **SQLPlus variables** (`DEFINE var=value`, `&var`): Processed during pre-processing
2. **Jinja2 variables** (`{{ var }}`): Processed during template rendering

### Forced Namespace Separation

To prevent variable name conflicts, MergeSourceFile implements **forced namespace separation** for DEFINE variables:

| Variable Type | Original Syntax | Available in Jinja2 |
|---------------|-----------------|-------------------|
| SQLPlus DEFINE | `DEFINE env=prod` → `&env` | `{{ sql_env }}` |
| Jinja2 Variable | External/config | `{{ env }}` |

### Configuration Examples

#### Variables with Namespace Separation
```toml
[jinja2.extensions.sqlplus]
process_defines = true  # Extract DEFINE variables to Jinja2 context
```

**Template usage:**
```sql
DEFINE schema=production_schema
DEFINE env=prod

-- Original SQLPlus syntax (still works)
SELECT * FROM &schema.users WHERE env = '&env';

-- Available in Jinja2 with sql_ prefix
SELECT '{{ sql_schema }}' AS schema_from_define;
SELECT '{{ sql_env }}' AS env_from_define;

-- Mixed usage
SELECT * FROM {{ sql_schema }}.{{ table_name }} 
WHERE env = '{{ sql_env }}' AND status = '{{ status }}';
```

### Conflict Detection and Warnings

When a variable name exists in both systems, MergeSourceFile warns you:

```
WARNING: CONFLICTO DE VARIABLES: La variable 'schema' está definida tanto en 
SQLPlus como en Jinja2. Usando namespace forzado: SQLPlus 'schema' → Jinja2 '{{ sql_schema }}'
```

**Example scenario:**
```sql
DEFINE schema=sqlplus_value  -- Available as {{ sql_schema }}

SELECT '{{ schema }}' AS jinja_var;      -- Uses Jinja2 variable
SELECT '{{ sql_schema }}' AS sqlplus_var; -- Uses DEFINE variable
```

**Configuration:**
```toml
[jinja2]
enabled = true
variables_file = "vars.yaml"  # Contains: {"schema": "jinja_value"}

[jinja2.extensions.sqlplus]
process_defines = true
```

**Result:**
- `{{ schema }}` → `"jinja_value"`
- `{{ sql_schema }}` → `"sqlplus_value"`

### Best Practices for Variables

1. **Use descriptive names** to avoid conflicts
2. **Leverage the sql_ prefix** to access DEFINE variables in Jinja2
3. **Plan your variable strategy** early in the project
4. **Monitor warnings** for potential conflicts

## Migration from v1.x

### What Changed in v2.0.0

**BREAKING CHANGES**:
- ❌ **Legacy format removed**: `[mergesourcefile]` section no longer supported
- ✅ **New hierarchical format**: `[project]`, `[jinja2]` sections
- ✅ **Extension system**: Optional SQLPlus compatibility
- ✅ **Simplified configuration**: More intuitive parameter names

### Migration Example

**Old format (v1.x - NO LONGER SUPPORTED)**:
```toml
[mergesourcefile]
input = "main.sql"
output = "output.sql"
jinja2 = true
jinja2_vars = "vars.yaml"
skip_var = false
processing_order = "default"
```

**New format (v2.0.0 - REQUIRED)**:
```toml
[project]
input = "main.sql"
output = "output.sql"
verbose = false

[jinja2]
enabled = true
variables_file = "vars.yaml"

[jinja2.extensions]
sqlplus = true
```

## Best Practices

### File Organization

```
project/
├── MKFSource.toml          # Configuration file
├── template.sql            # Main template
├── variables.yaml          # Template variables
├── includes/               # Included SQL files
│   ├── common.sql
│   └── functions.sql
└── output/                 # Generated files
    └── result.sql
```

### Security Considerations

- **Validate paths**: Ensure include paths don't allow directory traversal
- **Limit depth**: Set reasonable `max_depth` to prevent infinite recursion  
- **Review variables**: Validate all variables before processing
- **Backup files**: Use `create_backup = true` for important files

### Performance Tips

- **Specific paths**: Use specific `include_paths` to avoid unnecessary scanning
- **Reasonable depth**: Don't set `max_depth` too high
- **Minimal extensions**: Only enable extensions you actually need
- **Variables file**: Use external YAML for complex variable structures

## Error Handling

### Common Configuration Errors

1. **Missing required sections**: Ensure `[project]` and `[jinja2]` sections exist
2. **Invalid file paths**: Check that input files exist and output directories are writable
3. **Malformed YAML**: Validate variables file YAML syntax
4. **Extension conflicts**: Don't mix incompatible processing options

### Example Error Messages

```
ConfigurationError: Missing required section [project]
FileNotFoundError: Input file 'template.sql' not found
YAMLError: Invalid YAML in variables file 'vars.yaml'
RecursionError: Maximum inclusion depth (10) exceeded
```

## Troubleshooting

### Enable Verbose Mode

Add verbose logging to diagnose issues:

```toml
[project]
input = "template.sql"
output = "output.sql"
verbose = true  # Enable detailed logging
```

### Check File Paths

Ensure all paths are relative to the configuration file location:

```toml
[project]
input = "./templates/main.sql"        # Explicit relative path
output = "./output/result.sql"        # Explicit relative path

[jinja2]
variables_file = "./vars/prod.yaml"   # Explicit relative path
```

### Validate Configuration

Test your configuration with minimal templates first:

```sql
-- test_template.sql
SELECT '{{ database }}' as db_name;
```

```yaml
# test_vars.yaml
database: TEST_DB
```

```toml
# MKFSource.toml
[project]
input = "test_template.sql"
output = "test_output.sql"
verbose = true

[jinja2]
enabled = true
variables_file = "test_vars.yaml"
```
