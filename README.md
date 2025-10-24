# MergeSourceFile# MergeSourceFile 



[![CircleCI](https://dl.circleci.com/status-badge/img/gh/alegorico/MergeSourceFile/tree/main.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/gh/alegorico/MergeSourceFile/tree/main)[![CircleCI](https://dl.circleci.com/status-badge/img/gh/alegorico/MergeSourceFile/tree/main.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/gh/alegorico/MergeSourceFile/tree/main)

[![codecov](https://codecov.io/gh/alegorico/MergeSourceFile/branch/main/graph/badge.svg)](https://codecov.io/gh/alegorico/MergeSourceFile)[![codecov](https://codecov.io/gh/alegorico/MergeSourceFile/branch/main/graph/badge.svg)](https://codecov.io/gh/alegorico/MergeSourceFile)

[![PyPI version](https://badge.fury.io/py/MergeSourceFile.svg)](https://badge.fury.io/py/MergeSourceFile)

[![Python Support](https://img.shields.io/pypi/pyversions/MergeSourceFile.svg)](https://pypi.org/project/MergeSourceFile/)[![PyPI version](https://badge.fury.io/py/MergeSourceFile.svg)](https://badge.fury.io/py/MergeSourceFile)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)[![Python Support](https://img.shields.io/pypi/pyversions/MergeSourceFile.svg)](https://pypi.org/project/MergeSourceFile/)

[![TOML Config](https://img.shields.io/badge/Config-TOML-blue.svg)](https://toml.io/)[![GitHub release](https://img.shields.io/github/release/alegorico/MergeSourceFile.svg)](https://github.com/alegorico/MergeSourceFile/releases)

[![Jinja2](https://img.shields.io/badge/Templates-Jinja2-red.svg)](https://jinja.palletsprojects.com/)[![Downloads](https://pepy.tech/badge/mergesourcefile)](https://pepy.tech/project/mergesourcefile)



**A Jinja2-centric SQL template processor with optional SQLPlus compatibility**[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![GitHub issues](https://img.shields.io/github/issues/alegorico/MergeSourceFile.svg)](https://github.com/alegorico/MergeSourceFile/issues)

Process SQL files with Jinja2 templates, optionally supporting Oracle SQLPlus file inclusions (`@`/`@@`) and variable substitutions (`DEFINE`/`UNDEFINE`).[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/alegorico/MergeSourceFile/graphs/commit-activity)

[![TOML Config](https://img.shields.io/badge/Config-TOML-blue.svg)](https://toml.io/)

## Overview[![Jinja2](https://img.shields.io/badge/Templates-Jinja2-red.svg)](https://jinja.palletsprojects.com/)



MergeSourceFile v2.0.0 embraces **simplicity** with a **Jinja2-centric architecture**:A modular, plugin-based Python tool to process SQL*Plus scripts with Jinja2 template support, resolving file inclusions and variable substitutions.



- **Core**: Jinja2 template engine (always active)## Description

- **Extensions**: Optional preprocessors (currently: SQLPlus compatibility)

- **Configuration**: Simple TOML filesMergeSourceFile is a powerful SQL script processor with a **plugin-based architecture** that provides flexible, configurable processing pipelines. The tool processes SQL*Plus scripts with support for file inclusions (`@`, `@@`), variable substitutions (`DEFINE`/`UNDEFINE`), and Jinja2 templating with custom filters and processing strategies.

- **Philosophy**: Function-based, not over-engineered

## Features

Perfect for:

- 🔄 Processing SQL templates with variables- **🔌 Plugin Architecture**: Modular, extensible design with independent processing plugins

- 📁 Merging SQLPlus scripts with `@includes`- **📦 Processing Pipeline**: Configurable execution order for different processing strategies

- 🔧 Migrating legacy SQLPlus to modern templates- **📁 File Inclusion Resolution**: Processes `@` and `@@` directives to include external SQL files

- 🎯 Database deployment automation- **🔧 Variable Substitution**: Handles `DEFINE` and `UNDEFINE` commands for variable management

- **🔄 Variable Redefinition**: Supports redefining variables throughout the script

## Installation- **� Jinja2 Template Processing**: Full Jinja2 template support with variables, conditionals, loops, and filters

- **🛡️ Custom Jinja2 Filters**: `sql_escape` for SQL injection protection and `strftime` for date formatting

```bash- **⚙️ Flexible Processing Orders**: Customize plugin execution order for different workflows

pip install MergeSourceFile- **🌳 Tree Display**: Shows the inclusion hierarchy in a tree structure

```- **📊 Verbose Mode**: Detailed logging for debugging and understanding the processing flow



**Requirements**: Python 3.11+## Installation



## Quick Start```bash

pip install MergeSourceFile

### 1. Basic Jinja2 Templating```



**Create a template** (`template.sql`):## What's New in v2.0.0

```sql

-- Database: {{ database }}- 🔌 **Plugin Architecture**: Complete rewrite with modular, extensible plugin system

-- Environment: {{ environment }}- 📦 **Processing Pipeline**: Configurable execution order with `ProcessorPipeline`

- 🏗️ **Plugin Registry**: Central registry for plugin management and discovery

CREATE TABLE {{ schema }}.users (- 🔧 **Plugin System**: Abstract base classes (`ProcessorPlugin`) for custom plugins

    id NUMBER PRIMARY KEY,- 📝 **New Configuration Format**: Hierarchical TOML with `[project]`, `[plugins.*]` sections

    name VARCHAR2(100),- ❌ **Breaking Change**: Legacy `[mergesourcefile]` format no longer supported

    created_date DATE DEFAULT SYSDATE- ✅ **Enhanced Testing**: 69 comprehensive tests with 81% code coverage

);- 🎯 **Better Separation**: Clear separation between SQLPlus includes, variables, and Jinja2



{% if environment == "production" %}### Migration from v1.x to v2.0.0

GRANT SELECT ON {{ schema }}.users TO app_role;

{% endif %}**Old Configuration Format (v1.x - NO LONGER SUPPORTED)**:

``````toml

[mergesourcefile]

**Create variables** (`variables.json`):input = "main.sql"

```jsonoutput = "output.sql"

{jinja2 = true

  "database": "PROD_DB",processing_order = "default"

  "environment": "production",```

  "schema": "APP_SCHEMA"

}**New Configuration Format (v2.0.0 - REQUIRED)**:

``````toml

[project]

**Create configuration** (`MKFSource.toml`):input = "main.sql"

```tomloutput = "output.sql"

[project]verbose = false

input_file = "template.sql"

output_file = "output.sql"[plugins.sqlplus]

enabled = true

[jinja2]skip_var = false

enabled = true

vars_file = "variables.json"[plugins.jinja2]

```enabled = true

variables_file = "vars.json"

**Run**:

```bash# execution_order moved to [project] section: execution_order = ["sqlplus_includes", "jinja2", "sqlplus_vars"]

mergesourcefile```

```

## What's New in v1.4.0

**Result** (`output.sql`):

```sql- 🚀 **Configuration-Only Interface**: Removed all command-line parameters in favor of configuration files

-- Database: PROD_DB- 📁 **Standard Configuration File**: The tool now reads from `MKFSource.toml` in the current directory

-- Environment: production- 🎯 **Project-Based Workflow**: Each build configuration has its own dedicated configuration file

- 🧹 **Simplified CLI**: No more complex command-line arguments - just run `mergesourcefile`

CREATE TABLE APP_SCHEMA.users (- ✨ **Cleaner Architecture**: Streamlined codebase focused on configuration-driven processing

    id NUMBER PRIMARY KEY,

    name VARCHAR2(100),## What's New in v1.3.0

    created_date DATE DEFAULT SYSDATE

);- 🚀 **Python 3.11+ Required**: Updated minimum Python version to 3.11+

- � **Native TOML Support**: Uses built-in `tomllib` module (no external dependencies)

GRANT SELECT ON APP_SCHEMA.users TO app_role;- 🔧 **Simplified Dependencies**: Removed `tomli` dependency

```- ⚡ **Better Performance**: Improved performance and maintainability with native TOML support



### 2. SQLPlus Compatibility- 🐛 **DEFINE Bug Fixes**: Critical fix for DEFINE statements without quotes (e.g., `DEFINE VAR = value`)

- 🔧 **Enhanced DEFINE Support**: Improved regex to handle decimal values, hyphens, and complex alphanumeric values

**Enable SQLPlus extension** for legacy scripts with `@` includes and `DEFINE` variables:- 📊 **Better Error Reporting**: Verbose mode now shows ignored DEFINE statements with line numbers

- 🪟 **Windows Compatibility**: Fixed Unicode encoding issues for full Windows support

**Main script** (`main.sql`):- ✅ **Robust Testing**: 17 new tests added, 56/56 tests passing including full CLI integration

```sql

-- Include utility scripts## Configuration File (MKFSource.toml)

@scripts/create_tables.sql

@scripts/create_indexes.sql### How It Works



DEFINE schema='HR'MergeSourceFile now operates exclusively through configuration files. Simply create a `MKFSource.toml` file in your project directory and run `mergesourcefile`.

DEFINE version='2.0'

### Why Configuration Files?

-- Use variables

CREATE TABLE &schema..employees (Configuration files provide several advantages:

    id NUMBER,- **Project-Based**: Each build configuration has its own file

    version VARCHAR2(10) DEFAULT '&version'- **Version Control Friendly**: Store your configuration alongside your source code

);- **Maintainable**: Easier to manage complex configurations

```- **Reusable**: Share configurations across team members

- **Self-Documenting**: Configuration file serves as documentation

**Configuration** (`MKFSource.toml`):

```toml### Quick Start

[project]

input_file = "main.sql"1. **Create a `MKFSource.toml` file** in your project directory:

output_file = "merged.sql"

```toml

[jinja2][project]

enabled = trueinput = "main.sql"

output = "merged.sql"

[jinja2.extensions]

sqlplus = true[plugins.sqlplus]

enabled = true

[jinja2.extensions.sqlplus]```

process_includes = true   # Process @/@@ directives

process_defines = true    # Process DEFINE and &variables2. **Run the tool** (it automatically reads from `MKFSource.toml` in the current directory):

```

```bash

**Run**:mergesourcefile

```bash```

mergesourcefile

```That's it! No command-line arguments needed. The tool exclusively reads from `MKFSource.toml`.



The output will have all `@` includes expanded and `&variables` substituted.### Configuration Options



### 3. Combined WorkflowAll options are specified in the `MKFSource.toml` file:



**Mix Jinja2 and SQLPlus** features:```toml

[project]

```sql# Required fields

-- SQLPlus includesinput = "input.sql"              # Input file to process

@common/header.sqloutput = "output.sql"            # Output file for merged result



-- SQLPlus variables# Optional fields (with default values)

DEFINE table_prefix='tbl_'verbose = false                  # Enable verbose mode

execution_order = ["sqlplus_includes", "jinja2", "sqlplus_vars"]  # Plugin execution order

-- Jinja2 templating

{% for table in tables %}[plugins.sqlplus]

CREATE TABLE &table_prefix{{ table.name }} (# SQL*Plus plugin configuration

    id NUMBER PRIMARY KEY,enabled = true                   # Enable SQL*Plus processing

    {% for col in table.columns %}skip_var = false                 # Skip DEFINE/UNDEFINE variable substitution

    {{ col.name }} {{ col.type }}{% if not loop.last %},{% endif %}

    {% endfor %}[plugins.jinja2]

);# Jinja2 template plugin configuration

{% endfor %}enabled = false                  # Enable Jinja2 template processing

```variables_file = "vars.json"     # JSON file with Jinja2 variables

```

**Processing order**:

1. SQLPlus includes expanded (`@` → file contents)### Example Configurations

2. SQLPlus variables substituted (`&var` → value)

3. Jinja2 templates rendered (`{{ }}`, `{% %}`)**Basic Processing** (`MKFSource.toml`):

```toml

## Features[project]

input = "main.sql"

### Core Jinja2 Featuresoutput = "merged.sql"



✅ **Template Variables**: `{{ variable_name }}`  [plugins.sqlplus]

✅ **Conditionals**: `{% if condition %} ... {% endif %}`  enabled = true

✅ **Loops**: `{% for item in items %} ... {% endfor %}`  ```

✅ **Filters**: `{{ value|filter_name }}`  

✅ **Template Inheritance**: `{% extends "base.sql" %}`  **With Jinja2 Templates** (`MKFSource.toml`):

✅ **Macros**: Reusable template blocks  ```toml

[project]

**Custom Filters**:input = "template.sql"

- `sql_escape`: Escape SQL strings (doubles single quotes)output = "generated.sql"

  ```sqlverbose = false

  SELECT * FROM users WHERE name = '{{ username|sql_escape }}';execution_order = ["jinja2", "sqlplus_includes", "sqlplus_vars"]

  ```

- `strftime`: Format datetime objects[plugins.jinja2]

  ```sqlenabled = true

  -- Generated on: {{ now|strftime('%Y-%m-%d %H:%M:%S') }}variables_file = "production_vars.json"

  ``````



### SQLPlus Extension Features**Verbose Mode for Debugging** (`MKFSource.toml`):

```toml

When enabled with `[jinja2.extensions] sqlplus = true`:[project]

input = "debug.sql"

✅ **File Inclusions**:output = "debug_output.sql"

- `@filename` - Include relative to base pathverbose = true

- `@@filename` - Include relative to current file

- Recursive includes with circular dependency detection[plugins.sqlplus]

enabled = true

✅ **Variable Management**:skip_var = false

- `DEFINE var='value'` - Define variables```

- `DEFINE var=value` - Define without quotes

- `UNDEFINE var;` - Remove variables### Multiple Configurations for Different Environments

- `&var` - Substitute variable value

- `&var..` - Variable with period concatenationYou can maintain multiple configuration files for different build scenarios:



## Configuration```bash

# Development build

### Minimal Configurationcp MKFSource.dev.toml MKFSource.toml

mergesourcefile

```toml

[project]# Production build  

input_file = "template.sql"cp MKFSource.prod.toml MKFSource.toml

output_file = "output.sql"mergesourcefile

```

[jinja2]

enabled = trueSee the [Configuration Guide](CONFIGURATION.md) for a complete reference with all available options and examples.

```

## Usage

### Full Configuration

Simply run `mergesourcefile` in the directory containing your `MKFSource.toml` file:

```toml

[project]```bash

input_file = "src/main.sql"mergesourcefile

output_file = "build/output.sql"```

backup = true          # Create backup before overwriting

verbose = true         # Enable detailed loggingThe tool will:

1. Look for `MKFSource.toml` in the current directory

[jinja2]2. Read the configuration

enabled = true3. Load and configure plugins based on settings

vars_file = "config/variables.json"4. Execute the processing pipeline in the specified order

5. Output the merged result

# Custom delimiters (optional)

variable_start_string = "{{"### Workflow

variable_end_string = "}}"

strict_undefined = false  # Allow undefined variables1. **Create your configuration**: Create a `MKFSource.toml` file in your project directory

2. **Configure your build**: Set the input/output files and plugin settings

[jinja2.extensions]3. **Run the tool**: Execute `mergesourcefile` (no arguments needed, reads from `MKFSource.toml`)

sqlplus = true  # Enable SQLPlus compatibility4. **Get your output**: Find the merged SQL in the output file specified in your configuration



[jinja2.extensions.sqlplus]**Important**: The tool exclusively reads from `MKFSource.toml` in the current directory. There are no command-line parameters for specifying configuration files or overriding settings.

process_includes = true

process_defines = true### Configuration File Format

```

The `MKFSource.toml` file uses a hierarchical structure with three main sections:

See [CONFIGURATION.md](CONFIGURATION.md) for complete reference.

```toml

## Usage Examples[project]

input = "main.sql"              # Required: Input SQL file

### Example 1: Environment-Specific Deploymentsoutput = "merged.sql"           # Required: Output file for merged result

verbose = false                 # Optional: Enable detailed logging

**Template** (`deploy.sql`):execution_order = ["sqlplus_includes", "jinja2", "sqlplus_vars"]  # Plugin execution order

```sql

{% if env == "production" %}[plugins.sqlplus]

ALTER SYSTEM SET sga_target = 8G;enabled = true                   # Enable SQLPlus processing (includes + variables)

ALTER SYSTEM SET pga_aggregate_target = 4G;skip_var = false                 # Skip variable substitution if true

{% elif env == "development" %}

ALTER SYSTEM SET sga_target = 2G;[plugins.jinja2]

ALTER SYSTEM SET pga_aggregate_target = 1G;enabled = false                  # Enable Jinja2 template processing

{% endif %}variables_file = "vars.json"     # JSON file with Jinja2 variables

```

CREATE TABLESPACE {{ tablespace_name }}

  DATAFILE '{{ datafile_path }}' SIZE {{ datafile_size }};### Plugin System

```

MergeSourceFile v2.0.0 introduces a plugin-based architecture with three core plugins:

**Variables** (`prod.json`):

```json1. **sqlplus_includes**: Processes `@` and `@@` file inclusion directives

{2. **jinja2**: Processes Jinja2 template variables and expressions

  "env": "production",3. **sqlplus_vars**: Processes `DEFINE` and `UNDEFINE` variable commands

  "tablespace_name": "PROD_DATA",

  "datafile_path": "/oradata/prod/data01.dbf",You can customize the execution order to match your workflow:

  "datafile_size": "10G"

}```toml

```# Default: Includes → Jinja2 → Variables

execution_order = ["sqlplus_includes", "jinja2", "sqlplus_vars"]

### Example 2: Schema Generation from Metadata

# Jinja2 First: Templates → Includes → Variables  

**Template** (`schema.sql`):execution_order = ["jinja2", "sqlplus_includes", "sqlplus_vars"]

```sql

{% for table in tables %}# Variables First: Variables → Jinja2 → Includes

-- Table: {{ table.name }}execution_order = ["sqlplus_vars", "jinja2", "sqlplus_includes"]

CREATE TABLE {{ table.name }} (```

    {% for column in table.columns %}

    {{ column.name }} {{ column.type }}See the [Configuration Guide](CONFIGURATION.md) for detailed information about all configuration options.

    {%- if column.primary_key %} PRIMARY KEY{% endif %}

    {%- if column.not_null %} NOT NULL{% endif %}## Features Details

    {%- if not loop.last %},{% endif %}

    {% endfor %}## How It Works

);

### File Inclusion

{% endfor %}

```- `@filename`: Includes a file relative to the original base path

- `@@filename`: Includes a file relative to the current file's directory

**Variables** (`metadata.json`):

```json### Variable Substitution

{

  "tables": [#### DEFINE Syntax (Enhanced in v1.1.1)

    {- `DEFINE varname = 'quoted value';`: Defines with quoted value (supports spaces)

      "name": "users",- `DEFINE varname = unquoted_value;`: Defines with unquoted value (no spaces)

      "columns": [- `DEFINE varname = 3.14;`: Supports decimal values

        {"name": "id", "type": "NUMBER", "primary_key": true, "not_null": true},- `DEFINE varname = ABC-123;`: Supports hyphenated values

        {"name": "username", "type": "VARCHAR2(50)", "not_null": true},- `DEFINE varname = '';`: Supports empty string values

        {"name": "email", "type": "VARCHAR2(100)"}

      ]#### Variable Usage

    },- `&varname`: References a variable for substitution

    {- `&varname..`: Variable concatenation with period

      "name": "orders",- `UNDEFINE varname;`: Removes a variable definition

      "columns": [

        {"name": "id", "type": "NUMBER", "primary_key": true},#### Error Handling (v1.1.1)

        {"name": "user_id", "type": "NUMBER", "not_null": true},- Invalid DEFINE syntax is ignored and reported in verbose mode

        {"name": "amount", "type": "NUMBER(10,2)"}- Example: `DEFINE var = ;` will be skipped with a warning

      ]- Variables must be defined before use or an error is thrown

    }

  ]### 🆕 Jinja2 Template Processing

}

```#### Basic Template Syntax

- `{{ variable }}`: Variable substitution

### Example 3: Migrating Legacy SQLPlus Scripts- `{% if condition %}...{% endif %}`: Conditional blocks

- `{% for item in list %}...{% endfor %}`: Loop blocks

**Legacy** (`old_script.sql`):- `{# comment #}`: Template comments

```sql

@utils/settings.sql#### Custom Filters

@@local_params.sql- `sql_escape`: Escapes single quotes for SQL safety

  ```sql

DEFINE schema='HR'  SELECT * FROM users WHERE name = '{{ user_name | sql_escape }}';

DEFINE version='1.0'  ```

- `strftime`: Formats datetime objects

CREATE TABLE &schema..employees (  ```sql

    id NUMBER,  -- Generated on {{ now() | strftime('%Y-%m-%d %H:%M:%S') }}

    version VARCHAR2(10) DEFAULT '&version'  ```

);

```#### Processing Orders

1. **default**: File Inclusions → Jinja2 Templates → SQL Variables

**Modernized** (`new_script.sql`):2. **jinja2_first**: Jinja2 Templates → File Inclusions → SQL Variables

```sql3. **includes_last**: SQL Variables → Jinja2 Templates → File Inclusions

{# Keep backwards compatibility with includes #}

@utils/settings.sql#### Dynamic File Inclusion Example

@@local_params.sql```sql

-- Using jinja2_first order to dynamically determine which files to include

{# Use Jinja2 for cleaner templating #}{% if environment == 'production' %}

CREATE TABLE {{ schema }}.employees (@prod_config.sql

    id NUMBER,{% else %}

    version VARCHAR2(10) DEFAULT '{{ version }}',@dev_config.sql

    {% if include_audit_columns %}{% endif %}

    created_by VARCHAR2(50),```

    created_date DATE DEFAULT SYSDATE,

    {% endif %}## Complete Example

);

```### Input Template (`template.sql`)

```sql

Both work! You can migrate gradually.{# This is a Jinja2 comment #}

-- Database setup for {{ environment | upper }} environment

## Command-Line Interface-- Generated on {{ now() | strftime('%Y-%m-%d %H:%M:%S') }}



MergeSourceFile uses **configuration files only** (no CLI arguments):{% if environment == 'production' %}

@production_settings.sql

```bash{% else %}

# Reads from MKFSource.toml in current directory@development_settings.sql

mergesourcefile{% endif %}



# That's it! All configuration is in the TOML fileDEFINE db_name = '{{ database_name }}';

```DEFINE table_prefix = '{{ table_prefix }}';



**Why configuration-only?**CREATE TABLE &table_prefix._users (

- ✅ Reproducible builds    id NUMBER PRIMARY KEY,

- ✅ Version-controlled configurations    name VARCHAR2(100) NOT NULL,

- ✅ Clear project structure    email VARCHAR2(255) UNIQUE,

- ✅ No complex CLI syntax    created_date DATE DEFAULT SYSDATE

);

## Architecture

{% for table in additional_tables %}

```CREATE TABLE &table_prefix._{{ table.name }} (

┌──────────────┐    id NUMBER PRIMARY KEY,

│  Input File  │    {% for column in table.columns -%}

└──────┬───────┘    {{ column.name }} {{ column.type }}{% if not loop.last %},{% endif %}

       │    {% endfor %}

       ▼);

┌──────────────────────────────┐{% endfor %}

│   TemplateEngine             │

│  ┌────────────────────────┐  │-- Insert sample data with escaped values

│  │ SQLPlus Extension      │  │  (optional)INSERT INTO &table_prefix._users (name, email) 

│  │  - Expand @/@@         │  │VALUES ('{{ sample_user | sql_escape }}', '{{ sample_email | sql_escape }}');

│  │  - Process DEFINE      │  │```

│  └───────────┬────────────┘  │

│              ▼               │### Configuration (`MKFSource.toml`)

│  ┌────────────────────────┐  │```toml

│  │ Jinja2 Core            │  │  (always)[project]

│  │  - Load variables      │  │input = "template.sql"

│  │  - Apply filters       │  │output = "output.sql"

│  │  - Render template     │  │execution_order = ["jinja2", "sqlplus_includes", "sqlplus_vars"]

│  └───────────┬────────────┘  │

└──────────────┼───────────────┘[plugins.jinja2]

               ▼enabled = true

       ┌──────────────┐variables_file = "vars.json"

       │ Output File  │```

       └──────────────┘

```### Variables File (`vars.json`)

```json

**Key Design Principles**:{

1. **Jinja2 is the core** - Always active, not "just another plugin"  "environment": "production",

2. **Extensions are optional** - Add functionality, don't replace it  "database_name": "MYAPP_DB",

3. **Functions over classes** - Simple, testable, maintainable  "table_prefix": "APP",

4. **Clear data flow** - Input → Extensions → Jinja2 → Output  "sample_user": "John O'Brien",

  "sample_email": "john@example.com",

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed design documentation.  "additional_tables": [

    {

## What's New in v2.0.0      "name": "products",

      "columns": [

### Major Redesign 🎉        {"name": "title", "type": "VARCHAR2(200)"},

        {"name": "price", "type": "NUMBER(10,2)"}

v2.0.0 is a **complete architectural overhaul** focused on **simplicity**:      ]

    }

#### Removed ❌  ]

- ❌ Plugin system (over-engineered)}

- ❌ Plugin registry and discovery```

- ❌ Configurable execution order

- ❌ `resource_io` module### Run

- ❌ Complex plugin lifecycle```bash

mergesourcefile

#### Added ✅```

- ✅ Jinja2-centric design

- ✅ Simple extension system## Migration Guide from v1.x to v2.0.0

- ✅ Function-based architecture

- ✅ 92% code coverage (50 tests)**BREAKING CHANGE**: v2.0.0 introduces a new plugin-based architecture with a hierarchical configuration format. The old `[mergesourcefile]` format is no longer supported.

- ✅ Cleaner, more maintainable codebase

### Step 1: Update Your Configuration File Name

#### Changed 🔄

- 🔄 Configuration structure: `[jinja2]` + `[jinja2.extensions]`Rename your configuration file to `MKFSource.toml` and place it in the directory where you run `mergesourcefile`:

- 🔄 Fixed processing order: Extensions → Jinja2

- 🔄 Simplified API: `TemplateEngine` class```bash

- 🔄 Better error messages# If you have an old config file, rename it

mv myconfig.toml MKFSource.toml

### Migration from v1.x```



**Old (v1.x)**:**Note**: Since v1.4.0, the tool no longer accepts command-line parameters like `--config`. It exclusively reads from `MKFSource.toml` in the current directory.

```toml

[mergesourcefile]### Step 2: Update Your Configuration Structure

input = "main.sql"

output = "output.sql"**Old Configuration (v1.x)**:

jinja2 = true```toml

```[mergesourcefile]

input = "main.sql"

**New (v2.0)**:output = "output.sql"

```tomljinja2 = true

[project]jinja2_vars = "vars.json"

input_file = "main.sql"skip_var = false

output_file = "output.sql"processing_order = "default"

```

[jinja2]

enabled = true**New Configuration (v2.0.0)**:

```toml

[jinja2.extensions][project]

sqlplus = trueinput = "main.sql"

```output = "output.sql"

verbose = false

**Breaking Changes**:

- Configuration section names changed[plugins.sqlplus]

- Parameters renamed (`input` → `input_file`)enabled = true

- No more `execution_order` parameterskip_var = false

- No more plugin system imports

[plugins.jinja2]

See [CHANGELOG.md](CHANGELOG.md) for complete migration guide.enabled = true

variables_file = "vars.json"

## Python API

# execution_order moved to [project] section: execution_order = ["sqlplus_includes", "jinja2", "sqlplus_vars"]

```python```

from MergeSourceFile import TemplateEngine, load_config

### Step 2: Update Processing Order Mapping

# Load configuration

config = load_config('MKFSource.toml')| Old (v1.x) | New (v2.0.0) |

|------------|------------|

# Create template engine| `processing_order = "default"` | `execution_order = ["sqlplus_includes", "jinja2", "sqlplus_vars"]` |

engine = TemplateEngine(| `processing_order = "jinja2_first"` | `execution_order = ["jinja2", "sqlplus_includes", "sqlplus_vars"]` |

    config=config.get('jinja2', {}),| `processing_order = "includes_last"` | `execution_order = ["sqlplus_vars", "jinja2", "sqlplus_includes"]` |

    verbose=config.get('project', {}).get('verbose', False)

)### Step 3: Test Your Configuration



# Process file```bash

variables = {"env": "production", "version": "2.0.0"}mergesourcefile

output = engine.process_file(```

    input_file='template.sql',

    variables=variablesFor detailed migration instructions, see [CONFIGURATION.md](CONFIGURATION.md) and [RELEASE_NOTES_v2.0.0.md](RELEASE_NOTES_v2.0.0.md).

)

## Best Practices

# Write output

with open('output.sql', 'w', encoding='utf-8') as f:### When to Use Each Processing Order

    f.write(output)

```- **default**: `["sqlplus_includes", "jinja2", "sqlplus_vars"]` - Best for most use cases where Jinja2 templates don't need to generate file inclusion directives

- **jinja2_first**: `["jinja2", "sqlplus_includes", "sqlplus_vars"]` - Use when Jinja2 templates need to conditionally determine which files to include

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete API reference.- **includes_last**: `["sqlplus_vars", "jinja2", "sqlplus_includes"]` - Use when you need SQL variables to be processed before Jinja2 templates and file inclusions



## Testing### Security Considerations



MergeSourceFile has comprehensive test coverage:Always use the `sql_escape` filter when inserting user-provided data:

```sql

```bash-- ❌ Vulnerable to SQL injection

# Run all testsSELECT * FROM users WHERE name = '{{ user_input }}';

pytest

-- ✅ Safe with sql_escape filter

# Run with coverageSELECT * FROM users WHERE name = '{{ user_input | sql_escape }}';

pytest --cov=MergeSourceFile --cov-report=html```



# Run specific test file### Performance Tips

pytest tests/test_template_engine.py -v

```- Enable only the plugins you need in `[plugins]` section

- Use `skip_var = true` in `[plugins.sqlplus]` if you don't need SQL variable processing

**Test Statistics**:- For large projects, consider splitting templates into smaller, focused files

- **50 tests** total- Use Jinja2 comments `{# comment #}` instead of SQL comments for template-specific notes

- **92% code coverage**

- Tests for: config loading, template engine, SQLPlus extension, integration## Platform Compatibility



## Development### Operating Systems

- ✅ **Linux**: Full support with all features

### Setup Development Environment- ✅ **macOS**: Full support with all features  

- ✅ **Windows**: Full support with enhanced compatibility

```bash  - Fixed Unicode encoding issues for CLI operations

# Clone repository  - All 69 tests pass successfully on Windows systems

git clone https://github.com/alegorico/MergeSourceFile.git  - Proper error codes and file path handling

cd MergeSourceFile

### Python Versions

# Create virtual environment- Python 3.11+ (Required for native TOML support)

python -m venv .venv- Tested with Python 3.11, 3.12, 3.13, 3.14

source .venv/bin/activate  # On Windows: .venv\Scripts\activate

### Character Encoding

# Install in development mode- Primary support: UTF-8 (recommended)

pip install -e ".[dev]"- Windows compatibility: ASCII-safe output for CLI operations

- All text files should use UTF-8 encoding for best results

# Run tests

pytest## Troubleshooting

```

### Common Issues

### Project Structure

1. **Configuration errors**: Ensure your `MKFSource.toml` follows the v2.0.0 format with `[project]` and `[plugins.*]` sections

```2. **DEFINE syntax errors**: Use verbose mode (`verbose = true` in config) to see ignored invalid DEFINE statements

MergeSourceFile/3. **Jinja2 syntax errors**: Ensure proper template syntax with matching braces and tags

├── MergeSourceFile/4. **Variable not found**: Check that all variables are provided via `variables_file` in `[plugins.jinja2]`

│   ├── __init__.py5. **File inclusion issues**: Verify file paths and choose appropriate processing order

│   ├── main.py                 # Main orchestrator

│   ├── config_loader.py        # Configuration management### Debug Mode

│   ├── template_engine.py      # Core Jinja2 engine

│   └── extensions/Enable verbose mode in your configuration to see detailed processing information:

│       ├── __init__.py```toml

│       └── sqlplus.py          # SQLPlus extension[project]

├── tests/input = "template.sql"

│   ├── test_config_loader.pyoutput = "output.sql"

│   ├── test_template_engine.pyverbose = true

│   ├── test_sqlplus_extension.py```

│   └── test_integration.py

├── MKFSource.toml              # Example configuration## License

├── pyproject.toml              # Package metadata

└── README.mdThis project is licensed under the MIT License.  

```You are free to use, copy, modify, and distribute this software, provided that the copyright notice and this permission are included.  

The software is provided "as is", without warranty of any kind.

## Documentation

## Author

- **[CONFIGURATION.md](CONFIGURATION.md)** - Complete configuration reference

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design and architectureAlejandro G.

- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Python API reference

- **[EXAMPLES.md](EXAMPLES.md)** - Usage examples and patterns## Contributing

- **[CHANGELOG.md](CHANGELOG.md)** - Version history and migration notes

Contributions are welcome! Please feel free to submit a Pull Request.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Ensure all tests pass (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/alegorico/MergeSourceFile/issues)
- **Discussions**: [GitHub Discussions](https://github.com/alegorico/MergeSourceFile/discussions)
- **PyPI**: [MergeSourceFile on PyPI](https://pypi.org/project/MergeSourceFile/)

## Credits

**Author**: [alegorico](https://github.com/alegorico)

**Technologies**:
- [Jinja2](https://jinja.palletsprojects.com/) - Template engine
- [TOML](https://toml.io/) - Configuration format
- [pytest](https://pytest.org/) - Testing framework

---

**Made with ❤️ for database developers who love automation**
