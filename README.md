# MergeSourceFile 

[![CircleCI](https://dl.circleci.com/status-badge/img/gh/alegorico/MergeSourceFile/tree/main.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/gh/alegorico/MergeSourceFile/tree/main)
[![codecov](https://codecov.io/gh/alegorico/MergeSourceFile/branch/main/graph/badge.svg)](https://codecov.io/gh/alegorico/MergeSourceFile)

[![PyPI version](https://badge.fury.io/py/MergeSourceFile.svg)](https://badge.fury.io/py/MergeSourceFile)
[![Python Support](https://img.shields.io/pypi/pyversions/MergeSourceFile.svg)](https://pypi.org/project/MergeSourceFile/)
[![GitHub release](https://img.shields.io/github/release/alegorico/MergeSourceFile.svg)](https://github.com/alegorico/MergeSourceFile/releases)
[![Downloads](https://pepy.tech/badge/mergesourcefile)](https://pepy.tech/project/mergesourcefile)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub issues](https://img.shields.io/github/issues/alegorico/MergeSourceFile.svg)](https://github.com/alegorico/MergeSourceFile/issues)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/alegorico/MergeSourceFile/graphs/commit-activity)
[![TOML Config](https://img.shields.io/badge/Config-TOML-blue.svg)](https://toml.io/)
[![Jinja2](https://img.shields.io/badge/Templates-Jinja2-red.svg)](https://jinja.palletsprojects.com/)

A modular, plugin-based Python tool to process SQL*Plus scripts with Jinja2 template support, resolving file inclusions and variable substitutions.

## Description

MergeSourceFile is a powerful SQL script processor with a **plugin-based architecture** that provides flexible, configurable processing pipelines. The tool processes SQL*Plus scripts with support for file inclusions (`@`, `@@`), variable substitutions (`DEFINE`/`UNDEFINE`), and Jinja2 templating with custom filters and processing strategies.

## Features

- **🔌 Plugin Architecture**: Modular, extensible design with independent processing plugins
- **📦 Processing Pipeline**: Configurable execution order for different processing strategies
- **📁 File Inclusion Resolution**: Processes `@` and `@@` directives to include external SQL files
- **🔧 Variable Substitution**: Handles `DEFINE` and `UNDEFINE` commands for variable management
- **🔄 Variable Redefinition**: Supports redefining variables throughout the script
- **� Jinja2 Template Processing**: Full Jinja2 template support with variables, conditionals, loops, and filters
- **🛡️ Custom Jinja2 Filters**: `sql_escape` for SQL injection protection and `strftime` for date formatting
- **⚙️ Flexible Processing Orders**: Customize plugin execution order for different workflows
- **🌳 Tree Display**: Shows the inclusion hierarchy in a tree structure
- **📊 Verbose Mode**: Detailed logging for debugging and understanding the processing flow

## Installation

```bash
pip install MergeSourceFile
```

## What's New in v2.0.0

- 🔌 **Plugin Architecture**: Complete rewrite with modular, extensible plugin system
- 📦 **Processing Pipeline**: Configurable execution order with `ProcessorPipeline`
- 🏗️ **Plugin Registry**: Central registry for plugin management and discovery
- 🔧 **Plugin System**: Abstract base classes (`ProcessorPlugin`) for custom plugins
- 📝 **New Configuration Format**: Hierarchical TOML with `[project]`, `[plugins.*]` sections
- ❌ **Breaking Change**: Legacy `[mergesourcefile]` format no longer supported
- ✅ **Enhanced Testing**: 69 comprehensive tests with 81% code coverage
- 🎯 **Better Separation**: Clear separation between SQLPlus includes, variables, and Jinja2

### Migration from v1.x to v2.0.0

**Old Configuration Format (v1.x - NO LONGER SUPPORTED)**:
```toml
[mergesourcefile]
input = "main.sql"
output = "output.sql"
jinja2 = true
processing_order = "default"
```

**New Configuration Format (v2.0.0 - REQUIRED)**:
```toml
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

## What's New in v1.4.0

- 🚀 **Configuration-Only Interface**: Removed all command-line parameters in favor of configuration files
- 📁 **Standard Configuration File**: The tool now reads from `MKFSource.toml` in the current directory
- 🎯 **Project-Based Workflow**: Each build configuration has its own dedicated configuration file
- 🧹 **Simplified CLI**: No more complex command-line arguments - just run `mergesourcefile`
- ✨ **Cleaner Architecture**: Streamlined codebase focused on configuration-driven processing

## What's New in v1.3.0

- 🚀 **Python 3.11+ Required**: Updated minimum Python version to 3.11+
- � **Native TOML Support**: Uses built-in `tomllib` module (no external dependencies)
- 🔧 **Simplified Dependencies**: Removed `tomli` dependency
- ⚡ **Better Performance**: Improved performance and maintainability with native TOML support

- 🐛 **DEFINE Bug Fixes**: Critical fix for DEFINE statements without quotes (e.g., `DEFINE VAR = value`)
- 🔧 **Enhanced DEFINE Support**: Improved regex to handle decimal values, hyphens, and complex alphanumeric values
- 📊 **Better Error Reporting**: Verbose mode now shows ignored DEFINE statements with line numbers
- 🪟 **Windows Compatibility**: Fixed Unicode encoding issues for full Windows support
- ✅ **Robust Testing**: 17 new tests added, 56/56 tests passing including full CLI integration

## Configuration File (MKFSource.toml)

### How It Works

MergeSourceFile now operates exclusively through configuration files. Simply create a `MKFSource.toml` file in your project directory and run `mergesourcefile`.

### Why Configuration Files?

Configuration files provide several advantages:
- **Project-Based**: Each build configuration has its own file
- **Version Control Friendly**: Store your configuration alongside your source code
- **Maintainable**: Easier to manage complex configurations
- **Reusable**: Share configurations across team members
- **Self-Documenting**: Configuration file serves as documentation

### Quick Start

1. **Create a `MKFSource.toml` file** in your project directory:

```toml
[project]
input = "main.sql"
output = "merged.sql"

[plugins.sqlplus]
enabled = true
```

2. **Run the tool** (it automatically reads from `MKFSource.toml` in the current directory):

```bash
mergesourcefile
```

That's it! No command-line arguments needed. The tool exclusively reads from `MKFSource.toml`.

### Configuration Options

All options are specified in the `MKFSource.toml` file:

```toml
[project]
# Required fields
input = "input.sql"              # Input file to process
output = "output.sql"            # Output file for merged result

# Optional fields (with default values)
verbose = false                  # Enable verbose mode
execution_order = ["sqlplus_includes", "jinja2", "sqlplus_vars"]  # Plugin execution order

[plugins.sqlplus]
# SQL*Plus plugin configuration
enabled = true                   # Enable SQL*Plus processing
skip_var = false                 # Skip DEFINE/UNDEFINE variable substitution

[plugins.jinja2]
# Jinja2 template plugin configuration
enabled = false                  # Enable Jinja2 template processing
variables_file = "vars.json"     # JSON file with Jinja2 variables
```

### Example Configurations

**Basic Processing** (`MKFSource.toml`):
```toml
[project]
input = "main.sql"
output = "merged.sql"

[plugins.sqlplus]
enabled = true
```

**With Jinja2 Templates** (`MKFSource.toml`):
```toml
[project]
input = "template.sql"
output = "generated.sql"
verbose = false
execution_order = ["jinja2", "sqlplus_includes", "sqlplus_vars"]

[plugins.jinja2]
enabled = true
variables_file = "production_vars.json"
```

**Verbose Mode for Debugging** (`MKFSource.toml`):
```toml
[project]
input = "debug.sql"
output = "debug_output.sql"
verbose = true

[plugins.sqlplus]
enabled = true
skip_var = false
```

### Multiple Configurations for Different Environments

You can maintain multiple configuration files for different build scenarios:

```bash
# Development build
cp MKFSource.dev.toml MKFSource.toml
mergesourcefile

# Production build  
cp MKFSource.prod.toml MKFSource.toml
mergesourcefile
```

See the [Configuration Guide](CONFIGURATION.md) for a complete reference with all available options and examples.

## Usage

Simply run `mergesourcefile` in the directory containing your `MKFSource.toml` file:

```bash
mergesourcefile
```

The tool will:
1. Look for `MKFSource.toml` in the current directory
2. Read the configuration
3. Load and configure plugins based on settings
4. Execute the processing pipeline in the specified order
5. Output the merged result

### Workflow

1. **Create your configuration**: Create a `MKFSource.toml` file in your project directory
2. **Configure your build**: Set the input/output files and plugin settings
3. **Run the tool**: Execute `mergesourcefile` (no arguments needed, reads from `MKFSource.toml`)
4. **Get your output**: Find the merged SQL in the output file specified in your configuration

**Important**: The tool exclusively reads from `MKFSource.toml` in the current directory. There are no command-line parameters for specifying configuration files or overriding settings.

### Configuration File Format

The `MKFSource.toml` file uses a hierarchical structure with three main sections:

```toml
[project]
input = "main.sql"              # Required: Input SQL file
output = "merged.sql"           # Required: Output file for merged result
verbose = false                 # Optional: Enable detailed logging
execution_order = ["sqlplus_includes", "jinja2", "sqlplus_vars"]  # Plugin execution order

[plugins.sqlplus]
enabled = true                   # Enable SQLPlus processing (includes + variables)
skip_var = false                 # Skip variable substitution if true

[plugins.jinja2]
enabled = false                  # Enable Jinja2 template processing
variables_file = "vars.json"     # JSON file with Jinja2 variables
```

### Plugin System

MergeSourceFile v2.0.0 introduces a plugin-based architecture with three core plugins:

1. **sqlplus_includes**: Processes `@` and `@@` file inclusion directives
2. **jinja2**: Processes Jinja2 template variables and expressions
3. **sqlplus_vars**: Processes `DEFINE` and `UNDEFINE` variable commands

You can customize the execution order to match your workflow:

```toml
# Default: Includes → Jinja2 → Variables
execution_order = ["sqlplus_includes", "jinja2", "sqlplus_vars"]

# Jinja2 First: Templates → Includes → Variables  
execution_order = ["jinja2", "sqlplus_includes", "sqlplus_vars"]

# Variables First: Variables → Jinja2 → Includes
execution_order = ["sqlplus_vars", "jinja2", "sqlplus_includes"]
```

See the [Configuration Guide](CONFIGURATION.md) for detailed information about all configuration options.

## Features Details

## How It Works

### File Inclusion

- `@filename`: Includes a file relative to the original base path
- `@@filename`: Includes a file relative to the current file's directory

### Variable Substitution

#### DEFINE Syntax (Enhanced in v1.1.1)
- `DEFINE varname = 'quoted value';`: Defines with quoted value (supports spaces)
- `DEFINE varname = unquoted_value;`: Defines with unquoted value (no spaces)
- `DEFINE varname = 3.14;`: Supports decimal values
- `DEFINE varname = ABC-123;`: Supports hyphenated values
- `DEFINE varname = '';`: Supports empty string values

#### Variable Usage
- `&varname`: References a variable for substitution
- `&varname..`: Variable concatenation with period
- `UNDEFINE varname;`: Removes a variable definition

#### Error Handling (v1.1.1)
- Invalid DEFINE syntax is ignored and reported in verbose mode
- Example: `DEFINE var = ;` will be skipped with a warning
- Variables must be defined before use or an error is thrown

### 🆕 Jinja2 Template Processing

#### Basic Template Syntax
- `{{ variable }}`: Variable substitution
- `{% if condition %}...{% endif %}`: Conditional blocks
- `{% for item in list %}...{% endfor %}`: Loop blocks
- `{# comment #}`: Template comments

#### Custom Filters
- `sql_escape`: Escapes single quotes for SQL safety
  ```sql
  SELECT * FROM users WHERE name = '{{ user_name | sql_escape }}';
  ```
- `strftime`: Formats datetime objects
  ```sql
  -- Generated on {{ now() | strftime('%Y-%m-%d %H:%M:%S') }}
  ```

#### Processing Orders
1. **default**: File Inclusions → Jinja2 Templates → SQL Variables
2. **jinja2_first**: Jinja2 Templates → File Inclusions → SQL Variables
3. **includes_last**: SQL Variables → Jinja2 Templates → File Inclusions

#### Dynamic File Inclusion Example
```sql
-- Using jinja2_first order to dynamically determine which files to include
{% if environment == 'production' %}
@prod_config.sql
{% else %}
@dev_config.sql
{% endif %}
```

## Complete Example

### Input Template (`template.sql`)
```sql
{# This is a Jinja2 comment #}
-- Database setup for {{ environment | upper }} environment
-- Generated on {{ now() | strftime('%Y-%m-%d %H:%M:%S') }}

{% if environment == 'production' %}
@production_settings.sql
{% else %}
@development_settings.sql
{% endif %}

DEFINE db_name = '{{ database_name }}';
DEFINE table_prefix = '{{ table_prefix }}';

CREATE TABLE &table_prefix._users (
    id NUMBER PRIMARY KEY,
    name VARCHAR2(100) NOT NULL,
    email VARCHAR2(255) UNIQUE,
    created_date DATE DEFAULT SYSDATE
);

{% for table in additional_tables %}
CREATE TABLE &table_prefix._{{ table.name }} (
    id NUMBER PRIMARY KEY,
    {% for column in table.columns -%}
    {{ column.name }} {{ column.type }}{% if not loop.last %},{% endif %}
    {% endfor %}
);
{% endfor %}

-- Insert sample data with escaped values
INSERT INTO &table_prefix._users (name, email) 
VALUES ('{{ sample_user | sql_escape }}', '{{ sample_email | sql_escape }}');
```

### Configuration (`MKFSource.toml`)
```toml
[project]
input = "template.sql"
output = "output.sql"
execution_order = ["jinja2", "sqlplus_includes", "sqlplus_vars"]

[plugins.jinja2]
enabled = true
variables_file = "vars.json"
```

### Variables File (`vars.json`)
```json
{
  "environment": "production",
  "database_name": "MYAPP_DB",
  "table_prefix": "APP",
  "sample_user": "John O'Brien",
  "sample_email": "john@example.com",
  "additional_tables": [
    {
      "name": "products",
      "columns": [
        {"name": "title", "type": "VARCHAR2(200)"},
        {"name": "price", "type": "NUMBER(10,2)"}
      ]
    }
  ]
}
```

### Run
```bash
mergesourcefile
```

## Migration Guide from v1.x to v2.0.0

**BREAKING CHANGE**: v2.0.0 introduces a new plugin-based architecture with a hierarchical configuration format. The old `[mergesourcefile]` format is no longer supported.

### Step 1: Update Your Configuration File Name

Rename your configuration file to `MKFSource.toml` and place it in the directory where you run `mergesourcefile`:

```bash
# If you have an old config file, rename it
mv myconfig.toml MKFSource.toml
```

**Note**: Since v1.4.0, the tool no longer accepts command-line parameters like `--config`. It exclusively reads from `MKFSource.toml` in the current directory.

### Step 2: Update Your Configuration Structure

**Old Configuration (v1.x)**:
```toml
[mergesourcefile]
input = "main.sql"
output = "output.sql"
jinja2 = true
jinja2_vars = "vars.json"
skip_var = false
processing_order = "default"
```

**New Configuration (v2.0.0)**:
```toml
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

### Step 2: Update Processing Order Mapping

| Old (v1.x) | New (v2.0.0) |
|------------|------------|
| `processing_order = "default"` | `execution_order = ["sqlplus_includes", "jinja2", "sqlplus_vars"]` |
| `processing_order = "jinja2_first"` | `execution_order = ["jinja2", "sqlplus_includes", "sqlplus_vars"]` |
| `processing_order = "includes_last"` | `execution_order = ["sqlplus_vars", "jinja2", "sqlplus_includes"]` |

### Step 3: Test Your Configuration

```bash
mergesourcefile
```

For detailed migration instructions, see [CONFIGURATION.md](CONFIGURATION.md) and [RELEASE_NOTES_v2.0.0.md](RELEASE_NOTES_v2.0.0.md).

## Best Practices

### When to Use Each Processing Order

- **default**: `["sqlplus_includes", "jinja2", "sqlplus_vars"]` - Best for most use cases where Jinja2 templates don't need to generate file inclusion directives
- **jinja2_first**: `["jinja2", "sqlplus_includes", "sqlplus_vars"]` - Use when Jinja2 templates need to conditionally determine which files to include
- **includes_last**: `["sqlplus_vars", "jinja2", "sqlplus_includes"]` - Use when you need SQL variables to be processed before Jinja2 templates and file inclusions

### Security Considerations

Always use the `sql_escape` filter when inserting user-provided data:
```sql
-- ❌ Vulnerable to SQL injection
SELECT * FROM users WHERE name = '{{ user_input }}';

-- ✅ Safe with sql_escape filter
SELECT * FROM users WHERE name = '{{ user_input | sql_escape }}';
```

### Performance Tips

- Enable only the plugins you need in `[plugins]` section
- Use `skip_var = true` in `[plugins.sqlplus]` if you don't need SQL variable processing
- For large projects, consider splitting templates into smaller, focused files
- Use Jinja2 comments `{# comment #}` instead of SQL comments for template-specific notes

## Platform Compatibility

### Operating Systems
- ✅ **Linux**: Full support with all features
- ✅ **macOS**: Full support with all features  
- ✅ **Windows**: Full support with enhanced compatibility
  - Fixed Unicode encoding issues for CLI operations
  - All 69 tests pass successfully on Windows systems
  - Proper error codes and file path handling

### Python Versions
- Python 3.11+ (Required for native TOML support)
- Tested with Python 3.11, 3.12, 3.13, 3.14

### Character Encoding
- Primary support: UTF-8 (recommended)
- Windows compatibility: ASCII-safe output for CLI operations
- All text files should use UTF-8 encoding for best results

## Troubleshooting

### Common Issues

1. **Configuration errors**: Ensure your `MKFSource.toml` follows the v2.0.0 format with `[project]` and `[plugins.*]` sections
2. **DEFINE syntax errors**: Use verbose mode (`verbose = true` in config) to see ignored invalid DEFINE statements
3. **Jinja2 syntax errors**: Ensure proper template syntax with matching braces and tags
4. **Variable not found**: Check that all variables are provided via `variables_file` in `[plugins.jinja2]`
5. **File inclusion issues**: Verify file paths and choose appropriate processing order

### Debug Mode

Enable verbose mode in your configuration to see detailed processing information:
```toml
[project]
input = "template.sql"
output = "output.sql"
verbose = true
```

## License

This project is licensed under the MIT License.  
You are free to use, copy, modify, and distribute this software, provided that the copyright notice and this permission are included.  
The software is provided "as is", without warranty of any kind.

## Author

Alejandro G.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
