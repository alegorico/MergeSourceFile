# MergeSourceFile

[![CircleCI](https://dl.circleci.com/status-badge/img/gh/alegorico/MergeSourceFile/tree/main.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/gh/alegorico/MergeSourceFile/tree/main)
[![codecov](https://codecov.io/gh/alegorico/MergeSourceFile/branch/main/graph/badge.svg)](https://codecov.io/gh/alegorico/MergeSourceFile)
[![PyPI version](https://badge.fury.io/py/MergeSourceFile.svg)](https://badge.fury.io/py/MergeSourceFile)
[![Python Support](https://img.shields.io/pypi/pyversions/MergeSourceFile.svg)](https://pypi.org/project/MergeSourceFile/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub release](https://img.shields.io/github/release/alegorico/MergeSourceFile.svg)](https://github.com/alegorico/MergeSourceFile/releases)
[![Downloads](https://pepy.tech/badge/mergesourcefile)](https://pepy.tech/project/mergesourcefile)
[![GitHub issues](https://img.shields.io/github/issues/alegorico/MergeSourceFile.svg)](https://github.com/alegorico/MergeSourceFile/issues)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/alegorico/MergeSourceFile/graphs/commit-activity)
[![TOML Config](https://img.shields.io/badge/Config-TOML-blue.svg)](https://toml.io/)
[![Jinja2](https://img.shields.io/badge/Templates-Jinja2-red.svg)](https://jinja.palletsprojects.com/)

**A streamlined Jinja2-centric SQL template processor with optional SQLPlus compatibility**

Process SQL files with Jinja2 templates, optionally supporting Oracle SQLPlus file inclusions (`@`/`@@`) and variable substitutions (`DEFINE`/`UNDEFINE`).

## Overview

MergeSourceFile v2.0.0 introduces a **simplified, unified architecture**:

- **🎯 Streamlined Core**: Just 2 main files (`core.py` + `template_engine.py`)
- **⚡ Short Command**: Use `msf` instead of `mergesourcefile` 
- **🧩 Extension Registry**: Centralized extension management
- **🔧 Jinja2-Centric**: Template engine at the core with optional extensions
- **📋 Simple Config**: Clean TOML configuration

## Description

MergeSourceFile is a powerful, streamlined SQL script processor with a **unified architecture** that provides flexible template processing. The tool processes SQL*Plus scripts with support for file inclusions (`@`, `@@`), variable substitutions (`DEFINE`/`UNDEFINE`), and Jinja2 templating with custom filters and extensions.

## Features

- **🔌 Plugin Architecture**: Modular, extensible design with independent processing plugins
- **📦 Processing Pipeline**: Configurable execution order for different processing strategies
- **📁 File Inclusion Resolution**: Processes `@` and `@@` directives to include external SQL files
- **🔧 Variable Substitution**: Handles `DEFINE` and `UNDEFINE` commands for variable management
- **🔄 Variable Redefinition**: Supports redefining variables throughout the script
- **🎨 Jinja2 Template Processing**: Full Jinja2 template support with variables, conditionals, loops, and filters
- **🛡️ Custom Jinja2 Filters**: `sql_escape` for SQL injection protection and `strftime` for date formatting
- **⚠️ Smart Conflict Resolution**: Automatic exclusion between SQLPlus and Jinja2 include systems
- **🔀 Dual Include Support**: Choose between `@file` (SQLPlus) or `{% include %}` (Jinja2) - never both
- **�️ Variable Namespace Separation**: Forced `sql_` prefix for DEFINE variables in Jinja2 context
- **⚡ Conflict Detection**: Automatic warnings for variable name conflicts between systems
- **🔄 Variable Extraction**: DEFINE variables automatically available in Jinja2 templates
- **�🌳 Tree Display**: Shows the inclusion hierarchy in a tree structure
- **📊 Verbose Mode**: Detailed logging for debugging and understanding the processing flow

Perfect for:

- 🔄 Processing SQL templates with variables
- 📁 Merging SQLPlus scripts with `@includes`
- 🔧 Migrating legacy SQLPlus to modern templates
- 🎯 Database deployment automation

## Installation

```bash
pip install MergeSourceFile
```

**Requirements**: Python 3.11+

## Quick Start

### 1. Basic Jinja2 Templating

**Create a template** (`template.sql`):

```sql
-- Database: {{ database }}
-- Environment: {{ environment }}

CREATE TABLE {{ schema }}.users (
    id NUMBER PRIMARY KEY,
    name VARCHAR2(100),
    created_date DATE DEFAULT SYSDATE
);

{% if environment == "production" %}
GRANT SELECT ON {{ schema }}.users TO app_role;
{% endif %}
```

**Create variables** (`variables.json`):

```json
{
  "database": "PROD_DB",
  "environment": "production",
  "schema": "APP_SCHEMA"
}
```

**Create configuration** (`MKFSource.toml`):

```toml
[project]
input = "template.sql"
output = "output.sql"

[jinja2]
enabled = true
variables_file = "variables.json"
```

**Run the processor**:

```bash
msf
# or use the full command: mergesourcefile
```

### 2. With SQLPlus Extension

**Configuration** (`MKFSource.toml`):

```toml
[project]
input = "main.sql"
output = "output.sql"

[jinja2]
enabled = true

[jinja2.extensions]
sqlplus = true

[jinja2.sqlplus]
process_includes = true   # SQLPlus @file includes (disables Jinja2 {% include %})
process_defines = true    # DEFINE/UNDEFINE variables
```

### ⚠️ Important: Include System Behavior

MergeSourceFile prevents conflicts between include systems:

- **SQLPlus includes active** (`process_includes = true`) → `{% include %}` **disabled**
- **SQLPlus includes inactive** → `{% include %}` **enabled** 

Choose the approach that fits your project:

#### Option A: Modern Jinja2 (Recommended)
```toml
[jinja2]
enabled = true
# No SQLPlus extension = {% include %} works
```

#### Option B: Legacy SQLPlus Support  
```toml
[jinja2]
enabled = true
extensions = ["sqlplus"]

[jinja2.sqlplus]
process_includes = true   # @file works, {% include %} disabled
```

## Configuration

MergeSourceFile uses TOML configuration files. For complete configuration reference, visit the [Configuration Guide](https://github.com/alegorico/MergeSourceFile/blob/main/CONFIGURATION.md).

### Basic Structure

```toml
[project]                          # Required section
input = "template.sql"             # Required: input file
output = "output.sql"              # Required: output file
verbose = false                    # Optional: detailed logging

[jinja2]                           # Required section
enabled = true                     # Required: enable Jinja2
variables_file = "vars.json"       # Optional: variables file

[jinja2.extensions]                # Optional section
sqlplus = true                     # Optional: enable SQLPlus extension
```

## Usage Examples

For detailed examples and practical use cases, visit the [Examples Guide](https://github.com/alegorico/MergeSourceFile/blob/main/EXAMPLES.md).

## What's New in v2.0.0

Version 2.0.0 represents a **complete architectural overhaul** focused on **simplicity and clarity**:

- ✅ **Jinja2-centric design**: Template engine as core component
- ✅ **Extension system**: Simple function-based extensions  
- ✅ **Enhanced testing**: 50+ comprehensive tests
- ✅ **92% code coverage** (50 tests)
- ✅ **Complete documentation rewrite**
- ❌ **Breaking change**: New configuration format required

### Migration from v1.x

**Old format (v1.x - no longer supported)**:
```toml
[mergesourcefile]
input = "main.sql"
output = "output.sql"
```

**New format (v2.0.0 - required)**:
```toml
[project]
input = "main.sql"
output = "output.sql"

[jinja2]
enabled = true
```

## Architecture

MergeSourceFile v2.0.0 features a **streamlined unified architecture**:

### Core Components

1. **`core.py`**: Configuration loading, logging setup, and main orchestration
2. **`template_engine.py`**: Jinja2 engine + Extension registry + Extension manager

### Extension System

- **Extension Registry**: Centralized registration of all available extensions
- **Extension Manager**: Handles loading, execution order, and namespace management
- **SQLPlus Extension**: File inclusions (`@`/`@@`) and variable processing (`DEFINE`/`UNDEFINE`)

## Command-Line Interface

```bash
# Basic usage with short command
msf

# Or use the full command name
mergesourcefile

# Both commands support the same options
msf --help
```

## Python API

```python
from MergeSourceFile import TemplateEngine, load_config

# Using configuration file
config = load_config('MKFSource.toml')
engine = TemplateEngine(config)
result = engine.process_file('template.sql', variables={"schema": "APP", "env": "prod"})

# Direct usage without config file
engine = TemplateEngine({
    'jinja2': {
        'enabled': True,
        'extensions': ['sqlplus']
    }
})
result = engine.process_file('main.sql',
    output_file="result.sql",
    variables={"version": "2.0.0"},
    extensions={"sqlplus": True}
)
```

## Best Practices

### Security Considerations

- Use the `sql_escape` filter for dynamic content
- Validate input variables before processing
- Review generated SQL before execution

### Performance

- Use specific file paths to avoid unnecessary scanning
- Enable verbose mode only for debugging
- Consider processing order for optimal performance

### Organization

- Keep templates and variables in separate files
- Use meaningful variable names
- Document complex template logic

## Testing

Run the test suite:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=MergeSourceFile --cov-report=html
```

### Operating Systems

- ✅ **Windows**: Full support
- ✅ **Linux**: Full support  
- ✅ **macOS**: Full support

## Development

```bash
# Clone repository
git clone https://github.com/alegorico/MergeSourceFile.git
cd MergeSourceFile

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest
```

## Documentation

- [Configuration Guide](https://github.com/alegorico/MergeSourceFile/blob/main/CONFIGURATION.md) - Complete TOML reference
- [Usage Examples](https://github.com/alegorico/MergeSourceFile/blob/main/EXAMPLES.md) - Practical use cases
- [Changelog](https://github.com/alegorico/MergeSourceFile/blob/main/CHANGELOG.md) - Version history

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run the test suite: `pytest`
5. Submit a pull request

Please ensure your code follows the project's coding standards and includes appropriate tests.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/alegorico/MergeSourceFile/blob/main/LICENSE) file for details.

## Author

Created and maintained by [alegorico](https://github.com/alegorico).