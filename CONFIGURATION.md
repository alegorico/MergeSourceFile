# MergeSourceFile Configuration Guide

## TOML Configuration File Reference

MergeSourceFile supports configuration via TOML files using the `--config/-c` parameter. This approach simplifies complex workflows and provides better configuration management than command-line arguments.

## Quick Start

1. Create your configuration file based on the examples in this guide:
   ```bash
   # Create a new configuration file
   touch config.toml
   ```

2. Edit the configuration file according to your needs

3. Run with configuration:
   ```bash
   mergesourcefile --config config.toml
   ```

## Configuration File Structure

### Complete Example

```toml
# Example configuration file for MergeSourceFile
# Create your config.toml file and adjust values according to your needs

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
processing_order = "jinja2_first"   # Options: "default", "jinja2_first", "sqlplus_first"
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
- **`"sqlplus_first"`**: SQL variables → Jinja2 → File inclusions

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

## Command Line Usage

```bash
# Use configuration file
mergesourcefile --config config.toml

# Configuration overrides all command-line parameters
mergesourcefile --config config.toml --verbose  # --verbose is ignored
```

## Migration from Command Line

### Before (Command Line)
```bash
mergesourcefile \
  --input main.sql \
  --output merged.sql \
  --jinja2 \
  --jinja2-vars variables.json \
  --verbose \
  --processing-order jinja2_first
```

### After (TOML Configuration)
```toml
[mergesourcefile]
input = "main.sql"
output = "merged.sql"
jinja2 = true
jinja2_vars = "variables.json"
verbose = true
processing_order = "jinja2_first"
```

```bash
mergesourcefile --config config.toml
```

## Best Practices

1. **Version Control**: Include your `.toml` configuration files in version control
2. **Environment-Specific**: Create different config files for different environments (`config.dev.toml`, `config.prod.toml`)
3. **Documentation**: Add comments in your configuration files to explain complex setups
4. **Validation**: Test your configuration with `--verbose` enabled to verify processing order

## Troubleshooting

### Missing Required Parameters
```
ValueError: El archivo de configuracion debe especificar 'input'
```
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