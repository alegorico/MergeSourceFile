# MergeSourceFile 

[![CircleCI](https://dl.circleci.com/status-badge/img/gh/alegorico/MergeSourceFile/tree/main.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/gh/alegorico/MergeSourceFile/tree/main)
[![codecov](https://codecov.io/gh/alegorico/MergeSourceFile/branch/main/graph/badge.svg)](https://codecov.io/gh/alegorico/MergeSourceFile)

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

## What's New in v1.2.0

- ✨ **TOML Configuration Support**: New `--config` / `-c` parameter to read settings from a TOML file
- 🔧 **Configuration File**: Centralized configuration in `config.toml` instead of command-line parameters
- ⚠️ **Deprecation Warning**: Traditional command-line parameters now show a deprecation warning
- 🔒 **Mutual Exclusivity**: Config file and command-line parameters cannot be used together
- 📋 **Backward Compatibility**: All existing command-line parameters continue to work
- 🧪 **Comprehensive Testing**: 11 new tests added (67 total tests passing)

## What's New in v1.1.1

- 🐛 **DEFINE Bug Fixes**: Critical fix for DEFINE statements without quotes (e.g., `DEFINE VAR = value`)
- 🔧 **Enhanced DEFINE Support**: Improved regex to handle decimal values, hyphens, and complex alphanumeric values
- 📊 **Better Error Reporting**: Verbose mode now shows ignored DEFINE statements with line numbers
- 🪟 **Windows Compatibility**: Fixed Unicode encoding issues for full Windows support
- ✅ **Robust Testing**: 17 new tests added, 56/56 tests passing including full CLI integration

## 🚨 Important: Command-Line Parameters Deprecation Notice

**Starting from the next major version, command-line parameters will be deprecated in favor of TOML configuration files.**

We strongly recommend migrating to the new TOML configuration format:
- ✅ **Use**: `mergesourcefile --config config.toml` (Recommended)
- ⚠️ **Deprecated**: `mergesourcefile --input file.sql --output out.sql` (Will be removed in future versions)

See the [TOML Configuration](#toml-configuration-recommended) section below for migration instructions.

## What's New in v1.1.0

- ✨ **Jinja2 Template Support**: Full integration with Jinja2 templating engine
- 🔧 **Custom Filters**: Added `sql_escape` and `strftime` filters for enhanced functionality
- 🔀 **Processing Orders**: Three different processing strategies for complex scenarios
- 🎯 **Dynamic Inclusion**: Use Jinja2 variables to conditionally include files
- 📋 **Enhanced CLI**: New command-line options for Jinja2 functionality
- 🧪 **Comprehensive Testing**: 20+ new tests ensuring reliability

## TOML Configuration (Recommended)

### Why Use TOML Configuration?

TOML configuration files provide several advantages:
- **Version Control Friendly**: Store your configuration in the repository
- **Maintainable**: Easier to manage complex configurations
- **Reusable**: Use the same configuration across different environments
- **Future-Proof**: Command-line parameters will be deprecated in future versions

### Quick Start with TOML

1. **Create a configuration file** (e.g., `config.toml`):

```toml
[mergesourcefile]
input = "main.sql"
output = "merged.sql"
skip_var = false
verbose = false
jinja2 = false
processing_order = "default"
```

2. **Run with the configuration file**:

```bash
mergesourcefile --config config.toml
# or using short form:
mergesourcefile -c config.toml
```

### TOML Configuration Options

All command-line options are available in TOML format:

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

**Basic Processing**:
```toml
[mergesourcefile]
input = "main.sql"
output = "merged.sql"
```

**With Jinja2 Templates**:
```toml
[mergesourcefile]
input = "template.sql"
output = "generated.sql"
jinja2 = true
jinja2_vars = "production_vars.json"
processing_order = "jinja2_first"
```

**Verbose Mode for Debugging**:
```toml
[mergesourcefile]
input = "debug.sql"
output = "debug_output.sql"
verbose = true
skip_var = false
```

### Migration from Command-Line Parameters

If you're currently using command-line parameters, migration is simple:

**Before (Deprecated)**:
```bash
mergesourcefile --input main.sql --output merged.sql --verbose --jinja2 --jinja2-vars vars.json
```

**After (Recommended)**:

Create `config.toml`:
```toml
[mergesourcefile]
input = "main.sql"
output = "merged.sql"
verbose = true
jinja2 = true
jinja2_vars = "vars.json"
```

Run:
```bash
mergesourcefile --config config.toml
```

### Configuration File Location

Place your TOML configuration file:
- In the root of your project directory
- Or anywhere else and reference it with the full path: `mergesourcefile --config /path/to/config.toml`

See the [Configuration Guide](CONFIGURATION.md) for a complete reference with all available options and examples.

## Usage

### Recommended: TOML Configuration File

```bash
mergesourcefile --config config.toml
```

See the [TOML Configuration](#toml-configuration-recommended) section for detailed information.

### Legacy: Command Line (Deprecated)

⚠️ **Warning**: Command-line parameters will be deprecated in future versions. Please migrate to TOML configuration.

```bash
mergesourcefile --input input.sql --output output.sql
```

### Options (Legacy Command-Line)

- `--config, -c`: **RECOMMENDED** - Load configuration from TOML file
- `--input, -i`: Input SQL*Plus file to process (deprecated, use TOML config)
- `--output, -o`: Output file where the result will be written (deprecated, use TOML config)
- `--skip-var, -sv`: Skip variable substitution, only resolve file inclusions (deprecated, use TOML config)
- `--verbose, -v`: Enable verbose mode for detailed processing information (deprecated, use TOML config)
- `--jinja2`: Enable Jinja2 template processing (deprecated, use TOML config)
- `--jinja2-vars`: JSON string with variables for Jinja2 template processing (deprecated, use TOML config)
- `--processing-order`: Choose processing order: `default`, `jinja2_first`, or `includes_last` (deprecated, use TOML config)

### TOML Configuration File Format

Create a `config.toml` file in your project directory:

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

### Examples

1. **Recommended: Use TOML configuration**:
   ```bash
   mergesourcefile --config config.toml
   ```

2. **Legacy: Process a SQL file with full processing** (deprecated):
   ```bash
   mergesourcefile -i main.sql -o merged.sql
   ```

3. **Legacy: Process only file inclusions, skip variable substitution** (deprecated):
   ```bash
   mergesourcefile -i main.sql -o merged.sql --skip-var
   ```

4. **Legacy: Process with verbose output** (deprecated):
   ```bash
   mergesourcefile -i main.sql -o merged.sql --verbose
   ```

5. **Legacy: Process with Jinja2 template support** (deprecated):
   ```bash
   mergesourcefile -i template.sql -o merged.sql --jinja2
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
```bash
mergesourcefile -i main.sql -o output.sql --verbose --skip-var
```

Create a `config.toml` file:
```toml
[mergesourcefile]
input = "main.sql"
output = "output.sql"
verbose = true
skip_var = true
```

Then run:
```bash
mergesourcefile --config config.toml
```

#### Step 2: Migrating Jinja2 Configurations

For projects using Jinja2, instead of:
```bash
mergesourcefile -i template.sql -o output.sql --jinja2 --jinja2-vars vars.json --processing-order jinja2_first
```

Use a TOML config:
```toml
[mergesourcefile]
input = "template.sql"
output = "output.sql"
jinja2 = true
jinja2_vars = "vars.json"
processing_order = "jinja2_first"
```

#### Benefits of TOML Configuration

1. **Version Control Friendly**: Configuration files can be committed to your repository
2. **Project-Specific Settings**: Each project can have its own `config.toml`
3. **Cleaner Scripts**: Simplifies build scripts and CI/CD pipelines
4. **Self-Documenting**: Configuration files are easier to read and understand
5. **No Shell Escaping**: Avoid issues with special characters in command-line parameters

#### Deprecation Timeline

- **v1.2.0**: TOML configuration introduced, deprecation warning added for command-line parameters
- **v1.3.0** (planned): Increased warning severity
- **v2.0.0** (future): Command-line parameters may be removed entirely

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

- Use `--skip-var` if you don't need SQL variable processing
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
- Python 3.8+
- Tested with Python 3.9, 3.10, 3.11, 3.12, 3.14

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
