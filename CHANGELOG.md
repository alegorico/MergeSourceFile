# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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