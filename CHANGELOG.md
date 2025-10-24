# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.1] - 2025-10-24

### 🎯 Conflict Resolution: Include Systems & Variable Namespaces

This version addresses **critical conflicts** between SQLPlus and Jinja2 systems, implementing comprehensive resolution mechanisms for both includes and variables.

### Added

- **🚦 Automatic Include System Exclusion**
  - Implemented smart conflict resolution between `@file` (SQLPlus) and `{% include %}` (Jinja2)
  - When `process_includes = true`: SQLPlus includes ✅ active, Jinja2 includes ❌ disabled
  - When `process_includes = false`: SQLPlus includes ❌ disabled, Jinja2 includes ✅ active
  - Custom `NoIncludeLoader` class that blocks Jinja2 includes when SQLPlus handles them

- **🏷️ Variable Namespace Separation System**
  - **Forced namespace separation** for DEFINE variables with `sql_` prefix
  - SQLPlus `DEFINE var=value` → Jinja2 `{{ sql_var }}`
  - Automatic extraction of DEFINE variables to Jinja2 context
  - **Warning system** for variable name conflicts between SQLPlus and Jinja2
  - Non-configurable namespace to ensure consistency across projects

- **🔧 Enhanced Template Engine**
  - Modified `TemplateEngine._render_template()` to automatically select appropriate loader
  - Added `FileSystemLoader` support for proper Jinja2 include resolution
  - Intelligent loader selection based on extension configuration
  - Clear error messages when using wrong include system
  - Enhanced `process_sqlplus()` function with integrated variable extraction

- **📋 Comprehensive Testing**
  - New test suite: `tests/test_include_conflict.py` (4 tests)
  - New test suite: `tests/test_variable_namespace.py` (5 tests)
  - Complete coverage of conflict resolution scenarios
  - Tests verify exclusion logic works correctly in all scenarios
  - Validates error messages are clear and helpful

- **📚 Updated Documentation**
  - Enhanced `CONFIGURATION.md` with include system behavior section
  - Updated `README.md` with conflict resolution information
  - New `EXAMPLES.md` sections for include system management and migration
  - Added `INCLUDE_CONFLICT_RESOLUTION.md` technical guide

### Changed

- **🔄 Configuration Parameter Updates**
  - `resolve_includes` renamed to `process_includes` (more accurate naming)
  - `resolve_variables` renamed to `process_defines` (matches SQLPlus terminology)
  - Updated all documentation and examples to reflect new parameter names

### Fixed

- **🐛 Include System Conflicts**
  - Eliminated ambiguity between SQLPlus `@file` and Jinja2 `{% include %}` systems
  - Prevented potential file processing conflicts and unexpected behavior
  - Ensured only one include system is active at any time

### Technical Details

- Added `NoIncludeLoader` class that raises descriptive errors for blocked includes
- Modified `_render_template()` method with loader selection logic
- Updated import statements to include `FileSystemLoader`
- Enhanced error messages with actionable guidance for users

### Migration Guide

**Old behavior**: Both include systems could potentially conflict
**New behavior**: Automatic exclusion prevents conflicts

No breaking changes to existing configurations - upgrade is seamless.

---

## [2.0.0] - 2025-10-24

### 🎯 Major Architectural Redesign

Version 2.0.0 represents a **complete architectural overhaul** focused on **simplicity and clarity**. The previous plugin system was over-engineered for the actual use case. This version embraces a **Jinja2-centric architecture** with optional extensions.

### Added

- **✨ Jinja2-Centric Architecture**
  - `TemplateEngine` class as the core component (always active)
  - Jinja2 recognized as the essential functionality, not "one more plugin"
  - Clean, focused design that embraces Python's scripting strengths
  - Function-based extension system instead of complex plugin infrastructure

- **🔧 Extension System**
  - Simple extension interface using pure functions (not classes)
  - `extensions/sqlplus.py`: SQLPlus compatibility extension
  - Extensions are optional preprocessors, not interchangeable plugins
  - No plugin discovery, no dynamic loading, no registry overhead

- **📝 New Configuration Structure**
  - `[jinja2]` section: Core template engine settings
  - `[jinja2.extensions]` section: Enable/disable extensions
  - `[jinja2.extensions.sqlplus]`: SQLPlus extension configuration
  - Clearer hierarchy: Jinja2 is core, extensions extend it

- **✅ Enhanced Test Coverage**
  - **50 comprehensive tests** (down from 69, but more focused)
  - **92% code coverage** (up from 81%)
  - Test structure:
    - `test_config_loader.py` (12 tests) - Configuration management
    - `test_template_engine.py` (13 tests) - Core Jinja2 engine
    - `test_sqlplus_extension.py` (18 tests) - SQLPlus extension
    - `test_integration.py` (7 tests) - End-to-end workflows
  - Eliminated redundant tests and legacy compatibility tests

- **📚 Complete Documentation Rewrite**
  - `ARCHITECTURE.md`: New design philosophy and component documentation
  - `CONFIGURATION.md`: Complete TOML reference with examples
  - `README.md`: Updated with quick start and new examples
  - `EXAMPLES.md`: Rebuilt with practical use cases
  - All documentation reflects Jinja2-centric approach

### Changed

- **🏗️ Architectural Simplification**
  - **BREAKING CHANGE**: Removed entire plugin system infrastructure
  - From ~800 lines of plugin code to ~260 lines of focused functionality
  - Function-based design replaces class hierarchies
  - Fixed processing order: Extensions → Jinja2 (no more configurable pipeline)

- **Configuration Format**
  - **BREAKING CHANGE**: New hierarchical structure
  - `[project]` section unchanged (input_file, output_file, backup, verbose)
  - `[plugins.*]` sections → `[jinja2]` + `[jinja2.extensions.*]`
  - Parameter renames for clarity (see Migration Guide below)

- **Processing Model**
  - Simplified flow: Input → Extensions (optional) → Jinja2 (always) → Output
  - No more execution_order configuration (fixed: SQLPlus then Jinja2)
  - In-memory processing with clear data transformations
  - Better error messages with specific context

- **Code Quality**
  - 92% test coverage (up from 81%)
  - Eliminated 550+ lines of unused/over-engineered code
  - Better separation of concerns
  - More maintainable codebase

### Removed

- **🗑️ Plugin System Infrastructure** (BREAKING CHANGE)
  - `plugin_system.py` - ProcessorPlugin, PluginRegistry, ProcessorPipeline, ProcessingContext
  - `plugins/` directory - jinja2_plugin.py, sqlplus_plugin.py
  - `resource_io.py` - ResourceLoader functions
  - Legacy main implementations (_old_main.py, main_temp.py)

- **Configuration Options**
  - `execution_order` parameter (processing order now fixed)
  - `[plugins.sqlplus]` section (now `[jinja2.extensions.sqlplus]`)
  - `[plugins.jinja2]` section (now `[jinja2]`)

- **Python API Exports**
  - `ProcessorPlugin`, `PluginRegistry`, `ProcessorPipeline`, `ProcessingContext`
  - `get_available_plugins()` function
  - Resource loader functions

### Migration Guide from v1.x

#### Configuration Changes

**Old Format (v1.x - NO LONGER SUPPORTED)**:
```toml
[mergesourcefile]
input = "main.sql"
output = "output.sql"
jinja2 = true
jinja2_vars = "vars.json"
skip_var = false
processing_order = "default"
```

**New Format (v2.0.0 - REQUIRED)**:
```toml
[project]
input_file = "main.sql"        # Renamed from 'input'
output_file = "output.sql"     # Renamed from 'output'
backup = false
verbose = false

[jinja2]                       # New section (was [plugins.jinja2])
enabled = true
vars_file = "vars.json"        # Renamed from 'jinja2_vars'

[jinja2.extensions]            # New section
sqlplus = true                 # Enable SQLPlus extension

[jinja2.extensions.sqlplus]    # New section (was [plugins.sqlplus])
process_includes = true        # Process @/@@ directives
process_defines = true         # Process DEFINE/UNDEFINE (was 'skip_var = false')
```

#### Parameter Mapping

| v1.x | v2.0.0 | Notes |
|------|--------|-------|
| `[mergesourcefile]` | `[project]` | Section renamed |
| `input` | `input_file` | Parameter renamed |
| `output` | `output_file` | Parameter renamed |
| `jinja2` | `[jinja2]` section | Now a full section |
| `jinja2_vars` | `vars_file` | Parameter renamed and moved |
| `skip_var` | `process_defines` | Inverted logic! |
| `processing_order` | _(removed)_ | Processing order now fixed |
| `[plugins.sqlplus]` | `[jinja2.extensions.sqlplus]` | Section moved |
| `[plugins.jinja2]` | `[jinja2]` | Section renamed |

#### Code Changes

**Old API (v1.x - NO LONGER SUPPORTED)**:
```python
from MergeSourceFile import PluginRegistry, ProcessorPipeline, get_available_plugins

registry = PluginRegistry()
# ... plugin registration code
```

**New API (v2.0.0 - RECOMMENDED)**:
```python
from MergeSourceFile import TemplateEngine, load_config, main

# Use main function (simplest)
main('MKFSource.toml')

# Or use TemplateEngine directly
config = load_config('MKFSource.toml')
engine = TemplateEngine(config.get('jinja2', {}))
result = engine.process_file('template.sql', variables={})
```

#### Processing Order Changes

The processing order is now **fixed** and cannot be configured:

1. **SQLPlus Extension** (if enabled): Expands `@`/`@@` includes and processes `DEFINE` variables
2. **Jinja2 Core** (always): Renders Jinja2 templates with variables

**Old `processing_order` values** (v1.x):
- `"default"` → Now the only order available
- `"jinja2_first"` → No longer supported (order is fixed)
- `"includes_last"` → No longer supported (order is fixed)

#### What to Expect

**Functionality preserved:**
- ✅ All Jinja2 templating features work exactly the same
- ✅ SQLPlus `@`/`@@` includes work exactly the same
- ✅ `DEFINE`/`UNDEFINE` variables work exactly the same
- ✅ Custom Jinja2 filters (`sql_escape`, `strftime`) unchanged
- ✅ File backup functionality unchanged

**Behavior changes:**
- ⚠️ Processing order is now fixed (SQLPlus → Jinja2)
- ⚠️ Configuration file structure is different
- ⚠️ Python API has changed (if you use it programmatically)

### Why This Change?

**Problems with v1.x plugin architecture:**
1. Over-engineered for a simple use case
2. Jinja2 treated as "one more plugin" when it's actually essential
3. Complex infrastructure (registry, pipeline, context) for minimal benefit
4. Harder to maintain and understand

**Benefits of v2.0 architecture:**
1. **Simpler**: 550+ fewer lines of code
2. **Clearer**: Jinja2 is obviously the core
3. **More maintainable**: Functions over class hierarchies
4. **Better tested**: 92% coverage vs 81%
5. **True to Python**: Embraces scripting strengths, not over-engineering

## [1.4.0] - 2025-10-23

### Changed
- **🚀 Configuration-Only Interface**
  - **BREAKING CHANGE**: Removed all command-line parameters
  - Tool now exclusively reads from `MKFSource.toml` in the current directory
  - Simplified CLI: just run `mergesourcefile` with no arguments
  - Each build configuration has its own dedicated TOML file
  
- **Standard Configuration File Name**
  - Configuration file must be named `MKFSource.toml`
  - Located in the current working directory
  - Enables project-based workflow with version-controlled build configurations
  
- **Simplified Architecture**
  - Removed argparse dependency and all CLI argument handling
  - Cleaner, more focused codebase
  - Better separation of concerns

### Removed
- All command-line parameters (`--config`, `--input`, `--output`, `--verbose`, etc.)
- argparse dependency
- CustomArgumentParser class
- Deprecation warnings (no longer needed)

### Migration Guide
If upgrading from v1.3.0 or earlier:
1. Create a `MKFSource.toml` file in your project directory
2. Move your configuration from command-line arguments to the TOML file
3. Run `mergesourcefile` (no arguments)

Example migration:
```bash
# Old way (v1.3.0)
mergesourcefile --config myconfig.toml

# New way (v1.4.0)
# Create MKFSource.toml with your configuration
mergesourcefile
```

## [1.3.0] - 2025-10-23

### Changed
- **🚀 Python 3.11+ Required**
  - Updated minimum Python version from 3.8+ to 3.11+
  - Leverages native `tomllib` module for TOML support (no external dependencies)
  - Simplified codebase by removing conditional tomli/tomllib imports
  - Better performance and maintainability with native TOML support

- **Dependency Simplification**
  - Removed `tomli` dependency (no longer needed with Python 3.11+)
  - Cleaner dependency management with only `jinja2>=3.0.0` required
  - Reduced package size and installation complexity

- **Code Modernization**
  - Removed Python version compatibility code for TOML handling
  - Cleaner error handling without tomllib availability checks
  - Improved code readability and maintainability

### Removed
- Support for Python 3.8, 3.9, and 3.10
- `tomli` dependency and related compatibility code

## [1.2.0] - 2025-10-20

### Added
- **🚀 TOML Configuration Support**
  - New `--config/-c` parameter to load configuration from TOML files
  - Complete configuration via TOML eliminates need for command-line parameters
  - Supports all application options: input, output, skip_var, verbose, jinja2, jinja2_vars, processing_order
  - Automatic validation of required parameters (input/output)
  - Warning system when both TOML config and command-line parameters are provided
  - Compatible with Python 3.8-3.12 (via tomli dependency for <3.11, built-in tomllib for 3.11+)

- **Continuous Integration with CircleCI**
  - Complete CircleCI configuration for automated testing across Python 3.8-3.12 (discontinued in v1.3.0+)
  - Multi-version Python testing with coverage reporting
  - Automated codecov integration for coverage tracking
  - Matrix testing ensures compatibility across all supported Python versions

### Example TOML Configuration
```toml
[mergesourcefile]
input = "main.sql"
output = "merged.sql"
skip_var = false
verbose = true
jinja2 = true
jinja2_vars = "variables.json"
processing_order = "jinja2_first"
```

### Changed
- **Enhanced command-line interface**
  - Configuration precedence: TOML config overrides all command-line parameters
  - Improved error messages for missing required parameters
  - Better integration between TOML and command-line workflows

- **Build system improvements**
  - Updated setuptools compatibility to support both CI environments and local development
  - Improved pyproject.toml configuration for better PEP 621 compliance
  - Enhanced build dependencies management for consistent builds

### Fixed
- **CI/CD pipeline stability**
  - Resolved setuptools version conflicts between local and CI environments
  - Fixed license format compatibility issues with different setuptools versions
  - Improved build reliability and reproducibility
  - Enhanced error reporting during CI builds

## [1.1.1] - 2025-10-17

### Enhanced
- **Improved DEFINE syntax support**
  - Enhanced regex pattern to support decimal values (e.g., `DEFINE price = 3.14`)
  - Added support for hyphenated values (e.g., `DEFINE code = ABC-123`)
  - Extended support for complex alphanumeric values with special characters
  - Maintains full backward compatibility with existing quoted and unquoted syntax
  - Validates compliance with Oracle SQL*Plus DEFINE standards

- **Better error reporting for DEFINE statements**
  - Invalid DEFINE syntax now reported in verbose mode with line numbers
  - Clear distinction between ignored invalid DEFINE and successful definitions
  - Examples: `"Ignorando DEFINE con sintaxis invalida en linea 4: 'DEFINE var = ;'"`
  - Empty string values (`DEFINE var = '';`) now supported as valid
  - Better user feedback for troubleshooting problematic variable definitions

### Fixed
- **Critical bug fix**: DEFINE statements without quotes now process correctly
  - Previously: `DEFINE VAR = value` would fail with "variable used before defined" error
  - Now: Both `DEFINE VAR = value` and `DEFINE VAR = 'value'` work correctly
  - Affected real-world database deployment scripts

- **Windows compatibility improvements**
  - Fixed Unicode encoding issues causing CLI integration test failures on Windows
  - Replaced problematic Unicode characters (→, Á, └) with ASCII equivalents (-, A, |--)
  - Improved error codes: CLI now returns proper exit codes (1) for errors
  - Enhanced file path resolution for nested includes with correct base_path calculation
  - All 56 tests now pass successfully on Windows systems

### Testing
- **Comprehensive test coverage**
  - Added 17 new tests covering DEFINE syntax improvements and error reporting
  - Enhanced integration test suite with 6 CLI tests covering all major functionality
  - 100% test pass rate achieved (56/56 tests passing)
  - Full coverage of edge cases including space handling and Unicode compatibility

## [1.1.0] - 2024-10-17

### Added
- **Complete Jinja2 template support**
  - New CLI parameters: `--jinja2` / `-j` to enable Jinja2 processing
  - New parameter `--jinja2-vars` / `-jv` to specify JSON file with variables
  - Custom filters:
    - `sql_escape`: Escapes single quotes for SQL
    - `strftime`: Date formatting
  - Variable support: `{{ variable }}`
  - Conditional support: `{% if condition %}`
  - Loop support: `{% for item in list %}`
  - Complex nested structure support
  - Customizable delimiters
  - Strict mode for undefined variables

### Features
- **Perfect integration with existing functionality**
  - Jinja2 templates are processed BEFORE SQL variables
  - Maintains full compatibility with file inclusions (@, @@)
  - Works together with DEFINE/UNDEFINE variables
  - Cascading processing: Files → Jinja2 → SQL Variables

### Documentation
- 14 new comprehensive tests for Jinja2 functionality
- Integration tests between Jinja2 and existing functionality
- Advanced configuration tests
- Complete functional example with template files and variables

### Dependencies
- Added: `jinja2>=3.0.0`

### Compatibility
- ✅ **Maintains 100% backward compatibility**
- ✅ All existing functionality unchanged
- ✅ Existing users require no migration
- ✅ New functionality is opt-in (requires `--jinja2` flag)

## [1.0.0] - 2023-XX-XX

### Added
- SQL*Plus script processing
- File inclusion resolution with @ and @@
- Variable substitution with DEFINE/UNDEFINE
- Verbose mode for debugging
- Option to skip variable processing
- Complete command-line interface
- Comprehensive tests
- Complete documentation