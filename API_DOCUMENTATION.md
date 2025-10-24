# MergeSourceFile API Documentation# MergeSourceFile API Documentation



[![PyPI version](https://badge.fury.io/py/MergeSourceFile.svg)](https://badge.fury.io/py/MergeSourceFile)[![PyPI version](https://badge.fury.io/py/MergeSourceFile.svg)](https://badge.fury.io/py/MergeSourceFile)

[![Python Support](https://img.shields.io/pypi/pyversions/MergeSourceFile.svg)](https://pypi.org/project/MergeSourceFile/)[![Python Support](https://img.shields.io/pypi/pyversions/MergeSourceFile.svg)](https://pypi.org/project/MergeSourceFile/)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)



This document provides the Python API reference for MergeSourceFile v2.0.0.This document describes the internal API of MergeSourceFile v2.0.0 for developers who want to extend or integrate the functionality.



## Overview## What's New in v2.0.0



MergeSourceFile v2.0.0 provides a simple, functional API built around a Jinja2-centric architecture with optional extensions.### Plugin-Based Architecture

- **Complete rewrite**: New modular, extensible plugin system

## Public API- **Plugin Registry**: Central registry for plugin management (`PluginRegistry`)

- **Processing Pipeline**: Configurable execution order (`ProcessorPipeline`)

The package exports the following public API:- **Processing Context**: State management across plugins (`ProcessingContext`)

- **Core Plugins**: `SQLPlusIncludesPlugin`, `SQLPlusVarsPlugin`, `Jinja2Plugin`

```python

from MergeSourceFile import (### New Configuration Format

    main,              # Main entry point function- **Hierarchical TOML**: `[project]`, `[plugins.*]` sections

    load_config,       # Configuration loader- **Individual Plugin Config**: Separate configuration for each plugin

    TemplateEngine,    # Core template engine class- **Configurable Pipeline**: Custom plugin execution order

)- **BREAKING CHANGE**: Legacy `[mergesourcefile]` format no longer supported

```

### Enhanced Testing

## Main Entry Point- **69 comprehensive tests** with 81% code coverage

- **Plugin-oriented structure**: Tests organized by module

### `main(config_file=None, verbose=False)`- **Better separation**: Clear testing of each plugin independently



Main entry point for processing files.## Core Modules and Classes



**Parameters:**### Configuration Module: `config_loader.py`

- `config_file` (str, optional): Path to configuration file. Defaults to `'MKFSource.toml'`

- `verbose` (bool, optional): Enable verbose logging. Defaults to `False`#### `load_config(config_file='MKFSource.toml')`

Loads and validates configuration from a TOML file.

**Returns:**

- None (writes output to file specified in configuration)**Parameters:**

- `config_file` (str, optional): Path to the TOML configuration file. Defaults to `'MKFSource.toml'` in the current directory.

**Raises:**

- `FileNotFoundError`: When input file or configuration file not found**Returns:**

- `ValueError`: When configuration is invalid- `dict`: Normalized configuration dictionary with all settings

- `jinja2.TemplateError`: When template processing fails

**Raises:**

**Example:**- `FileNotFoundError`: When the configuration file doesn't exist (with detailed error message and example)

```python- `ValueError`: When the TOML file is invalid or missing required sections (with formatted error messages)

from MergeSourceFile import main- `tomllib.TOMLDecodeError`: When the TOML file has invalid syntax (wrapped in ValueError with helpful tips)



# Use default MKFSource.toml**Example:**

main()```python

from MergeSourceFile.config_loader import load_config

# Use custom configuration

main(config_file='custom_config.toml', verbose=True)# Load from default MKFSource.toml in current directory

```config = load_config()

print(config['project']['input'])   # Access configuration values

**CLI Equivalent:**print(config['project']['output'])

```bashprint(config['plugins']['sqlplus']['enabled'])

mergesourcefile

```# Or specify a custom path

config = load_config("custom_config.toml")

## Configuration Module```



### `load_config(config_file='MKFSource.toml')`**TOML File Structure (v2.0.0):**

```toml

Load and validate TOML configuration file.[project]

# Required fields

**Module:** `MergeSourceFile.config_loader`input = "input.sql"

output = "output.sql"

**Parameters:**

- `config_file` (str, optional): Path to TOML file. Defaults to `'MKFSource.toml'`# Optional fields (defaults shown)

verbose = false

**Returns:**

- `dict`: Validated configuration dictionary with structure:[plugins.sqlplus]

  ```pythonenabled = true

  {skip_var = false

      'project': {

          'input_file': str,[plugins.jinja2]

          'output_file': str,enabled = false

          'backup': bool,variables_file = "vars.json"

          'verbose': bool,

      },# execution_order moved to [project] section: execution_order = ["sqlplus_includes", "jinja2", "sqlplus_vars"]

      'jinja2': {```

          'enabled': bool,

          'vars_file': str | None,### Plugin System: `plugin_system.py`

          'variable_start_string': str,

          'variable_end_string': str,#### `ProcessingContext`

          'strict_undefined': bool,Data container for processing state across plugins.

          # ... other Jinja2 settings

      },**Attributes:**

      'jinja2.extensions': {- `input_file` (str): Input file being processed

          'sqlplus': bool,- `content` (str): Current content being processed

      },- `base_path` (Path): Base path for resolving relative paths

      'jinja2.extensions.sqlplus': {- `processed_files` (set): Set of processed files (prevents circular includes)

          'process_includes': bool,- `variables` (dict): Variables available for substitution

          'process_defines': bool,- `verbose` (bool): Enable verbose logging

      }

  }#### `ProcessorPlugin` (Abstract Base Class)

  ```Base class for all processing plugins.



**Raises:****Abstract Methods:**

- `FileNotFoundError`: Configuration file not found- `name` (property): Returns the plugin name

- `ValueError`: Invalid TOML syntax or missing required fields- `process(context: ProcessingContext)`: Processes content and returns updated context



**Example:****Example:**

```python```python

from MergeSourceFile import load_configfrom MergeSourceFile.plugin_system import ProcessorPlugin, ProcessingContext



# Load configurationclass MyCustomPlugin(ProcessorPlugin):

config = load_config('MKFSource.toml')    @property

    def name(self) -> str:

# Access configuration        return "my_custom_plugin"

input_file = config['project']['input_file']    

jinja2_config = config.get('jinja2', {})    def process(self, context: ProcessingContext) -> ProcessingContext:

```        # Process context.content

        context.content = context.content.upper()

### `normalize_config(config)`        return context

```

Normalize configuration by applying defaults.

#### `PluginRegistry`

**Module:** `MergeSourceFile.config_loader`Central registry for plugin management.



**Parameters:****Methods:**

- `config` (dict): Raw configuration dictionary from TOML- `register(plugin: ProcessorPlugin)`: Register a plugin

- `get_plugin(name: str)`: Get a plugin by name

**Returns:**- `list_plugins()`: List all registered plugin names

- `dict`: Normalized configuration with all defaults applied

#### `ProcessorPipeline`

**Example:**Executes plugins in a specified order.

```python

from MergeSourceFile.config_loader import normalize_config**Methods:**

import tomllib- `__init__(registry: PluginRegistry, execution_order: list)`: Create pipeline

- `execute(context: ProcessingContext)`: Execute all plugins in order

# Load raw TOML

with open('MKFSource.toml', 'rb') as f:**Example:**

    raw_config = tomllib.load(f)```python

from MergeSourceFile.plugin_system import PluginRegistry, ProcessorPipeline, ProcessingContext

# Normalizefrom MergeSourceFile.plugins import get_available_plugins

config = normalize_config(raw_config)

```# Get available plugins

available_plugins = get_available_plugins()

### `validate_config(config)`

# Setup registry

Validate configuration has required fields.registry = PluginRegistry()

registry.register(available_plugins['sqlplus_includes']({}))

**Module:** `MergeSourceFile.config_loader`registry.register(available_plugins['jinja2']({}))



**Parameters:**# Create pipeline

- `config` (dict): Configuration dictionary to validatepipeline = ProcessorPipeline(registry, ["sqlplus_includes", "jinja2"])



**Returns:**# Execute

- Nonecontext = ProcessingContext()

context.input_file = "main.sql"

**Raises:**context.content = "SELECT * FROM dual;"

- `ValueError`: Missing required fields with detailed messageresult = pipeline.execute(context)

print(result.content)

**Example:**```

```python

from MergeSourceFile.config_loader import validate_config### Plugin Discovery: `plugins/__init__.py`



try:#### `get_available_plugins()`

    validate_config(config)Returns a dictionary of all available plugin classes.

except ValueError as e:

    print(f"Configuration error: {e}")**Returns:**

```- `dict[str, Type[ProcessorPlugin]]`: Mapping of plugin names to plugin classes



## Template Engine**Available Plugins:**

- `'sqlplus_includes'`: `SQLPlusIncludesPlugin` - Processes `@` and `@@` file inclusions

### `class TemplateEngine`- `'sqlplus_vars'`: `SQLPlusVarsPlugin` - Processes `DEFINE` and `UNDEFINE` commands

- `'jinja2'`: `Jinja2Plugin` - Processes Jinja2 template expressions

Core Jinja2 template engine with optional extensions.

**Example:**

**Module:** `MergeSourceFile.template_engine````python

from MergeSourceFile.plugins import get_available_plugins

#### Constructor

# List all available plugins

```pythonplugins = get_available_plugins()

TemplateEngine(config: dict, verbose: bool = False)for name, plugin_class in plugins.items():

```    print(f"{name}: {plugin_class.__name__}")



**Parameters:**# Output:

- `config` (dict): Jinja2 configuration dictionary# sqlplus_includes: SQLPlusIncludesPlugin

- `verbose` (bool, optional): Enable verbose logging. Defaults to `False`# sqlplus_vars: SQLPlusVarsPlugin

# jinja2: Jinja2Plugin

**Example:**

```python# Instantiate a specific plugin

from MergeSourceFile import TemplateEnginejinja2_config = {'variables_file': 'vars.json'}

jinja2_plugin = plugins['jinja2'](jinja2_config)

# Create engine```

config = {

    'enabled': True,**Note:** This is the **recommended way** to access plugins programmatically. Avoid importing plugin classes directly from `MergeSourceFile.plugins.sqlplus_plugin` or similar paths to maintain loose coupling.

    'vars_file': 'variables.json',

    'strict_undefined': False,##### Legacy Processing Orders (Deprecated)

}

engine = TemplateEngine(config, verbose=True)The following functions are kept for backward compatibility but are **deprecated** in v2.0.0:

```

##### `_process_default_order(content, args, input_path, processed_files)`

#### Methods**Order:** File Inclusions → Jinja2 Templates → SQL Variables



##### `process_file(input_file: str, variables: dict) -> str`Best for most use cases where templates don't generate file inclusion directives.



Process a template file with variables.##### `_process_jinja2_first(content, args, input_path, processed_files)`

**Order:** Jinja2 Templates → File Inclusions → SQL Variables

**Parameters:**

- `input_file` (str): Path to input template fileEnables dynamic file inclusion based on Jinja2 variables.

- `variables` (dict): Template variables

##### `_process_includes_last(content, args, input_path, processed_files)`

**Returns:****Order:** SQL Variables → Jinja2 Templates → File Inclusions

- `str`: Processed template content

Useful when SQL variables need to be available in Jinja2 templates.

**Raises:**

- `FileNotFoundError`: Input file not found**Migration Note:** Use the new `ProcessorPipeline` with custom `execution_order` instead.

- `jinja2.TemplateError`: Template syntax error or undefined variable

### Jinja2 Processing

**Example:**

```python#### `process_jinja2_template(content, jinja2_vars_dict, input_path)`

from MergeSourceFile import TemplateEngineProcesses Jinja2 templates with custom filters and error handling.



engine = TemplateEngine({'enabled': True})**Parameters:**

- `content` (str): Template content

# Process with variables- `jinja2_vars_dict` (dict): Variables for template rendering

variables = {- `input_path` (str): Path for error reporting

    'database': 'PROD_DB',

    'schema': 'APP_SCHEMA',**Returns:**

}- `str`: Rendered template content

output = engine.process_file('template.sql', variables)

**Features:**

# Write output- Custom delimiters

with open('output.sql', 'w', encoding='utf-8') as f:- Strict undefined variables

    f.write(output)- Custom filters: `sql_escape`, `strftime`

```- Comprehensive error handling



#### Custom Jinja2 Filters#### Custom Jinja2 Filters



The `TemplateEngine` provides custom filters:##### `sql_escape_filter(value)`

Escapes single quotes for SQL safety.

##### `sql_escape` Filter

**Example:**

Escape SQL strings by doubling single quotes.```python

# Template: SELECT * FROM users WHERE name = '{{ user_name | sql_escape }}';

**Usage:**# Input: user_name = "John O'Brien"

```jinja2# Output: SELECT * FROM users WHERE name = 'John O''Brien';

SELECT * FROM users WHERE name = '{{ username|sql_escape }}';```

```

##### `strftime_filter(value, format_string)`

**Example:**Formats datetime objects and strings.

```python

# If username = "O'Brien"**Example:**

# Output: SELECT * FROM users WHERE name = 'O''Brien';```python

```# Template: -- Generated on {{ now() | strftime('%Y-%m-%d %H:%M:%S') }}

# Output: -- Generated on 2024-10-17 14:30:45

##### `strftime` Filter```



Format datetime objects.### File Processing (Existing Functionality)



**Usage:**#### `process_file_replacements(file_content, input_path, processed_files)`

```jinja2Processes file inclusions (`@` and `@@` directives).

-- Generated: {{ now|strftime('%Y-%m-%d %H:%M:%S') }}

```#### `process_file_sequentially(content, verbose=False)` 🆕 Enhanced in v1.1.1

Processes SQL*Plus variable definitions and substitutions with enhanced DEFINE support.

**Example:**

```python**Parameters:**

from datetime import datetime- `content` (str): Content to process

- `verbose` (bool): Enable detailed logging

variables = {'now': datetime.now()}

# Output: -- Generated: 2025-10-24 14:30:00**Returns:**

```- `str`: Content with variables substituted



## Extensions System**Enhanced Features (v1.1.1):**

- **Improved DEFINE regex**: Supports decimal values, hyphens, complex alphanumeric values

### SQLPlus Extension- **Better error handling**: Invalid DEFINE statements ignored with verbose reporting

- **Enhanced compatibility**: Fixed critical bug with unquoted DEFINE values

**Module:** `MergeSourceFile.extensions.sqlplus`- **Examples of supported syntax**:

  ```sql

Process SQLPlus compatibility features (includes and variables).  DEFINE var = unquoted_value    -- ✅ Fixed in v1.1.1

  DEFINE price = 3.14           -- ✅ New: decimal support

#### `process_sqlplus(content, input_file, base_path, config, verbose)`  DEFINE code = ABC-123         -- ✅ New: hyphenated values

  DEFINE id = DB2_V2_FINAL      -- ✅ New: complex alphanumeric

Main entry point for SQLPlus extension.  DEFINE empty = '';            -- ✅ New: empty string support

  ```

**Parameters:**

- `content` (str): File content to process### Utility Functions

- `input_file` (str): Path to input file

- `base_path` (str): Base directory for relative paths#### `load_jinja2_vars(jinja2_vars_str)`

- `config` (dict): Extension configurationLoads and validates Jinja2 variables from JSON string.

- `verbose` (bool): Enable verbose logging

**Parameters:**

**Returns:**- `jinja2_vars_str` (str): JSON string with variables

- `str`: Processed content with includes expanded and variables substituted

**Returns:**

**Configuration:**- `dict`: Parsed variables dictionary

```python

config = {**Raises:**

    'process_includes': True,  # Process @/@@ directives- `ValueError`: On invalid JSON or parsing errors

    'process_defines': True,   # Process DEFINE and &variables

}#### `show_file_tree(file_tree, level)`

```Displays the file inclusion hierarchy.



**Example:**## Integration Examples

```python

from MergeSourceFile.extensions.sqlplus import process_sqlplus### Basic Integration



content = """```python

@common/header.sqlfrom MergeSourceFile.main import process_file_with_jinja2_replacements

DEFINE schema='HR'import argparse

CREATE TABLE &schema..employees (id NUMBER);

"""# Create arguments object

args = argparse.Namespace(

config = {    jinja2=True,

    'process_includes': True,    jinja2_vars='{"environment": "production"}',

    'process_defines': True,    processing_order="default",

}    skip_var=False,

    verbose=False

result = process_sqlplus()

    content=content,

    input_file='main.sql',# Process content

    base_path='/path/to/scripts',content = "SELECT * FROM {{ table_name }};"

    config=config,result = process_file_with_jinja2_replacements(

    verbose=True    content=content,

)    args=args,

```    input_path="template.sql",

    processed_files=set()

#### `_process_includes(content, input_file, base_path, verbose)`)

```

Process `@` and `@@` include directives (internal function).

### Custom Processing Pipeline

**Parameters:**

- `content` (str): Content with include directives```python

- `input_file` (str): Current file pathfrom MergeSourceFile.main import (

- `base_path` (str): Base directory    process_jinja2_template,

- `verbose` (bool): Verbose logging    process_file_replacements,

    process_variable_replacements,

**Returns:**    load_jinja2_vars

- `str`: Content with includes expanded)



**Supported Directives:**def custom_processor(content, jinja2_vars_json, input_path):

- `@filename` - Include relative to base_path    """Custom processing with additional steps."""

- `@@filename` - Include relative to current file directory    

    # Load variables

**Example:**    jinja2_vars = load_jinja2_vars(jinja2_vars_json)

```python    

from MergeSourceFile.extensions.sqlplus import _process_includes    # Custom pre-processing

    content = content.replace("{{OLD_SYNTAX}}", "{{ new_syntax }}")

content = """    

@scripts/tables.sql    # Jinja2 processing

@@local_config.sql    content = process_jinja2_template(content, jinja2_vars, input_path)

SELECT 1;    

"""    # File inclusions

    content = process_file_replacements(content, input_path, set())

result = _process_includes(    

    content=content,    # SQL variables

    input_file='/project/main.sql',    content = process_variable_replacements(content, input_path)

    base_path='/project',    

    verbose=False    # Custom post-processing

)    content = content.upper()  # Example transformation

```    

    return content

#### `_process_defines(content, verbose)````



Process DEFINE/UNDEFINE and variable substitutions (internal function).### Custom Jinja2 Filters



**Parameters:**```python

- `content` (str): Content with DEFINE statementsfrom jinja2 import Environment, BaseLoader

- `verbose` (bool): Verbose loggingfrom MergeSourceFile.main import sql_escape_filter, strftime_filter



**Returns:**def create_custom_environment():

- `str`: Content with variables substituted    """Create Jinja2 environment with custom filters."""

    

**Supported Syntax:**    env = Environment(

- `DEFINE var='value'` - Define with quotes        loader=BaseLoader(),

- `DEFINE var=value` - Define without quotes        variable_start_string='{{',

- `UNDEFINE var;` - Remove variable        variable_end_string='}}',

- `&var` - Substitute variable        block_start_string='{%',

- `&var..` - Substitute with period concatenation        block_end_string='%}',

        comment_start_string='{#',

**Example:**        comment_end_string='#}',

```python        undefined=StrictUndefined

from MergeSourceFile.extensions.sqlplus import _process_defines    )

    

content = """    # Add built-in filters

DEFINE schema='HR'    env.filters['sql_escape'] = sql_escape_filter

DEFINE version=2.0    env.filters['strftime'] = strftime_filter

    

CREATE TABLE &schema..employees (    # Add custom filters

    id NUMBER,    env.filters['upper_snake'] = lambda x: x.replace(' ', '_').upper()

    version VARCHAR2(10) DEFAULT '&version'    env.filters['quote_identifier'] = lambda x: f'"{x}"'

);    

    return env

UNDEFINE schema;```

"""

## SQL Variables (DEFINE) Syntax

result = _process_defines(content, verbose=False)

```### Supported DEFINE Formats



## Complete Usage ExampleMergeSourceFile supports SQL*Plus-compatible DEFINE syntax with enhanced flexibility:



### Programmatic Usage#### 1. **Quoted Values** (Traditional)

```sql

```pythonDEFINE variable = 'value';

from MergeSourceFile import TemplateEngine, load_configDEFINE schema = 'production';

import jsonDEFINE table_name = 'audit_log';

from pathlib import Path```



# 1. Load configuration#### 2. **Unquoted Values** (SQL*Plus Standard)

config = load_config('MKFSource.toml')```sql

DEFINE counter = 100;

# 2. Load variables from JSONDEFINE database = production;

vars_file = config.get('jinja2', {}).get('vars_file')DEFINE schema_log = DBO;

if vars_file:```

    with open(vars_file, 'r', encoding='utf-8') as f:**Note**: Unquoted values cannot contain spaces. Use quotes for values with spaces.

        variables = json.load(f)

else:#### 3. **Decimal Values** (Enhanced Support)

    variables = {}```sql

DEFINE price = 3.14;

# 3. Create template engineDEFINE ratio = 0.75;

engine = TemplateEngine(DEFINE version = 2.5;

    config=config.get('jinja2', {}),```

    verbose=config.get('project', {}).get('verbose', False)

)#### 4. **Hyphenated Values** (Enhanced Support)

```sql

# 4. Process templateDEFINE code = ABC-123;

input_file = config['project']['input_file']DEFINE version = v1-2-3;

output_content = engine.process_file(input_file, variables)DEFINE project = my-project;

```

# 5. Write output

output_file = config['project']['output_file']#### 5. **Mixed Alphanumeric** (Enhanced Support)

Path(output_file).write_text(output_content, encoding='utf-8')```sql

DEFINE table_audit = log_audit_2024;

print(f"✅ Processed {input_file} → {output_file}")DEFINE schema_name = DB_PROD;

```DEFINE config = app_config_v2;

```

### Custom Template Processing

### Syntax Rules

```python

from MergeSourceFile import TemplateEngine1. **Case-insensitive**: `DEFINE`, `define`, `Define` all work

from datetime import datetime2. **Optional semicolon**: Both `DEFINE var = value;` and `DEFINE var = value` work

3. **Flexible spacing**: Spaces around `=` are optional

# Create engine with custom configuration4. **Value types**: Supports quoted strings, unquoted identifiers, numbers, decimals, and special characters

config = {5. **SQL*Plus compatibility**: Adheres to Oracle SQL*Plus DEFINE standards

    'enabled': True,6. **Spaces in values**: Use quotes for values containing spaces: `DEFINE msg = 'Hello world'`

    'variable_start_string': '<%',

    'variable_end_string': '%>',### Design Decision

    'strict_undefined': True,

}**Our implementation correctly follows SQL*Plus standards by supporting both quoted and unquoted values.**

engine = TemplateEngine(config)

In Oracle SQL*Plus, both of these are valid and equivalent:

# Prepare template- `DEFINE var1 = 123` (unquoted - standard for simple values)

template_content = """- `DEFINE var1 = '123'` (quoted - used for complex values with spaces)

-- Generated: <% now|strftime('%Y-%m-%d') %>

-- Database: <% database %>This design decision was validated against Oracle documentation and real-world SQL*Plus usage patterns.



CREATE TABLE <% schema %>.users (### Examples in Practice

    id NUMBER PRIMARY KEY,

    name VARCHAR2(100)```sql

);-- Database configuration

"""DEFINE SCHEMA_LOG = DBO;

DEFINE TABLE_LOG = AUDIT_LOG;

# Process with variablesDEFINE VERSION = 2.5;

variables = {DEFINE MESSAGE = 'Database deployment completed';  -- Spaces require quotes

    'now': datetime.now(),

    'database': 'PROD',-- Usage in SQL

    'schema': 'APP',CREATE TABLE &SCHEMA_LOG..&TABLE_LOG (

}    id NUMBER,

    version NUMBER DEFAULT &VERSION,

# Note: process_file expects a file path, so write to temp file    message VARCHAR2(100) DEFAULT '&MESSAGE'

from tempfile import NamedTemporaryFile);

with NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:```

    f.write(template_content)

    temp_file = f.name**Result:**

```sql

output = engine.process_file(temp_file, variables)CREATE TABLE DBO.AUDIT_LOG (

print(output)    id NUMBER,

```    version NUMBER DEFAULT 2.5,

    message VARCHAR2(100) DEFAULT 'Database deployment completed'

### Extension Integration);

```

```python

from MergeSourceFile.extensions.sqlplus import process_sqlplus### Invalid Examples (Not Supported)

from MergeSourceFile import TemplateEngine

```sql

# 1. Process SQLPlus features-- ❌ INVALID: Spaces without quotes

sqlplus_config = {DEFINE message = Hello world;

    'process_includes': True,DEFINE path = C:\Program Files\App;

    'process_defines': True,

}-- ✅ CORRECT: Use quotes for spaces

DEFINE message = 'Hello world';

content = """DEFINE path = 'C:\Program Files\App';

@common/setup.sql```

DEFINE owner='SCOTT'

CREATE TABLE &owner..test (id NUMBER);### Error Handling for DEFINE Statements

"""

#### Invalid DEFINE Syntax Detection

processed = process_sqlplus(

    content=content,The system detects and reports invalid DEFINE statements:

    input_file='script.sql',

    base_path='/scripts',```sql

    config=sqlplus_config,-- ❌ These will be ignored and reported in verbose mode:

    verbose=TrueDEFINE variable_name = ;           -- Missing value

)DEFINE = value;                    -- Missing variable name  

DEFINE var@ = value;               -- Invalid character in name

# 2. Then process with Jinja2DEFINE var# = value;               -- Invalid character in name

from tempfile import NamedTemporaryFile

with NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:-- ✅ These are valid:

    f.write(processed)DEFINE var = '';                   -- Empty string (valid)

    temp_file = f.nameDEFINE var = value;                -- Simple value

DEFINE var = 'complex value';      -- Quoted value

engine = TemplateEngine({'enabled': True})```

variables = {'timestamp': '2025-10-24'}

final = engine.process_file(temp_file, variables)#### Error Messages

```

**Verbose Mode** (`--verbose`):

## Error Handling- `[VERBOSE] Ignorando DEFINE con sintaxis inválida en línea 4: 'DEFINE var = ;'`

- `[VERBOSE] Definiendo variable: var_name = value`

### Configuration Errors

**Runtime Errors**:

```python- `Error: La variable 'var_name' se usa antes de ser definida (línea 15).`

from MergeSourceFile import load_config

#### Best Practices for Troubleshooting

try:

    config = load_config('missing.toml')1. **Use verbose mode** to see which DEFINE statements are being ignored

except FileNotFoundError as e:2. **Check syntax carefully** - ensure variable names use only alphanumeric characters and underscores

    print(f"Configuration file not found: {e}")3. **Use quotes for complex values** containing spaces or special characters

except ValueError as e:4. **Verify variable names** in usage match exactly with definitions (case-insensitive)

    print(f"Invalid configuration: {e}")

```## Error Handling



### Template Errors### Exception Types



```pythonThe module raises specific exceptions for different error conditions:

from MergeSourceFile import TemplateEngine

import jinja2- `FileNotFoundError`: When included files are not found

- `ValueError`: For invalid JSON in `--jinja2-vars`

engine = TemplateEngine({'strict_undefined': True})- `TemplateError`: For Jinja2 template syntax errors

- `UndefinedError`: For undefined Jinja2 variables

try:

    output = engine.process_file('template.sql', {})### Error Handling Example

except jinja2.UndefinedError as e:

    print(f"Undefined variable: {e}")```python

except jinja2.TemplateSyntaxError as e:try:

    print(f"Template syntax error at line {e.lineno}: {e.message}")    result = process_file_with_jinja2_replacements(

except FileNotFoundError as e:        content, args, input_path, processed_files

    print(f"Template file not found: {e}")    )

```except ValueError as e:

    print(f"Configuration error: {e}")

### Extension Errorsexcept FileNotFoundError as e:

    print(f"File not found: {e}")

```pythonexcept Exception as e:

from MergeSourceFile.extensions.sqlplus import process_sqlplus    print(f"Processing error: {e}")

```

try:

    result = process_sqlplus(## Extension Points

        content="@missing_file.sql",

        input_file="main.sql",### Adding New Processing Orders

        base_path="/scripts",

        config={'process_includes': True},```python

        verbose=Falsedef _process_custom_order(content, args, input_path, processed_files):

    )    """Custom processing order implementation."""

except FileNotFoundError as e:    

    print(f"Include file not found: {e}")    # Example: SQL first, then custom processing, then Jinja2

except ValueError as e:    if not args.skip_var:

    print(f"Variable error: {e}")        content = process_variable_replacements(content, input_path)

```    

    # Custom processing step

## Type Annotations    content = custom_transformation(content)

    

MergeSourceFile includes type annotations for better IDE support:    if args.jinja2 and args.jinja2_vars:

        jinja2_vars_dict = load_jinja2_vars(args.jinja2_vars)

```python        content = process_jinja2_template(content, jinja2_vars_dict, input_path)

from typing import Dict, Any, Optional    

    content = process_file_replacements(content, input_path, processed_files)

def load_config(config_file: str = 'MKFSource.toml') -> Dict[str, Any]:    

    ...    return content



class TemplateEngine:# Register in main processing function

    def __init__(self, config: Dict[str, Any], verbose: bool = False) -> None:PROCESSING_ORDERS = {

        ...    'default': _process_default_order,

        'jinja2_first': _process_jinja2_first,

    def process_file(self, input_file: str, variables: Dict[str, Any]) -> str:    'includes_last': _process_includes_last,

        ...    'custom': _process_custom_order,  # New order

}

def process_sqlplus(```

    content: str,

    input_file: str,### Adding New Command-Line Arguments

    base_path: str,

    config: Dict[str, Any],```python

    verbose: booldef setup_argument_parser():

) -> str:    """Extended argument parser with custom options."""

    ...    

```    parser = argparse.ArgumentParser(

        description='MergeSourceFile with custom extensions'

## Logging    )

    

MergeSourceFile uses Python's standard `logging` module:    # Existing arguments...

    

```python    # Custom arguments

import logging    parser.add_argument('--custom-filter', type=str,

                        help='Custom filter configuration')

# Enable verbose logging    parser.add_argument('--output-format', choices=['sql', 'json', 'xml'],

logging.basicConfig(                        default='sql', help='Output format')

    level=logging.DEBUG,    

    format='%(levelname)s: %(message)s'    return parser

)```



from MergeSourceFile import main## Testing and Development

main(verbose=True)

```### Running Tests



**Log Levels:**```bash

- `DEBUG`: Detailed processing information (when `verbose=True`)# Run all tests

- `INFO`: General progress messagespython -m pytest

- `WARNING`: Warnings (e.g., unknown extensions)

- `ERROR`: Error messages# Run with coverage

python -m pytest --cov=MergeSourceFile --cov-report=html

## Testing

# Run specific test categories

### Unit Testingpython -m pytest tests/test_jinja2.py -v

python -m pytest tests/test_processing_orders.py -v

```python```

import pytest

from MergeSourceFile import TemplateEngine### Development Setup



def test_simple_template():```bash

    engine = TemplateEngine({'enabled': True})# Clone and setup development environment

    git clone <repository>

    # Create test templatecd MergeSourceFile

    from tempfile import NamedTemporaryFilepython -m venv .venv

    with NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:source .venv/bin/activate  # Linux/Mac

        f.write("SELECT '{{ value }}';").venv\Scripts\activate.bat  # Windows

        temp_file = f.name

    # Install in development mode

    # Processpip install -e .

    result = engine.process_file(temp_file, {'value': 'test'})pip install pytest pytest-cov

    assert result == "SELECT 'test';"```

```

This API documentation provides the foundation for extending MergeSourceFile. The modular design allows for easy customization while maintaining backward compatibility.
### Integration Testing

```python
from MergeSourceFile import main
from pathlib import Path

def test_full_workflow(tmp_path):
    # Create config
    config_file = tmp_path / "MKFSource.toml"
    config_file.write_text("""
    [project]
    input_file = "input.sql"
    output_file = "output.sql"
    
    [jinja2]
    enabled = true
    """)
    
    # Create input
    input_file = tmp_path / "input.sql"
    input_file.write_text("SELECT '{{ test }}';")
    
    # Run
    import os
    os.chdir(tmp_path)
    main()
    
    # Verify
    output_file = tmp_path / "output.sql"
    assert output_file.exists()
```

## Best Practices

### 1. Use Configuration Files

```python
# ✅ Good: Configuration-driven
from MergeSourceFile import main
main()

# ❌ Avoid: Hardcoded values
engine = TemplateEngine({'enabled': True})
output = engine.process_file('hardcoded.sql', {'var': 'value'})
```

### 2. Handle Errors Gracefully

```python
from MergeSourceFile import main

try:
    main(config_file='MKFSource.toml')
except FileNotFoundError as e:
    print(f"Error: {e}")
    print("Please create MKFSource.toml configuration file")
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
    raise
```

### 3. Use Type Hints

```python
from typing import Dict, Any
from MergeSourceFile import TemplateEngine

def process_template(
    config: Dict[str, Any],
    variables: Dict[str, Any]
) -> str:
    engine = TemplateEngine(config)
    return engine.process_file('template.sql', variables)
```

### 4. Leverage Logging

```python
import logging
from MergeSourceFile import main

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Run with verbose mode
main(verbose=True)
```

## API Changes in v2.0.0

### Removed APIs

❌ **Plugin System** (no longer exists):
```python
# OLD (v1.x) - NO LONGER AVAILABLE
from MergeSourceFile import (
    ProcessorPlugin,
    PluginRegistry,
    ProcessorPipeline,
    ProcessingContext,
)
```

❌ **Resource Loader** (no longer exists):
```python
# OLD (v1.x) - NO LONGER AVAILABLE
from MergeSourceFile.resource_loader import (
    read_text_file,
    write_text_file,
    read_json_file,
)
```

### New APIs

✅ **Template Engine**:
```python
# NEW (v2.0)
from MergeSourceFile import TemplateEngine

engine = TemplateEngine(config={'enabled': True})
output = engine.process_file('template.sql', variables)
```

✅ **Extensions**:
```python
# NEW (v2.0)
from MergeSourceFile.extensions.sqlplus import process_sqlplus

result = process_sqlplus(content, input_file, base_path, config, verbose)
```

## References

- [Configuration Guide](CONFIGURATION.md) - TOML configuration reference
- [Architecture Documentation](ARCHITECTURE.md) - System design
- [Examples](EXAMPLES.md) - Usage examples
- [Changelog](CHANGELOG.md) - Version history

---

**Last Updated**: October 2025  
**Version**: 2.0.0  
**API Stability**: Stable
