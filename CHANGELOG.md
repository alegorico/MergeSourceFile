# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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