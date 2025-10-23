# MergeSourceFile Configuration Guide

## Configuration File Reference (v1.4.0)

MergeSourceFile v1.4.0 operates exclusively through configuration files. The tool reads from a file named `MKFSource.toml` located in the current directory.

## Quick Start

1. Create `MKFSource.toml` in your project directory:
   ```bash
   # Create a new configuration file
   touch MKFSource.toml
   ```

2. Edit the configuration file according to your needs

3. Run the tool (no arguments needed):
   ```bash
   mergesourcefile
   ```

## What Changed in v1.4.0

**BREAKING CHANGES**:
- ❌ **Removed all command-line parameters** (`--config`, `--input`, `--output`, etc.)
- ✅ **Standard configuration file**: Must be named `MKFSource.toml`
- ✅ **Located in current directory**: The tool looks for `MKFSource.toml` in `pwd`
- ✅ **Simplified CLI**: Just run `mergesourcefile` with no arguments

**Migration from v1.3.0**:
```bash
# Old way (v1.3.0)
mergesourcefile --config myconfig.toml

# New way (v1.4.0)
# Rename your config file to MKFSource.toml
mv myconfig.toml MKFSource.toml
mergesourcefile
```

## Configuration File Structure

### Complete Example

```toml
# MKFSource.toml - Configuration for MergeSourceFile v1.4.0
# This file must be located in the current directory

[mergesourcefile]
# Input and output files (REQUIRED)
input = "main.sql"
output = "merged_output.sql"

# Processing options
skip_var = false                    # true to skip DEFINE/UNDEFINE variable substitution
verbose = true                      # true to show detailed processing information

# Jinja2 template support
jinja2 = true                       # true to enable Jinja2 processing
jinja2_vars = "variables.json"      # JSON file with variables for Jinja2

# Processing order
processing_order = "jinja2_first"   # Options: "default", "jinja2_first", "includes_last"
```

## Configuration Parameters

### Required Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `input` | string | Input SQL file to process | `"main.sql"` |
| `output` | string | Output file for merged result | `"merged_output.sql"` |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip_var` | boolean | `false` | Skip DEFINE/UNDEFINE variable substitution |
| `verbose` | boolean | `false` | Enable detailed processing information |
| `jinja2` | boolean | `false` | Enable Jinja2 template processing |
| `jinja2_vars` | string | `null` | JSON file with Jinja2 variables |
| `processing_order` | string | `"default"` | Processing order strategy |

### Processing Order Options

- **`"default"`**: File inclusions → Jinja2 → SQL variables
- **`"jinja2_first"`**: Jinja2 → File inclusions → SQL variables  
- **`"includes_last"`**: Jinja2 → SQL variables → File inclusions

## Usage Examples

### Basic Configuration
```toml
[mergesourcefile]
input = "database_schema.sql"
output = "deployment_script.sql"
```

### With Jinja2 Templates
```toml
[mergesourcefile]
input = "template.sql"
output = "generated.sql"
jinja2 = true
jinja2_vars = "env_variables.json"
verbose = true
```

### Skip Variable Processing
```toml
[mergesourcefile]
input = "static_script.sql"
output = "merged_static.sql"
skip_var = true
processing_order = "jinja2_first"
```

## Running MergeSourceFile

```bash
# Simply run in the directory containing MKFSource.toml
mergesourcefile

# The tool will:
# 1. Look for MKFSource.toml in current directory
# 2. Read the configuration
# 3. Process your SQL files
# 4. Output the merged result
```

## Multiple Configurations for Different Environments

Maintain separate configuration files and copy the appropriate one:

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

## Best Practices

1. **Version Control**: Include your `MKFSource.toml` file in version control
2. **Environment-Specific**: Create separate config files for different environments (`MKFSource.dev.toml`, `MKFSource.prod.toml`)
3. **Documentation**: Add comments in your configuration files to explain complex setups
4. **Validation**: Test your configuration with `verbose = true` to verify processing order
5. **Project-Based**: Keep one `MKFSource.toml` per build configuration/project

## Troubleshooting

### Missing Configuration File
```
ERROR: No se encontró el archivo de configuración
======================================================================
Archivo buscado: MKFSource.toml
Directorio actual: /path/to/current/directory

Para usar MergeSourceFile, necesitas crear un archivo 'MKFSource.toml'
en el directorio desde donde ejecutas el comando.
```
**Solution**: Create a `MKFSource.toml` file in your current directory.

### Missing Required Parameters
```
ERROR: Parámetros requeridos faltantes
======================================================================
Faltan los siguientes parámetros requeridos en 'MKFSource.toml':
  - input
  - output
```
**Solution**: Add the required `input` and `output` fields to your `MKFSource.toml` file.
**Solution**: Ensure both `input` and `output` parameters are specified in your TOML file.

### Invalid TOML Syntax
```
ValueError: Error al parsear el archivo TOML: ...
```
**Solution**: Validate your TOML syntax using an online TOML validator or ensure proper quoting of string values.

### File Not Found
```
FileNotFoundError: Archivo de configuración no encontrado: config.toml
```
**Solution**: Verify the configuration file path and ensure the file exists.

## Configuration Validation

MergeSourceFile automatically validates your configuration:

- **Required fields**: `input` and `output` must be specified
- **File existence**: Input files are checked at runtime
- **Parameter compatibility**: Invalid processing orders are rejected
- **Type checking**: Boolean and string parameters are validated

## Advanced Configuration

### Multiple Configurations
You can maintain separate configuration files for different use cases:

```bash
# Development environment
mergesourcefile --config config.dev.toml

# Production deployment
mergesourcefile --config config.prod.toml

# Testing with minimal processing
mergesourcefile --config config.test.toml
```

### Complex Processing Pipeline
```toml
[mergesourcefile]
input = "complex_template.sql"
output = "final_deployment.sql"
jinja2 = true
jinja2_vars = "production_vars.json"
verbose = true
processing_order = "jinja2_first"
# This configuration processes Jinja2 templates first,
# then handles file inclusions, and finally SQL variables
```

## Related Documentation

- [README.md](README.md) - General usage and installation
- [EXAMPLES.md](EXAMPLES.md) - Practical usage examples
- [CHANGELOG.md](CHANGELOG.md) - Version history and changes