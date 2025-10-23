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

A Python tool to process SQL*Plus scripts with Jinja2 template support, resolving file inclusions and variable substitutions.

## Description

This is a Python project that includes a script capable of processing SQL*Plus scripts with Jinja2 template support. The program resolves file inclusions referenced through `@` and `@@`, performs variable substitutions defined with `DEFINE`, supports variable removal with `UNDEFINE`, allows variable redefinition throughout the script, and **now includes Jinja2 template processing** with custom filters and multiple processing strategies.

## Features

- **File Inclusion Resolution**: Processes `@` and `@@` directives to include external SQL files
- **Variable Substitution**: Handles `DEFINE` and `UNDEFINE` commands for variable management
- **Variable Redefinition**: Supports redefining variables throughout the script
- **🆕 Jinja2 Template Processing**: Full Jinja2 template support with variables, conditionals, loops, and filters
- **🆕 Custom Jinja2 Filters**: `sql_escape` for SQL injection protection and `strftime` for date formatting
- **🆕 Multiple Processing Orders**: Choose between `default`, `jinja2_first`, or `includes_last` processing strategies
- **🆕 Dynamic File Inclusion**: Use Jinja2 variables to determine which files to include
- **Tree Display**: Shows the inclusion hierarchy in a tree structure
- **Verbose Mode**: Detailed logging for debugging and understanding the processing flow

## Installation

```bash
pip install MergeSourceFile
```

## What's New in v1.4.0

- 🚀 **Configuration-Only Interface**: Removed all command-line parameters in favor of configuration files
- 📁 **Standard Configuration File**: The tool now reads from `MKFSource.toml` in the current directory
- 🎯 **Project-Based Workflow**: Each build configuration has its own dedicated configuration file
- 🧹 **Simplified CLI**: No more complex command-line arguments - just run `mergesourcefile`
- ✨ **Cleaner Architecture**: Streamlined codebase focused on configuration-driven processing

## What's New in v1.3.0

- 🚀 **Python 3.11+ Required**: Updated minimum Python version to 3.11+
- 📦 **Native TOML Support**: Uses built-in `tomllib` module (no external dependencies)
- 🔧 **Simplified Dependencies**: Removed `tomli` dependency
- ⚡ **Better Performance**: Improved performance and maintainability with native TOML support

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
[mergesourcefile]
input = "main.sql"
output = "merged.sql"
skip_var = false
verbose = false
jinja2 = false
processing_order = "default"
```

2. **Run the tool** (it automatically reads from `MKFSource.toml`):

```bash
mergesourcefile
```

That's it! No command-line arguments needed.

### Configuration Options

All options are specified in the `MKFSource.toml` file:

```toml
[mergesourcefile]
# Required fields
input = "input.sql"              # Input file to process
output = "output.sql"            # Output file for results

# Optional fields (with default values)
skip_var = false                 # Skip variable substitution
verbose = false                  # Enable verbose mode
jinja2 = false                   # Enable Jinja2 processing
jinja2_vars = "vars.json"        # JSON file with Jinja2 variables
processing_order = "default"     # Processing order: default, jinja2_first, includes_last
```

### Example Configurations

**Basic Processing** (`MKFSource.toml`):
```toml
[mergesourcefile]
input = "main.sql"
output = "merged.sql"
```

**With Jinja2 Templates** (`MKFSource.toml`):
```toml
[mergesourcefile]
input = "template.sql"
output = "generated.sql"
jinja2 = true
jinja2_vars = "production_vars.json"
processing_order = "jinja2_first"
```

**Verbose Mode for Debugging** (`MKFSource.toml`):
```toml
[mergesourcefile]
input = "debug.sql"
output = "debug_output.sql"
verbose = true
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
3. Process your SQL files according to the settings
4. Output the merged result

### Workflow

1. **Create your configuration**: Create a `MKFSource.toml` file in your project directory
2. **Configure your build**: Set the input/output files and processing options
3. **Run the tool**: Execute `mergesourcefile` (no arguments needed)
4. **Get your output**: Find the merged SQL in the output file specified in your configuration

### Configuration File Format

The `MKFSource.toml` file must contain a `[mergesourcefile]` section:

```toml
[mergesourcefile]
input = "main.sql"
output = "merged.sql"

# Optional parameters
skip_var = false        # Set to true to skip variable substitution
verbose = false         # Set to true for detailed processing information
jinja2 = false          # Set to true to enable Jinja2 template processing
jinja2_vars = ""        # Path to JSON file with Jinja2 variables
processing_order = "default"  # Options: default, jinja2_first, includes_last
```

Example with Jinja2 support:

```toml
[mergesourcefile]
input = "template.sql"
output = "output.sql"
jinja2 = true
jinja2_vars = "vars.json"
processing_order = "jinja2_first"
verbose = true
```

### Usage Examples

1. **Basic usage** (with MKFSource.toml in current directory):
   ```bash
   mergesourcefile
   ```

2. **With verbose output** (set in MKFSource.toml):
   ```toml
   [mergesourcefile]
   input = "main.sql"
   output = "merged.sql"
   verbose = true
   ```

3. **With Jinja2 templates**:
   ```toml
   [mergesourcefile]
   input = "template.sql"
   output = "merged.sql"
   jinja2 = true
   jinja2_vars = "vars.json"
   ```

6. **Legacy: Process with Jinja2 variables** (deprecated):
   ```bash
   mergesourcefile -i template.sql -o merged.sql --jinja2 --jinja2-vars vars.json
   ```

7. **Legacy: Process with Jinja2-first processing order** (deprecated):
   ```bash
   mergesourcefile -i template.sql -o merged.sql --jinja2 --processing-order jinja2_first
   ```

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

### Command
```bash
mergesourcefile -i template.sql -o output.sql --jinja2 --processing-order jinja2_first --jinja2-vars '{
  "environment": "production",
  "database_name": "MYAPP_DB",
  "table_prefix": "APP",
  "sample_user": "John O'\''Brien",
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
}'
```

## Migration from v1.0.x

If you're upgrading from a previous version, your existing scripts will continue to work without any changes. The new Jinja2 functionality is **completely optional** and requires explicit activation with the `--jinja2` flag.

### Backward Compatibility
- All existing command-line options work exactly as before
- File inclusion (`@`, `@@`) behavior is unchanged
- Variable substitution (`DEFINE`, `UNDEFINE`) works as expected
- No breaking changes to existing functionality

### Gradual Adoption
You can gradually adopt Jinja2 features:
1. Start with simple variable substitution: `{{ variable }}`
2. Add conditional logic: `{% if condition %}`
3. Use loops for repetitive structures: `{% for item in list %}`
4. Apply custom filters: `{{ value | sql_escape }}`
5. Experiment with processing orders for complex scenarios

## Migration from v1.1.x to v1.2.0

### Migrating to TOML Configuration

The new TOML configuration file approach offers a cleaner, more maintainable way to manage your MergeSourceFile settings. While command-line parameters are still supported, they will be deprecated in future versions.

#### Step 1: Create a TOML Configuration File

Instead of:
## Migration Guide from v1.3.0 to v1.4.0

**BREAKING CHANGE**: v1.4.0 removes all command-line parameters. Follow these steps to migrate:

### Step 1: Rename Your Configuration File

```bash
# Old way (v1.3.0)
mergesourcefile --config myconfig.toml

# New way (v1.4.0)
mv myconfig.toml MKFSource.toml
mergesourcefile
```

### Step 2: Place Configuration in Project Directory

Ensure your `MKFSource.toml` is in the directory where you run `mergesourcefile`:

```toml
[mergesourcefile]
input = "main.sql"
output = "output.sql"
verbose = true
skip_var = false
```

### Step 3: Update Build Scripts

**Before (v1.3.0)**:
```bash
#!/bin/bash
mergesourcefile --config config.prod.toml
```

**After (v1.4.0)**:
```bash
#!/bin/bash
cp MKFSource.prod.toml MKFSource.toml
mergesourcefile
```

### Benefits of Configuration-Only Interface

1. **Simplified CLI**: No complex command-line arguments
2. **Project-Based**: Each build configuration has its own file
3. **Version Control Friendly**: Configuration files commit alongside source code
4. **Self-Documenting**: Configuration file serves as documentation
5. **Maintainable**: Easier to manage complex configurations
6. **Team-Friendly**: Share configurations across team members

## Best Practices

### When to Use Each Processing Order

- **default**: Best for most use cases where Jinja2 templates don't need to generate file inclusion directives
- **jinja2_first**: Use when Jinja2 templates need to conditionally determine which files to include
- **includes_last**: Use when you need SQL variables to be processed before Jinja2 templates and file inclusions

### Security Considerations

Always use the `sql_escape` filter when inserting user-provided data:
```sql
-- ❌ Vulnerable to SQL injection
SELECT * FROM users WHERE name = '{{ user_input }}';

-- ✅ Safe with sql_escape filter
SELECT * FROM users WHERE name = '{{ user_input | sql_escape }}';
```

### Performance Tips

- Use `skip_var = true` in your MKFSource.toml if you don't need SQL variable processing
- For large projects, consider splitting templates into smaller, focused files
- Use Jinja2 comments `{# comment #}` instead of SQL comments for template-specific notes

## Platform Compatibility

### Operating Systems
- ✅ **Linux**: Full support with all features
- ✅ **macOS**: Full support with all features  
- ✅ **Windows**: Full support with enhanced compatibility (v1.1.1)
  - Fixed Unicode encoding issues for CLI operations
  - All 56 tests pass successfully on Windows systems
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

1. **DEFINE syntax errors** (Fixed in v1.1.1):
   - ✅ `DEFINE VAR = value` now works correctly (was broken in v1.1.0)
   - ✅ Both quoted and unquoted DEFINE values supported
   - Use verbose mode (`--verbose`) to see ignored invalid DEFINE statements

2. **Jinja2 syntax errors**: Ensure proper template syntax with matching braces and tags
3. **Variable not found**: Check that all variables are provided via `--jinja2-vars`
4. **File inclusion issues**: Verify file paths and choose appropriate processing order
5. **Encoding problems** (Fixed in v1.1.1): 
   - ✅ Windows encoding issues resolved
   - Ensure all files use consistent encoding (UTF-8 recommended)
   - CLI now works properly on all Windows systems

### Windows-Specific Issues (Resolved in v1.1.1)
- ✅ **Unicode character display**: Fixed issues with special characters in CLI output
- ✅ **File path resolution**: Enhanced path handling for nested file inclusions
- ✅ **Exit codes**: CLI now returns proper error codes (1 for errors, 0 for success)

### Debug Mode

Use `--verbose` flag to see detailed processing information:
```bash
mergesourcefile -i template.sql -o output.sql --jinja2 --verbose
```

## License

This project is licensed under the MIT License.  
You are free to use, copy, modify, and distribute this software, provided that the copyright notice and this permission are included.  
The software is provided "as is", without warranty of any kind.

## Author

Alejandro G.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
