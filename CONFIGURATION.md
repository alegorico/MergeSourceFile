# MergeSourceFile Configuration Guide

## Overview

MergeSourceFile v2.0.0 uses a **Jinja2-centric architecture** with optional extensions. Configuration is stored in `MKFSource.toml` using the TOML format. The tool reads from a file named `MKFSource.toml` located in the current directory.

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
variables_file = "variables.json"

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
| `variables_file` | string | 🟢 No | - | JSON file with template variables |
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
variables_file = "vars.json"
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
| `resolve_includes` | boolean | 🟢 No | `true` | Process `@` and `@@` file inclusions |
| `resolve_variables` | boolean | 🟢 No | `true` | Process `DEFINE` and `UNDEFINE` commands |
| `include_paths` | array | 🟢 No | `["."]` | Search paths for included files |
| `max_depth` | integer | 🟢 No | `10` | Maximum inclusion depth |

#### Example

```toml
[jinja2.extensions.sqlplus]
resolve_includes = true
resolve_variables = true
include_paths = [".", "includes/", "common/"]
max_depth = 5
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
variables_file = "production.json"
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
resolve_includes = true
resolve_variables = true
include_paths = [".", "sql/includes/", "sql/common/"]
max_depth = 8
```

### Example 3: Advanced Template Processing

```toml
[project]
input = "advanced_template.sql"
output = "generated_schema.sql"
verbose = true

[jinja2]
enabled = true
variables_file = "schema_vars.json"
variable_start_string = "${"
variable_end_string = "}"
block_start_string = "<%"
block_end_string = "%>"
strict_undefined = true

[jinja2.extensions]
sqlplus = true

[jinja2.extensions.sqlplus]
resolve_includes = true
resolve_variables = false
include_paths = ["templates/", "schemas/"]
```

## Variables File Format

When using `variables_file`, create a JSON file with your template variables:

### Example `variables.json`

```json
{
  "database": "PROD_DB",
  "schema": "APP_SCHEMA",
  "environment": "production",
  "version": "2.0.0",
  "features": {
    "logging": true,
    "auditing": false,
    "encryption": true
  },
  "tables": [
    {"name": "users", "prefix": "usr"},
    {"name": "products", "prefix": "prd"},
    {"name": "orders", "prefix": "ord"}
  ]
}
```

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
jinja2_vars = "vars.json"
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
variables_file = "vars.json"

[jinja2.extensions]
sqlplus = true
```

## Best Practices

### File Organization

```
project/
├── MKFSource.toml          # Configuration file
├── template.sql            # Main template
├── variables.json          # Template variables
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
- **Variables file**: Use external JSON for complex variable structures

## Error Handling

### Common Configuration Errors

1. **Missing required sections**: Ensure `[project]` and `[jinja2]` sections exist
2. **Invalid file paths**: Check that input files exist and output directories are writable
3. **Malformed JSON**: Validate variables file JSON syntax
4. **Extension conflicts**: Don't mix incompatible processing options

### Example Error Messages

```
ConfigurationError: Missing required section [project]
FileNotFoundError: Input file 'template.sql' not found
JSONDecodeError: Invalid JSON in variables file 'vars.json'
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
variables_file = "./vars/prod.json"   # Explicit relative path
```

### Validate Configuration

Test your configuration with minimal templates first:

```sql
-- test_template.sql
SELECT '{{ database }}' as db_name;
```

```json
// test_vars.json
{
  "database": "TEST_DB"
}
```

```toml
# MKFSource.toml
[project]
input = "test_template.sql"
output = "test_output.sql"
verbose = true

[jinja2]
enabled = true
variables_file = "test_vars.json"
```