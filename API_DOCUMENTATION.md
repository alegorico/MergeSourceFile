# MergeSourceFile API Documentation

This document describes the internal API of MergeSourceFile v1.1.1 for developers who want to extend or integrate the functionality.

## What's New in v1.1.1

### Enhanced DEFINE Processing
- **Improved regex pattern**: Now supports decimal values, hyphens, and complex alphanumeric values
- **Better error handling**: Invalid DEFINE statements are ignored with verbose reporting
- **Enhanced compatibility**: Fixed critical bug with unquoted DEFINE values

### Platform Compatibility Improvements
- **Windows support**: Fixed Unicode encoding issues for full Windows compatibility
- **Error handling**: Enhanced CLI error codes and file path resolution
- **Robust testing**: All 56 tests now pass on all platforms

## Core Classes and Functions

### Main Processing Functions

#### `process_file_with_jinja2_replacements(content, args, input_path, processed_files)`
Main processing function that handles the complete workflow.

**Parameters:**
- `content` (str): File content to process
- `args` (Namespace): Parsed command-line arguments
- `input_path` (str): Path to input file
- `processed_files` (set): Set of already processed files (prevents circular includes)

**Returns:** 
- `str`: Processed content

**Processing Order:**
Delegates to specific processing order functions based on `args.processing_order`.

#### Processing Order Functions

##### `_process_default_order(content, args, input_path, processed_files)`
**Order:** File Inclusions → Jinja2 Templates → SQL Variables

Best for most use cases where templates don't generate file inclusion directives.

##### `_process_jinja2_first(content, args, input_path, processed_files)`
**Order:** Jinja2 Templates → File Inclusions → SQL Variables

Enables dynamic file inclusion based on Jinja2 variables.

##### `_process_includes_last(content, args, input_path, processed_files)`
**Order:** SQL Variables → Jinja2 Templates → File Inclusions

Useful when SQL variables need to be available in Jinja2 templates.

### Jinja2 Processing

#### `process_jinja2_template(content, jinja2_vars_dict, input_path)`
Processes Jinja2 templates with custom filters and error handling.

**Parameters:**
- `content` (str): Template content
- `jinja2_vars_dict` (dict): Variables for template rendering
- `input_path` (str): Path for error reporting

**Returns:**
- `str`: Rendered template content

**Features:**
- Custom delimiters
- Strict undefined variables
- Custom filters: `sql_escape`, `strftime`
- Comprehensive error handling

#### Custom Jinja2 Filters

##### `sql_escape_filter(value)`
Escapes single quotes for SQL safety.

**Example:**
```python
# Template: SELECT * FROM users WHERE name = '{{ user_name | sql_escape }}';
# Input: user_name = "John O'Brien"
# Output: SELECT * FROM users WHERE name = 'John O''Brien';
```

##### `strftime_filter(value, format_string)`
Formats datetime objects and strings.

**Example:**
```python
# Template: -- Generated on {{ now() | strftime('%Y-%m-%d %H:%M:%S') }}
# Output: -- Generated on 2024-10-17 14:30:45
```

### File Processing (Existing Functionality)

#### `process_file_replacements(file_content, input_path, processed_files)`
Processes file inclusions (`@` and `@@` directives).

#### `process_file_sequentially(content, verbose=False)` 🆕 Enhanced in v1.1.1
Processes SQL*Plus variable definitions and substitutions with enhanced DEFINE support.

**Parameters:**
- `content` (str): Content to process
- `verbose` (bool): Enable detailed logging

**Returns:**
- `str`: Content with variables substituted

**Enhanced Features (v1.1.1):**
- **Improved DEFINE regex**: Supports decimal values, hyphens, complex alphanumeric values
- **Better error handling**: Invalid DEFINE statements ignored with verbose reporting
- **Enhanced compatibility**: Fixed critical bug with unquoted DEFINE values
- **Examples of supported syntax**:
  ```sql
  DEFINE var = unquoted_value    -- ✅ Fixed in v1.1.1
  DEFINE price = 3.14           -- ✅ New: decimal support
  DEFINE code = ABC-123         -- ✅ New: hyphenated values
  DEFINE id = DB2_V2_FINAL      -- ✅ New: complex alphanumeric
  DEFINE empty = '';            -- ✅ New: empty string support
  ```

### Utility Functions

#### `load_jinja2_vars(jinja2_vars_str)`
Loads and validates Jinja2 variables from JSON string.

**Parameters:**
- `jinja2_vars_str` (str): JSON string with variables

**Returns:**
- `dict`: Parsed variables dictionary

**Raises:**
- `ValueError`: On invalid JSON or parsing errors

#### `show_file_tree(file_tree, level)`
Displays the file inclusion hierarchy.

## Integration Examples

### Basic Integration

```python
from MergeSourceFile.main import process_file_with_jinja2_replacements
import argparse

# Create arguments object
args = argparse.Namespace(
    jinja2=True,
    jinja2_vars='{"environment": "production"}',
    processing_order="default",
    skip_var=False,
    verbose=False
)

# Process content
content = "SELECT * FROM {{ table_name }};"
result = process_file_with_jinja2_replacements(
    content=content,
    args=args,
    input_path="template.sql",
    processed_files=set()
)
```

### Custom Processing Pipeline

```python
from MergeSourceFile.main import (
    process_jinja2_template,
    process_file_replacements,
    process_variable_replacements,
    load_jinja2_vars
)

def custom_processor(content, jinja2_vars_json, input_path):
    """Custom processing with additional steps."""
    
    # Load variables
    jinja2_vars = load_jinja2_vars(jinja2_vars_json)
    
    # Custom pre-processing
    content = content.replace("{{OLD_SYNTAX}}", "{{ new_syntax }}")
    
    # Jinja2 processing
    content = process_jinja2_template(content, jinja2_vars, input_path)
    
    # File inclusions
    content = process_file_replacements(content, input_path, set())
    
    # SQL variables
    content = process_variable_replacements(content, input_path)
    
    # Custom post-processing
    content = content.upper()  # Example transformation
    
    return content
```

### Custom Jinja2 Filters

```python
from jinja2 import Environment, BaseLoader
from MergeSourceFile.main import sql_escape_filter, strftime_filter

def create_custom_environment():
    """Create Jinja2 environment with custom filters."""
    
    env = Environment(
        loader=BaseLoader(),
        variable_start_string='{{',
        variable_end_string='}}',
        block_start_string='{%',
        block_end_string='%}',
        comment_start_string='{#',
        comment_end_string='#}',
        undefined=StrictUndefined
    )
    
    # Add built-in filters
    env.filters['sql_escape'] = sql_escape_filter
    env.filters['strftime'] = strftime_filter
    
    # Add custom filters
    env.filters['upper_snake'] = lambda x: x.replace(' ', '_').upper()
    env.filters['quote_identifier'] = lambda x: f'"{x}"'
    
    return env
```

## SQL Variables (DEFINE) Syntax

### Supported DEFINE Formats

MergeSourceFile supports SQL*Plus-compatible DEFINE syntax with enhanced flexibility:

#### 1. **Quoted Values** (Traditional)
```sql
DEFINE variable = 'value';
DEFINE schema = 'production';
DEFINE table_name = 'audit_log';
```

#### 2. **Unquoted Values** (SQL*Plus Standard)
```sql
DEFINE counter = 100;
DEFINE database = production;
DEFINE schema_log = DBO;
```
**Note**: Unquoted values cannot contain spaces. Use quotes for values with spaces.

#### 3. **Decimal Values** (Enhanced Support)
```sql
DEFINE price = 3.14;
DEFINE ratio = 0.75;
DEFINE version = 2.5;
```

#### 4. **Hyphenated Values** (Enhanced Support)
```sql
DEFINE code = ABC-123;
DEFINE version = v1-2-3;
DEFINE project = my-project;
```

#### 5. **Mixed Alphanumeric** (Enhanced Support)
```sql
DEFINE table_audit = log_audit_2024;
DEFINE schema_name = DB_PROD;
DEFINE config = app_config_v2;
```

### Syntax Rules

1. **Case-insensitive**: `DEFINE`, `define`, `Define` all work
2. **Optional semicolon**: Both `DEFINE var = value;` and `DEFINE var = value` work
3. **Flexible spacing**: Spaces around `=` are optional
4. **Value types**: Supports quoted strings, unquoted identifiers, numbers, decimals, and special characters
5. **SQL*Plus compatibility**: Adheres to Oracle SQL*Plus DEFINE standards
6. **Spaces in values**: Use quotes for values containing spaces: `DEFINE msg = 'Hello world'`

### Design Decision

**Our implementation correctly follows SQL*Plus standards by supporting both quoted and unquoted values.**

In Oracle SQL*Plus, both of these are valid and equivalent:
- `DEFINE var1 = 123` (unquoted - standard for simple values)
- `DEFINE var1 = '123'` (quoted - used for complex values with spaces)

This design decision was validated against Oracle documentation and real-world SQL*Plus usage patterns.

### Examples in Practice

```sql
-- Database configuration
DEFINE SCHEMA_LOG = DBO;
DEFINE TABLE_LOG = AUDIT_LOG;
DEFINE VERSION = 2.5;
DEFINE MESSAGE = 'Database deployment completed';  -- Spaces require quotes

-- Usage in SQL
CREATE TABLE &SCHEMA_LOG..&TABLE_LOG (
    id NUMBER,
    version NUMBER DEFAULT &VERSION,
    message VARCHAR2(100) DEFAULT '&MESSAGE'
);
```

**Result:**
```sql
CREATE TABLE DBO.AUDIT_LOG (
    id NUMBER,
    version NUMBER DEFAULT 2.5,
    message VARCHAR2(100) DEFAULT 'Database deployment completed'
);
```

### Invalid Examples (Not Supported)

```sql
-- ❌ INVALID: Spaces without quotes
DEFINE message = Hello world;
DEFINE path = C:\Program Files\App;

-- ✅ CORRECT: Use quotes for spaces
DEFINE message = 'Hello world';
DEFINE path = 'C:\Program Files\App';
```

### Error Handling for DEFINE Statements

#### Invalid DEFINE Syntax Detection

The system detects and reports invalid DEFINE statements:

```sql
-- ❌ These will be ignored and reported in verbose mode:
DEFINE variable_name = ;           -- Missing value
DEFINE = value;                    -- Missing variable name  
DEFINE var@ = value;               -- Invalid character in name
DEFINE var# = value;               -- Invalid character in name

-- ✅ These are valid:
DEFINE var = '';                   -- Empty string (valid)
DEFINE var = value;                -- Simple value
DEFINE var = 'complex value';      -- Quoted value
```

#### Error Messages

**Verbose Mode** (`--verbose`):
- `[VERBOSE] Ignorando DEFINE con sintaxis inválida en línea 4: 'DEFINE var = ;'`
- `[VERBOSE] Definiendo variable: var_name = value`

**Runtime Errors**:
- `Error: La variable 'var_name' se usa antes de ser definida (línea 15).`

#### Best Practices for Troubleshooting

1. **Use verbose mode** to see which DEFINE statements are being ignored
2. **Check syntax carefully** - ensure variable names use only alphanumeric characters and underscores
3. **Use quotes for complex values** containing spaces or special characters
4. **Verify variable names** in usage match exactly with definitions (case-insensitive)

## Error Handling

### Exception Types

The module raises specific exceptions for different error conditions:

- `FileNotFoundError`: When included files are not found
- `ValueError`: For invalid JSON in `--jinja2-vars`
- `TemplateError`: For Jinja2 template syntax errors
- `UndefinedError`: For undefined Jinja2 variables

### Error Handling Example

```python
try:
    result = process_file_with_jinja2_replacements(
        content, args, input_path, processed_files
    )
except ValueError as e:
    print(f"Configuration error: {e}")
except FileNotFoundError as e:
    print(f"File not found: {e}")
except Exception as e:
    print(f"Processing error: {e}")
```

## Extension Points

### Adding New Processing Orders

```python
def _process_custom_order(content, args, input_path, processed_files):
    """Custom processing order implementation."""
    
    # Example: SQL first, then custom processing, then Jinja2
    if not args.skip_var:
        content = process_variable_replacements(content, input_path)
    
    # Custom processing step
    content = custom_transformation(content)
    
    if args.jinja2 and args.jinja2_vars:
        jinja2_vars_dict = load_jinja2_vars(args.jinja2_vars)
        content = process_jinja2_template(content, jinja2_vars_dict, input_path)
    
    content = process_file_replacements(content, input_path, processed_files)
    
    return content

# Register in main processing function
PROCESSING_ORDERS = {
    'default': _process_default_order,
    'jinja2_first': _process_jinja2_first,
    'includes_last': _process_includes_last,
    'custom': _process_custom_order,  # New order
}
```

### Adding New Command-Line Arguments

```python
def setup_argument_parser():
    """Extended argument parser with custom options."""
    
    parser = argparse.ArgumentParser(
        description='MergeSourceFile with custom extensions'
    )
    
    # Existing arguments...
    
    # Custom arguments
    parser.add_argument('--custom-filter', type=str,
                        help='Custom filter configuration')
    parser.add_argument('--output-format', choices=['sql', 'json', 'xml'],
                        default='sql', help='Output format')
    
    return parser
```

## Testing and Development

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=MergeSourceFile --cov-report=html

# Run specific test categories
python -m pytest tests/test_jinja2.py -v
python -m pytest tests/test_processing_orders.py -v
```

### Development Setup

```bash
# Clone and setup development environment
git clone <repository>
cd MergeSourceFile
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate.bat  # Windows

# Install in development mode
pip install -e .
pip install pytest pytest-cov
```

This API documentation provides the foundation for extending MergeSourceFile. The modular design allows for easy customization while maintaining backward compatibility.