# MergeSourceFile - Practical Examples

This document provides practical examples of using MergeSourceFile v2.0.0 with the new plugin-based architecture, hierarchical configuration format, and flexible processing pipelines.

## 🆕 Configuration-Only Workflow (v2.0.0)

MergeSourceFile v2.0.0 uses a **configuration-only interface** with a new hierarchical format. All settings are specified in a `MKFSource.toml` file in your project directory.

### Example 1: Basic Configuration

**MKFSource.toml**:
```toml
[project]
input = "main.sql"
output = "merged.sql"

[plugins.sqlplus]
enabled = true
```

**Command**:
```bash
mergesourcefile
```

That's it! The tool automatically reads from `MKFSource.toml`.

### Example 2: Configuration with Jinja2

**MKFSource.toml**:
```toml
[project]
input = "template.sql"
output = "generated.sql"
verbose = true
execution_order = ["jinja2", "sqlplus_includes", "sqlplus_vars"]

[plugins.jinja2]
enabled = true
variables_file = "production_vars.json"
```

**production_vars.json**:
```json
{
  "environment": "production",
  "database": "PROD_DB",
  "schema": "APP_SCHEMA",
  "table_prefix": "PROD"
}
```

**template.sql**:
```sql
-- Generated for {{ environment | upper }} environment
-- Database: {{ database }}

{% if environment == 'production' %}
@production_settings.sql
{% else %}
@development_settings.sql
{% endif %}

DEFINE schema={{ schema }};
DEFINE prefix={{ table_prefix }};

CREATE TABLE &prefix._USERS (
    id NUMBER PRIMARY KEY,
    environment VARCHAR2(50) DEFAULT '{{ environment }}'
);
```

**Command**:
```bash
mergesourcefile
```

### Example 3: Multiple Environment Configurations

Create different TOML files for each environment and copy the appropriate one:

**MKFSource.dev.toml**:
```toml
[project]
input = "app.sql"
output = "app_dev.sql"
verbose = true
execution_order = ["sqlplus_includes", "jinja2", "sqlplus_vars"]

[plugins.jinja2]
enabled = true
variables_file = "dev_vars.json"
```

**MKFSource.prod.toml**:
```toml
[project]
input = "app.sql"
output = "app_prod.sql"
verbose = false
execution_order = ["sqlplus_includes", "jinja2", "sqlplus_vars"]

[plugins.jinja2]
enabled = true
variables_file = "prod_vars.json"
```

**Usage**:
```bash
# For development
cp MKFSource.dev.toml MKFSource.toml
mergesourcefile

# For production
cp MKFSource.prod.toml MKFSource.toml
mergesourcefile
```

### Example 4: Skip Variable Processing

When you only want to resolve file inclusions without processing DEFINE variables:

**MKFSource.toml**:
```toml
[project]
input = "includes.sql"
output = "merged_includes.sql"

[plugins.sqlplus]
enabled = true
skip_var = true
```

**Command**:
```bash
mergesourcefile
```

### Example 5: Debugging with Verbose Mode

**MKFSource.toml**:
```toml
[project]
input = "debug.sql"
output = "debug_output.sql"
verbose = true

[plugins.sqlplus]
enabled = true
skip_var = false
```

**Command**:
```bash
mergesourcefile
```

This will show detailed information about:
- Which files are being included
- Which variables are being defined
- Which variables are being replaced and where

## Processing Pipeline Examples

### Example 6: Jinja2 First (Template-Driven Includes)

Use when Jinja2 templates determine which files to include:

**MKFSource.toml**:
```toml
[project]
input = "main.sql"
output = "output.sql"
execution_order = ["jinja2", "sqlplus_includes", "sqlplus_vars"]

[plugins.jinja2]
enabled = true
variables_file = "config.json"
```

**main.sql**:
```sql
-- Jinja2 processes first, determines which file to include
{% if environment == 'production' %}
@production_config.sql
{% else %}
@development_config.sql
{% endif %}
```

### Example 7: Variables First

Use when SQL variables should affect Jinja2 templates:

**MKFSource.toml**:
```toml
[project]
input = "main.sql"
output = "output.sql"

[plugins.sqlplus]
enabled = true

[plugins.jinja2]
enabled = true
variables_file = "vars.json"

# execution_order moved to [project] section: execution_order = ["sqlplus_vars", "jinja2", "sqlplus_includes"]
```

## Enhanced DEFINE Syntax Support

### Example 8: Improved DEFINE Statement Support

**input.sql**:
```sql
-- ✅ All of these now work correctly
DEFINE schema_name = PRODUCTION;
DEFINE table_prefix = TBL;
DEFINE version_num = 2;

-- ✅ Enhanced support for complex values
DEFINE decimal_value = 3.14;
DEFINE hyphenated_code = ABC-123-XYZ;
DEFINE complex_identifier = DB2_TABLE_V2_FINAL;
DEFINE empty_string = '';

-- ✅ Quoted values still work as before
DEFINE schema_desc = 'Production Database';
DEFINE full_path = '/opt/oracle/data files/prod.dbf';

-- Using the variables
CREATE TABLESPACE &schema_name._DATA
DATAFILE '&full_path'
SIZE &decimal_value.G;

CREATE TABLE &table_prefix._USERS_&version_num (
    id NUMBER,
    code VARCHAR2(50) DEFAULT '&hyphenated_code'
);
```

**MKFSource.toml**:
```toml
[project]
input = "input.sql"
output = "output.sql"

[plugins.sqlplus]
enabled = true
```

### Example 9: Enhanced Error Reporting with Verbose Mode

**Input with some invalid DEFINE statements**:
```sql
-- Valid DEFINE statements
DEFINE good_var = value123;
DEFINE quoted_var = 'spaced value';

-- Invalid DEFINE statements (will be ignored)
DEFINE bad_var = ;
DEFINE = no_name_here;
DEFINE another_bad =;

-- Using the valid variables
SELECT '&good_var', '&quoted_var' FROM dual;
```

**MKFSource.toml**:
```toml
[project]
input = "mixed_defines.sql"
output = "output.sql"
verbose = true

[plugins.sqlplus]
enabled = true
```

**Expected verbose output**:
```
Arbol de inclusiones:
|-- mixed_defines.sql
[VERBOSE] Definiendo variable: good_var = value123
[VERBOSE] Definiendo variable: quoted_var = spaced value
[VERBOSE] Ignorando DEFINE con sintaxis invalida en linea 6: 'DEFINE bad_var = ;'
[VERBOSE] Ignorando DEFINE con sintaxis invalida en linea 7: 'DEFINE = no_name_here;'
[VERBOSE] Ignorando DEFINE con sintaxis invalida en linea 8: 'DEFINE another_bad =;'
[VERBOSE] Reemplazando variable good_var con valor value123 en la linea 11
[VERBOSE] Reemplazando variable quoted_var con valor spaced value en la linea 11

Resumen de sustituciones:
good_var	1
quoted_var	1
```

### Example 10: ⚠️ Common Pitfall: Spaces in Unquoted Values

**DANGEROUS Example - This WILL FAIL**:
```sql
-- Input file with risky syntax
DEFINE schema_name = {{ schema_name }};        -- ❌ NO quotes
DEFINE table_space = {{ table_space }};       -- ❌ NO quotes  
DEFINE max_conn = {{ max_connections }};      -- ✅ OK (number)

CREATE TABLESPACE &table_space;
```

**JSON with spaces**:
```json
{
  "schema_name": "MY PROD SCHEMA",
  "table_space": "PROD DATA TS", 
  "max_connections": 200
}
```

**MKFSource.toml**:
```toml
[project]
input = "dangerous.sql"
output = "output.sql"
execution_order = ["jinja2", "sqlplus_includes", "sqlplus_vars"]

[plugins.jinja2]
enabled = true
variables_file = "vars.json"
```

**Resulting output (BROKEN SQL*Plus syntax)**:
```sql
-- ❌ THESE LINES WILL CAUSE SQL*PLUS ERRORS:
DEFINE schema_name = MY PROD SCHEMA;           -- ❌ Invalid: missing quotes around spaced value
DEFINE table_space = PROD DATA TS;            -- ❌ Invalid: missing quotes around spaced value
DEFINE max_conn = 200;                        -- ✅ Valid: number without spaces

CREATE TABLESPACE PROD DATA TS;               -- ❌ This will fail in SQL*Plus!
```

**FIXED Version (using quotes)**:
```sql
-- Input file with safe syntax
DEFINE schema_name = '{{ schema_name }}';      -- ✅ With quotes
DEFINE table_space = '{{ table_space }}';     -- ✅ With quotes
DEFINE max_conn = {{ max_connections }};      -- ✅ OK (number)

CREATE TABLESPACE &table_space;
```

**Resulting output (CORRECT SQL*Plus syntax)**:
```sql
-- ✅ THESE LINES ARE VALID SQL*PLUS:
DEFINE schema_name = 'MY PROD SCHEMA';         -- ✅ Valid: quoted value with spaces
DEFINE table_space = 'PROD DATA TS';          -- ✅ Valid: quoted value with spaces  
DEFINE max_conn = 200;                        -- ✅ Valid: number without quotes

CREATE TABLESPACE PROD DATA TS;               -- ✅ This works correctly!
```

## Jinja2 Integration Examples

### Example 11: Simple Variable Substitution

**⚠️ Important: Quoted vs Unquoted Jinja2 Variables in DEFINE**

```sql
-- ✅ CORRECT: Use quotes when Jinja2 variable might contain spaces or special characters
DEFINE schema_name = '{{ schema_name }}';     -- Results in: DEFINE schema_name = 'PROD_SCHEMA';
DEFINE table_space = '{{ table_space }}';     -- Results in: DEFINE table_space = 'PROD_TS';
DEFINE file_path = '{{ base_path }}/data';    -- Results in: DEFINE file_path = '/opt/oracle data/data';

-- ✅ CORRECT: No quotes when Jinja2 variable contains simple numeric values
DEFINE max_connections = {{ max_connections }}; -- Results in: DEFINE max_connections = 100;
DEFINE timeout_seconds = {{ timeout }};         -- Results in: DEFINE timeout_seconds = 30;

-- ⚠️ RISKY: No quotes with string variables - ONLY if you're 100% sure no spaces
DEFINE schema_prefix = {{ prefix }};          -- OK if prefix = "PROD" (no spaces)
                                             -- FAILS if prefix = "PROD SCHEMA" (has spaces)

-- ❌ DANGEROUS: This WILL FAIL with spaces or special characters
DEFINE schema_name = {{ schema_name }};       -- Results in: DEFINE schema_name = PROD SCHEMA; 
                                             -- ❌ SQL*Plus syntax error!

-- 💡 SAFE ALTERNATIVE: Always use quotes for strings to avoid syntax errors
DEFINE max_connections = '{{ max_connections }}'; -- Results in: DEFINE max_connections = '100'; 
                                                  -- ✅ Works but treats number as string
```

**🔥 Critical Rule: When in doubt, use quotes! They prevent SQL*Plus syntax errors.**

**config.sql**:
```sql
-- Database configuration for {{ environment }}
DEFINE schema_name = '{{ schema_name }}';      -- String value needs quotes
DEFINE table_space = '{{ table_space }}';      -- String value needs quotes
DEFINE max_connections = {{ max_connections }}; -- Numeric value, no quotes
DEFINE timeout_seconds = {{ timeout }};        -- Numeric value, no quotes

CREATE TABLESPACE &table_space
DATAFILE '{{ data_file_path }}' 
SIZE {{ initial_size }};

ALTER SYSTEM SET sessions = &max_connections;
ALTER SYSTEM SET sql_trace_wait_time = &timeout_seconds;
```

**vars.json**:
```json
{
  "environment": "production",
  "schema_name": "PROD_SCHEMA",
  "table_space": "PROD_TS",
  "max_connections": 200,
  "timeout": 60,
  "data_file_path": "/opt/oracle/data/prod.dbf",
  "initial_size": "1G"
}
```

**MKFSource.toml**:
```toml
[project]
input = "config.sql"
output = "output.sql"
execution_order = ["jinja2", "sqlplus_includes", "sqlplus_vars"]

[plugins.jinja2]
enabled = true
variables_file = "vars.json"
```

**Expected output**:
```sql
-- Database configuration for production
DEFINE schema_name = 'PROD_SCHEMA';
DEFINE table_space = 'PROD_TS';
DEFINE max_connections = 200;
DEFINE timeout_seconds = 60;

CREATE TABLESPACE PROD_TS
DATAFILE '/opt/oracle/data/prod.dbf' 
SIZE 1G;

ALTER SYSTEM SET sessions = 200;
ALTER SYSTEM SET sql_trace_wait_time = 60;
```

### Example 12: Conditional Logic

**deploy.sql**:
```sql
-- Deployment script for {{ environment }}
{% if environment == 'production' %}
-- Production-specific settings
ALTER SYSTEM SET sga_target = 2G;
ALTER SYSTEM SET pga_aggregate_target = 1G;
{% else %}
-- Development/Test settings
ALTER SYSTEM SET sga_target = 512M;
ALTER SYSTEM SET pga_aggregate_target = 256M;
{% endif %}

{% if backup_enabled %}
-- Enable backup
ALTER DATABASE ARCHIVELOG;
{% endif %}
```

**environment.json**:
```json
{
  "environment": "production",
  "backup_enabled": true
}
```

**MKFSource.toml**:
```toml
[project]
input = "deploy.sql"
output = "output.sql"
execution_order = ["jinja2", "sqlplus_includes", "sqlplus_vars"]

[plugins.jinja2]
enabled = true
variables_file = "environment.json"
```

### Example 13: Loops for Repetitive Structures

**create_tables.sql**:
```sql
-- Create multiple tables
{% for table in tables %}
CREATE TABLE {{ table.name }} (
    id NUMBER PRIMARY KEY,
    {% for column in table.columns -%}
    {{ column.name }} {{ column.type }}{% if column.nullable %} NULL{% else %} NOT NULL{% endif %}{% if not loop.last %},{% endif %}
    {% endfor %}
);

CREATE INDEX idx_{{ table.name }}_id ON {{ table.name }}(id);
{% if table.audit %}
-- Audit table for {{ table.name }}
CREATE TABLE {{ table.name }}_audit AS SELECT * FROM {{ table.name }} WHERE 1=0;
{% endif %}

{% endfor %}
```

**tables.json**:
```json
{
  "tables": [
    {
      "name": "users",
      "audit": true,
      "columns": [
        {"name": "username", "type": "VARCHAR2(50)", "nullable": false},
        {"name": "email", "type": "VARCHAR2(100)", "nullable": false},
        {"name": "created_date", "type": "DATE", "nullable": true}
      ]
    },
    {
      "name": "products",
      "audit": false,
      "columns": [
        {"name": "title", "type": "VARCHAR2(200)", "nullable": false},
        {"name": "price", "type": "NUMBER(10,2)", "nullable": false}
      ]
    }
  ]
}
```

**MKFSource.toml**:
```toml
[project]
input = "create_tables.sql"
output = "output.sql"
execution_order = ["jinja2", "sqlplus_includes", "sqlplus_vars"]

[plugins.jinja2]
enabled = true
variables_file = "tables.json"
```

## Advanced Examples

### Example 14: Dynamic File Inclusion

**main.sql**:
```sql
-- Main deployment script
-- Generated on {{ now() | strftime('%Y-%m-%d %H:%M:%S') }}

{# Include environment-specific configuration #}
{% if environment == 'production' %}
@config/prod_config.sql
@config/prod_security.sql
{% elif environment == 'staging' %}
@config/staging_config.sql
{% else %}
@config/dev_config.sql
{% endif %}

{# Include feature-specific scripts based on enabled features #}
{% for feature in enabled_features %}
@features/{{ feature }}.sql
{% endfor %}

-- Common scripts
@common/create_base_tables.sql
@common/insert_reference_data.sql
```

**environment.json**:
```json
{
  "environment": "production",
  "enabled_features": ["audit", "reporting", "notifications"]
}
```

**MKFSource.toml (using jinja2_first order)**:
```toml
[project]
input = "main.sql"
output = "output.sql"
execution_order = ["jinja2", "sqlplus_includes", "sqlplus_vars"]

[plugins.jinja2]
enabled = true
variables_file = "environment.json"
```

### Example 15: SQL Injection Protection

**data_script.sql**:
```sql
-- Insert user data with proper escaping
{% for user in users %}
INSERT INTO users (username, email, full_name, bio) 
VALUES (
    '{{ user.username | sql_escape }}',
    '{{ user.email | sql_escape }}',
    '{{ user.full_name | sql_escape }}',
    '{{ user.bio | sql_escape }}'
);
{% endfor %}

-- Update statement with user input
UPDATE users 
SET last_login = SYSDATE,
    notes = '{{ user_notes | sql_escape }}'
WHERE username = '{{ current_user | sql_escape }}';
```

**users.json**:
```json
{
  "users": [
    {
      "username": "john_doe",
      "email": "john@example.com",
      "full_name": "John O'Brien",
      "bio": "Software developer who loves 'coding' and databases"
    }
  ],
  "current_user": "admin",
  "user_notes": "User said: 'Everything looks good!'"
}
```

**MKFSource.toml**:
```toml
[project]
input = "data_script.sql"
output = "output.sql"
execution_order = ["jinja2", "sqlplus_includes", "sqlplus_vars"]

[plugins.jinja2]
enabled = true
variables_file = "users.json"
```

### Example 16: Date Formatting

**audit_script.sql**:
```sql
-- Audit script generated on {{ now() | strftime('%A, %B %d, %Y at %I:%M %p') }}

CREATE TABLE audit_log_{{ now() | strftime('%Y%m%d') }} (
    id NUMBER PRIMARY KEY,
    action_date DATE DEFAULT SYSDATE,
    action_type VARCHAR2(50),
    description CLOB
);

-- Archive old data (older than {{ cutoff_date | strftime('%Y-%m-%d') }})
INSERT INTO archive_table 
SELECT * FROM main_table 
WHERE created_date < DATE '{{ cutoff_date | strftime('%Y-%m-%d') }}';
```

**audit_config.json**:
```json
{
  "cutoff_date": "2024-01-01"
}
```

**MKFSource.toml**:
```toml
[project]
input = "audit_script.sql"
output = "output.sql"
execution_order = ["jinja2", "sqlplus_includes", "sqlplus_vars"]

[plugins.jinja2]
enabled = true
variables_file = "audit_config.json"
```

### Example 17: Complex Processing Order

**complex.sql**:
```sql
-- Complex script demonstrating processing order

DEFINE base_schema = 'MYAPP';

{# Jinja2 will determine which config to include #}
{% if environment == 'production' %}
@@ prod_includes.sql
{% else %}
@@ dev_includes.sql
{% endif %}

-- Using both SQL and Jinja2 variables
CREATE VIEW &base_schema..user_summary_{{ environment }} AS
SELECT 
    user_id,
    username,
    '{{ report_title }}' as report_title,
    '&base_schema' as schema_name
FROM &base_schema..users;
```

**complex_vars.json**:
```json
{
  "environment": "prod",
  "report_title": "Production Report"
}
```

**Different processing orders**:

**MKFSource_default.toml** (Default order: Includes → Jinja2 → SQL):
```toml
[project]
input = "complex.sql"
output = "output1.sql"
execution_order = ["sqlplus_includes", "jinja2", "sqlplus_vars"]

[plugins.jinja2]
enabled = true
variables_file = "complex_vars.json"
```

**MKFSource_jinja2_first.toml** (Jinja2 first - enables dynamic includes):
```toml
[project]
input = "complex.sql"
output = "output2.sql"
execution_order = ["jinja2", "sqlplus_includes", "sqlplus_vars"]

[plugins.jinja2]
enabled = true
variables_file = "complex_vars.json"
```

**MKFSource_includes_last.toml** (Includes last):
```toml
[project]
input = "complex.sql"
output = "output3.sql"
execution_order = ["sqlplus_vars", "jinja2", "sqlplus_includes"]

[plugins.jinja2]
enabled = true
variables_file = "complex_vars.json"
```

## Best Practices

1. **DEFINE with Jinja2 Variables - Quote Management (CRITICAL)**:
   ```sql
   -- 🛡️ SAFE: Always use quotes for string values (prevents syntax errors)
   DEFINE schema_name = '{{ schema_name }}';      -- Safe for "PROD", "PROD SCHEMA", "PROD-2"
   DEFINE file_path = '{{ data_directory }}/{{ filename }}';  -- Safe for paths with spaces
   DEFINE description = '{{ user_description }}'; -- Safe for any user input
   
   -- ⚡ PERFORMANCE: No quotes only for pure numeric values
   DEFINE max_users = {{ user_limit }};           -- OK only if user_limit = 200 (pure number)
   DEFINE buffer_size = {{ memory_mb }};          -- OK only if memory_mb = 1024 (pure number)
   
   -- ⚠️ RISKY: No quotes with variables that MIGHT contain spaces
   DEFINE prefix = {{ env_prefix }};              -- DANGEROUS! Fails if env_prefix = "DEV TEST"
   
   -- 🔥 CRITICAL ERROR EXAMPLE:
   -- JSON: {"schema": "MY PROD SCHEMA"}
   DEFINE schema = {{ schema }};                  -- Results in: DEFINE schema = MY PROD SCHEMA;
                                                  -- ❌ SQL*Plus ERROR: Invalid syntax!
   
   -- ✅ CORRECT VERSION:
   DEFINE schema = '{{ schema }}';                -- Results in: DEFINE schema = 'MY PROD SCHEMA';
                                                  -- ✅ Valid SQL*Plus syntax
   ```

   **💡 Golden Rule**: Use quotes unless you're 100% certain the variable contains only:
   - Pure numbers (100, 3.14, -50)
   - Simple identifiers without spaces (PROD, TEST, V2)

2. **Use Verbose Mode for Debugging**:
   ```toml
   [project]
   input = "script.sql"
   output = "output.sql"
   verbose = true  # Enable detailed logging
   ```

3. **Separate Concerns with Processing Order**:
   - Use `["jinja2", "sqlplus_includes", "sqlplus_vars"]` when Jinja2 determines which files to include
   - Use `["sqlplus_includes", "jinja2", "sqlplus_vars"]` (default) for most cases
   - Use `["sqlplus_vars", "jinja2", "sqlplus_includes"]` when SQL variables affect Jinja2 templates

4. **Always Use SQL Escape Filter for User Input**:
   ```sql
   INSERT INTO users (name, comment) 
   VALUES ('{{ user.name | sql_escape }}', '{{ user.comment | sql_escape }}');
   ```

5. **Test Processing Orders**:
   - Create different MKFSource configurations for testing
   - Understand how plugin order affects the final output

## Migration Examples

### Migrating from CLI to Configuration File (v2.0.0)

**Old approach (v1.x - NO LONGER WORKS)**:
```bash
mergesourcefile -i existing.sql -o output.sql
```

**New approach (v2.0.0)**:
```toml
# MKFSource.toml
[project]
input = "existing.sql"
output = "output.sql"

[plugins.sqlplus]
enabled = true
```

Then run:
```bash
mergesourcefile
```

### Adding Jinja2 to Existing Project

**Before (v1.x - NO LONGER WORKS)**:
```bash
mergesourcefile -i existing.sql -o output.sql --jinja2
```

**After (v2.0.0)**:
```toml
# MKFSource.toml
[project]
input = "enhanced.sql"
output = "output.sql"
execution_order = ["jinja2", "sqlplus_includes", "sqlplus_vars"]

[plugins.jinja2]
enabled = true
variables_file = "vars.json"
```

## Summary

MergeSourceFile v2.0.0 provides a powerful, flexible, plugin-based system for processing SQL*Plus scripts with template support. The new hierarchical configuration format makes it easy to:

- Process SQL*Plus scripts with file inclusions
- Apply Jinja2 templates with custom filters
- Manage variables with DEFINE/UNDEFINE
- Configure processing order for different workflows
- Separate concerns between plugins
- Version control your build configurations
- Share configurations across teams

For more information:
- **Configuration Reference**: See `CONFIGURATION.md`
- **Architecture Details**: See `ARCHITECTURE.md`
- **Change Log**: See `CHANGELOG.md`
- **Quick Start**: See `README.md`

2. **Safe JSON Variable Design**:
   ```json
   {
     "schema_name": "PROD_SCHEMA",           // ✅ Use quotes in DEFINE (no spaces)
     "schema_desc": "Production Database",   // ✅ MUST use quotes (has spaces)
     "max_connections": 200,                 // ✅ Can skip quotes (pure number)
     "timeout_seconds": 30,                  // ✅ Can skip quotes (pure number)  
     "environment": "production",            // ✅ Use quotes (string)
     "data_path": "/opt/oracle data/files"   // ✅ MUST use quotes (has spaces)
   }
   ```

2. **Use `sql_escape` filter** for any dynamic content that might contain single quotes:
   ```sql
   DEFINE user_comment = '{{ user_input | sql_escape }}';
   ```

3. **Choose the right processing order** based on your use case:
   - `default`: Most common scenarios
   - `jinja2_first`: When you need dynamic file inclusion
   - `includes_last`: When SQL variables need to be processed before templates

4. **Use Jinja2 comments** `{# ... #}` for template-specific documentation

5. **Validate your JSON** before passing it to `--jinja2-vars`

6. **Use `--verbose`** flag when debugging template issues

7. **Test your variable types**:
   ```json
   {
     "schema_name": "PROD_SCHEMA",           // String - use quotes in DEFINE
     "max_connections": 200,                 // Number - no quotes in DEFINE  
     "timeout_seconds": 30,                  // Number - no quotes in DEFINE
     "debug_enabled": true,                  // Boolean - no quotes if using true/false
     "environment": "production"             // String - use quotes in DEFINE
   }
   ```

## Integration with Existing Scripts

All existing MergeSourceFile scripts work without changes. You can gradually add Jinja2 features:

```bash
# Phase 1: Existing script (no changes needed)
mergesourcefile -i existing.sql -o output.sql

# Phase 2: Add Jinja2 processing (optional)
mergesourcefile -i existing.sql -o output.sql --jinja2

# Phase 3: Add Jinja2 variables and logic
mergesourcefile -i enhanced.sql -o output.sql --jinja2 --jinja2-vars '{"env": "prod"}'
```