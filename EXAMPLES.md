# MergeSourceFile - Usage Examples

This document provides practical examples for common MergeSourceFile use cases. All examples use the v2.0.0 Jinja2-centric architecture.

## Table of Contents

1. [Basic Jinja2 Templating](#1-basic-jinja2-templating)
2. [Environment-Specific Deployments](#2-environment-specific-deployments)
3. [SQLPlus Script Migration](#3-sqlplus-script-migration)
4. [Schema Generation from Metadata](#4-schema-generation-from-metadata)
5. [Complex Multi-File Projects](#5-complex-multi-file-projects)
6. [Database Migration Scripts](#6-database-migration-scripts)
7. [Conditional Feature Deployment](#7-conditional-feature-deployment)
8. [Template Reuse with Macros](#8-template-reuse-with-macros)

---

## 1. Basic Jinja2 Templating

**Use Case**: Simple variable substitution in SQL templates.

### Files

**template.sql**:
```sql
-- Application: {{ app_name }}
-- Version: {{ version }}
-- Environment: {{ environment }}

CREATE TABLE {{ schema }}.users (
    id NUMBER PRIMARY KEY,
    username VARCHAR2(50) NOT NULL,
    email VARCHAR2(100),
    created_date DATE DEFAULT SYSDATE,
    app_version VARCHAR2(20) DEFAULT '{{ version }}'
);

COMMENT ON TABLE {{ schema }}.users IS 'User accounts for {{ app_name }}';
```

**variables.json**:
```json
{
  "app_name": "MyApplication",
  "version": "2.0.0",
  "environment": "production",
  "schema": "APP_SCHEMA"
}
```

**MKFSource.toml**:
```toml
[project]
input_file = "template.sql"
output_file = "output.sql"

[jinja2]
enabled = true
vars_file = "variables.json"
```

### Run

```bash
mergesourcefile
```

### Output (output.sql)

```sql
-- Application: MyApplication
-- Version: 2.0.0
-- Environment: production

CREATE TABLE APP_SCHEMA.users (
    id NUMBER PRIMARY KEY,
    username VARCHAR2(50) NOT NULL,
    email VARCHAR2(100),
    created_date DATE DEFAULT SYSDATE,
    app_version VARCHAR2(20) DEFAULT '2.0.0'
);

COMMENT ON TABLE APP_SCHEMA.users IS 'User accounts for MyApplication';
```

---

## 2. Environment-Specific Deployments

**Use Case**: Generate different SQL for dev/test/prod environments.

### Files

**deploy.sql**:
```sql
-- Deployment Script
-- Environment: {{ env }}
-- Generated: {{ now|strftime('%Y-%m-%d %H:%M:%S') }}

-- Environment-specific database parameters
{% if env == "production" %}
ALTER SYSTEM SET sga_target = 8G;
ALTER SYSTEM SET pga_aggregate_target = 4G;
ALTER SYSTEM SET processes = 500;
{% elif env == "test" %}
ALTER SYSTEM SET sga_target = 4G;
ALTER SYSTEM SET pga_aggregate_target = 2G;
ALTER SYSTEM SET processes = 200;
{% else %}
ALTER SYSTEM SET sga_target = 2G;
ALTER SYSTEM SET pga_aggregate_target = 1G;
ALTER SYSTEM SET processes = 100;
{% endif %}

-- Create tablespace with environment-specific settings
CREATE TABLESPACE {{ tablespace_name }}
  DATAFILE '{{ datafile_path }}' 
  SIZE {{ datafile_size }}
  AUTOEXTEND ON
  {% if env == "production" %}
  NEXT 1G MAXSIZE UNLIMITED
  {% else %}
  NEXT 100M MAXSIZE 10G
  {% endif %}
  EXTENT MANAGEMENT LOCAL;

-- Grant privileges
{% if env == "production" %}
-- Production: Read-only for app_reader role
GRANT SELECT ON {{ schema }}.* TO app_reader;
{% else %}
-- Non-production: Full access for developers
GRANT ALL ON {{ schema }}.* TO developers;
{% endif %}
```

**prod.json**:
```json
{
  "env": "production",
  "tablespace_name": "PROD_DATA",
  "datafile_path": "/oradata/prod/data01.dbf",
  "datafile_size": "50G",
  "schema": "PROD_SCHEMA",
  "now": "2025-10-24 10:30:00"
}
```

**dev.json**:
```json
{
  "env": "development",
  "tablespace_name": "DEV_DATA",
  "datafile_path": "/oradata/dev/data01.dbf",
  "datafile_size": "5G",
  "schema": "DEV_SCHEMA",
  "now": "2025-10-24 10:30:00"
}
```

**MKFSource.toml**:
```toml
[project]
input_file = "deploy.sql"
output_file = "deploy_output.sql"
backup = true

[jinja2]
enabled = true
vars_file = "prod.json"  # Change to dev.json for dev deployment
```

---

## 3. SQLPlus Script Migration

**Use Case**: Maintain legacy SQLPlus scripts while gradually migrating to Jinja2.

### Files

**legacy_script.sql**:
```sql
-- Legacy SQLPlus script with includes and DEFINE variables
PROMPT Loading common utilities...
@utils/common_settings.sql
@@local/db_params.sql

DEFINE schema='HR'
DEFINE version='2.0'
DEFINE table_prefix='EMP_'

PROMPT Creating tables with prefix: &table_prefix

CREATE TABLE &schema..&table_prefix.EMPLOYEES (
    id NUMBER PRIMARY KEY,
    name VARCHAR2(100),
    department VARCHAR2(50),
    version VARCHAR2(10) DEFAULT '&version'
);

CREATE TABLE &schema..&table_prefix.DEPARTMENTS (
    id NUMBER PRIMARY KEY,
    name VARCHAR2(100)
);

UNDEFINE schema
UNDEFINE version
UNDEFINE table_prefix
```

**utils/common_settings.sql**:
```sql
-- Common database settings
SET SERVEROUTPUT ON
SET LINESIZE 200
WHENEVER SQLERROR EXIT SQL.SQLCODE
```

**local/db_params.sql**:
```sql
-- Local database parameters (relative to parent file)
ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS';
```

**MKFSource.toml**:
```toml
[project]
input_file = "legacy_script.sql"
output_file = "merged_script.sql"
verbose = true

[jinja2]
enabled = true

[jinja2.extensions]
sqlplus = true

[jinja2.extensions.sqlplus]
process_includes = true
process_defines = true
```

### Output

All `@` includes will be expanded, and all `&variables` will be substituted inline.

---

## 4. Schema Generation from Metadata

**Use Case**: Generate database schema from JSON metadata.

### Files

**schema_template.sql**:
```sql
-- Database Schema Generator
-- Generated: {{ now|strftime('%Y-%m-%d') }}

{% for table in tables %}
-- ============================================================================
-- Table: {{ table.name }}
-- Description: {{ table.description }}
-- ============================================================================

CREATE TABLE {{ table.name }} (
    {% for column in table.columns %}
    {{ "%-30s"|format(column.name) }} {{ "%-20s"|format(column.type) }}
    {%- if column.primary_key %} PRIMARY KEY{% endif %}
    {%- if column.not_null and not column.primary_key %} NOT NULL{% endif %}
    {%- if column.unique %} UNIQUE{% endif %}
    {%- if column.default %} DEFAULT {{ column.default }}{% endif %}
    {%- if not loop.last %},{% endif %}
    {% endfor %}
);

{% if table.indexes %}
-- Indexes for {{ table.name }}
{% for index in table.indexes %}
CREATE {% if index.unique %}UNIQUE {% endif %}INDEX {{ index.name }} 
    ON {{ table.name }} ({{ index.columns|join(', ') }});
{% endfor %}
{% endif %}

{% if table.comment %}
COMMENT ON TABLE {{ table.name }} IS '{{ table.comment|sql_escape }}';
{% endif %}

{% endfor %}

-- ============================================================================
-- Foreign Keys
-- ============================================================================

{% for table in tables %}
{% if table.foreign_keys %}
{% for fk in table.foreign_keys %}
ALTER TABLE {{ table.name }}
    ADD CONSTRAINT {{ fk.name }}
    FOREIGN KEY ({{ fk.columns|join(', ') }})
    REFERENCES {{ fk.ref_table }}({{ fk.ref_columns|join(', ') }})
    {% if fk.on_delete %}ON DELETE {{ fk.on_delete }}{% endif %};
{% endfor %}
{% endif %}
{% endfor %}
```

**metadata.json**:
```json
{
  "now": "2025-10-24",
  "tables": [
    {
      "name": "users",
      "description": "Application users",
      "comment": "Stores user account information",
      "columns": [
        {
          "name": "id",
          "type": "NUMBER",
          "primary_key": true,
          "not_null": true
        },
        {
          "name": "username",
          "type": "VARCHAR2(50)",
          "not_null": true,
          "unique": true
        },
        {
          "name": "email",
          "type": "VARCHAR2(100)",
          "not_null": true
        },
        {
          "name": "created_date",
          "type": "DATE",
          "default": "SYSDATE"
        },
        {
          "name": "active",
          "type": "CHAR(1)",
          "default": "'Y'",
          "not_null": true
        }
      ],
      "indexes": [
        {
          "name": "idx_users_email",
          "columns": ["email"],
          "unique": true
        },
        {
          "name": "idx_users_created",
          "columns": ["created_date"],
          "unique": false
        }
      ],
      "foreign_keys": []
    },
    {
      "name": "orders",
      "description": "Customer orders",
      "comment": "Stores order information",
      "columns": [
        {
          "name": "id",
          "type": "NUMBER",
          "primary_key": true
        },
        {
          "name": "user_id",
          "type": "NUMBER",
          "not_null": true
        },
        {
          "name": "order_date",
          "type": "DATE",
          "default": "SYSDATE"
        },
        {
          "name": "total",
          "type": "NUMBER(10,2)",
          "not_null": true
        },
        {
          "name": "status",
          "type": "VARCHAR2(20)",
          "default": "'PENDING'"
        }
      ],
      "indexes": [
        {
          "name": "idx_orders_user",
          "columns": ["user_id"],
          "unique": false
        }
      ],
      "foreign_keys": [
        {
          "name": "fk_orders_user",
          "columns": ["user_id"],
          "ref_table": "users",
          "ref_columns": ["id"],
          "on_delete": "CASCADE"
        }
      ]
    }
  ]
}
```

**MKFSource.toml**:
```toml
[project]
input_file = "schema_template.sql"
output_file = "schema_generated.sql"

[jinja2]
enabled = true
vars_file = "metadata.json"
```

---

## 5. Complex Multi-File Projects

**Use Case**: Large project with multiple included files and shared variables.

### Project Structure

```
project/
├── MKFSource.toml
├── main.sql
├── variables.json
├── common/
│   ├── header.sql
│   └── footer.sql
├── ddl/
│   ├── tables.sql
│   └── indexes.sql
└── dml/
    ├── seed_data.sql
    └── test_data.sql
```

### Files

**main.sql**:
```sql
@common/header.sql

-- ============================================================================
-- DDL Section
-- ============================================================================

@ddl/tables.sql
@ddl/indexes.sql

-- ============================================================================
-- DML Section
-- ============================================================================

{% if include_seed_data %}
@dml/seed_data.sql
{% endif %}

{% if environment == "development" %}
@dml/test_data.sql
{% endif %}

@common/footer.sql
```

**common/header.sql**:
```sql
-- ============================================================================
-- Database Deployment Script
-- Project: {{ project_name }}
-- Version: {{ version }}
-- Environment: {{ environment }}
-- Generated: {{ now|strftime('%Y-%m-%d %H:%M:%S') }}
-- ============================================================================

SET ECHO OFF
SET SERVEROUTPUT ON
WHENEVER SQLERROR EXIT SQL.SQLCODE
```

**common/footer.sql**:
```sql
-- ============================================================================
-- Deployment Complete
-- ============================================================================

COMMIT;
EXIT;
```

**ddl/tables.sql**:
```sql
-- Tables for {{ project_name }}

CREATE TABLE {{ schema }}.users (
    id NUMBER PRIMARY KEY,
    username VARCHAR2(50) NOT NULL
);

CREATE TABLE {{ schema }}.logs (
    id NUMBER PRIMARY KEY,
    message VARCHAR2(4000),
    log_date DATE DEFAULT SYSDATE
);
```

**variables.json**:
```json
{
  "project_name": "MyApp",
  "version": "2.0.0",
  "environment": "development",
  "schema": "APP_DEV",
  "include_seed_data": true,
  "now": "2025-10-24 10:00:00"
}
```

**MKFSource.toml**:
```toml
[project]
input_file = "main.sql"
output_file = "deployment.sql"
backup = true
verbose = true

[jinja2]
enabled = true
vars_file = "variables.json"

[jinja2.extensions]
sqlplus = true

[jinja2.extensions.sqlplus]
process_includes = true
process_defines = false
```

---

## 6. Database Migration Scripts

**Use Case**: Version-controlled database migrations with rollback support.

### Files

**migration_v2_0_0.sql**:
```sql
-- Migration Script: v{{ from_version }} → v{{ to_version }}
-- Date: {{ now|strftime('%Y-%m-%d') }}

{% if migration_type == "upgrade" %}
-- ============================================================================
-- UPGRADE from {{ from_version }} to {{ to_version }}
-- ============================================================================

-- Step 1: Add new columns
{% for table, columns in new_columns.items() %}
{% for column in columns %}
ALTER TABLE {{ table }} ADD {{ column.name }} {{ column.type }}
{% if column.default %} DEFAULT {{ column.default }}{% endif %};
{% endfor %}
{% endfor %}

-- Step 2: Migrate data
{% for migration in data_migrations %}
UPDATE {{ migration.table }}
SET {{ migration.column }} = {{ migration.value }}
WHERE {{ migration.condition }};
{% endfor %}

-- Step 3: Create new tables
{% for table in new_tables %}
CREATE TABLE {{ table.name }} (
{% for col in table.columns %}
    {{ col.name }} {{ col.type }}{% if not loop.last %},{% endif %}
{% endfor %}
);
{% endfor %}

{% elif migration_type == "rollback" %}
-- ============================================================================
-- ROLLBACK from {{ to_version }} to {{ from_version }}
-- ============================================================================

-- Drop new tables
{% for table in new_tables %}
DROP TABLE {{ table.name }};
{% endfor %}

-- Remove new columns
{% for table, columns in new_columns.items() %}
{% for column in columns %}
ALTER TABLE {{ table }} DROP COLUMN {{ column.name }};
{% endfor %}
{% endfor %}

{% endif %}

-- Update version
UPDATE system_config SET version = '{{ to_version }}' WHERE key = 'schema_version';
COMMIT;
```

**migration_config.json**:
```json
{
  "migration_type": "upgrade",
  "from_version": "1.9.0",
  "to_version": "2.0.0",
  "now": "2025-10-24",
  "new_columns": {
    "users": [
      {"name": "last_login", "type": "DATE", "default": null},
      {"name": "login_count", "type": "NUMBER", "default": "0"}
    ]
  },
  "data_migrations": [
    {
      "table": "users",
      "column": "active",
      "value": "'Y'",
      "condition": "active IS NULL"
    }
  ],
  "new_tables": [
    {
      "name": "audit_log",
      "columns": [
        {"name": "id", "type": "NUMBER PRIMARY KEY"},
        {"name": "action", "type": "VARCHAR2(100)"},
        {"name": "timestamp", "type": "DATE DEFAULT SYSDATE"}
      ]
    }
  ]
}
```

**MKFSource.toml**:
```toml
[project]
input_file = "migration_v2_0_0.sql"
output_file = "migration_upgrade.sql"

[jinja2]
enabled = true
vars_file = "migration_config.json"
```

---

## 7. Conditional Feature Deployment

**Use Case**: Enable/disable features based on license or configuration.

### Files

**features.sql**:
```sql
-- Feature Deployment Script
-- License: {{ license_type }}

-- Core features (always included)
CREATE TABLE core_users (
    id NUMBER PRIMARY KEY,
    username VARCHAR2(50)
);

{% if features.analytics %}
-- ============================================================================
-- Analytics Module (Premium Feature)
-- ============================================================================

CREATE TABLE analytics_events (
    id NUMBER PRIMARY KEY,
    event_type VARCHAR2(50),
    event_data CLOB,
    created_date DATE DEFAULT SYSDATE
);

CREATE INDEX idx_analytics_type ON analytics_events(event_type);
CREATE INDEX idx_analytics_date ON analytics_events(created_date);
{% endif %}

{% if features.reporting %}
-- ============================================================================
-- Reporting Module (Enterprise Feature)
-- ============================================================================

CREATE TABLE reports (
    id NUMBER PRIMARY KEY,
    name VARCHAR2(100),
    definition CLOB,
    {% if features.scheduled_reports %}
    schedule VARCHAR2(100),
    last_run DATE,
    {% endif %}
    created_date DATE DEFAULT SYSDATE
);
{% endif %}

{% if features.api_access %}
-- ============================================================================
-- API Access (Professional+ Feature)
-- ============================================================================

CREATE TABLE api_keys (
    id NUMBER PRIMARY KEY,
    user_id NUMBER,
    api_key VARCHAR2(64) UNIQUE,
    rate_limit NUMBER DEFAULT {{ api_rate_limit }},
    created_date DATE DEFAULT SYSDATE,
    FOREIGN KEY (user_id) REFERENCES core_users(id)
);
{% endif %}

-- ============================================================================
-- Feature Summary
-- ============================================================================

-- License Type: {{ license_type }}
-- Enabled Features:
{% for feature, enabled in features.items() %}
--   - {{ feature }}: {{ "YES" if enabled else "NO" }}
{% endfor %}
```

**enterprise.json**:
```json
{
  "license_type": "Enterprise",
  "features": {
    "analytics": true,
    "reporting": true,
    "scheduled_reports": true,
    "api_access": true,
    "audit_logging": true
  },
  "api_rate_limit": 10000
}
```

**basic.json**:
```json
{
  "license_type": "Basic",
  "features": {
    "analytics": false,
    "reporting": false,
    "scheduled_reports": false,
    "api_access": false,
    "audit_logging": false
  },
  "api_rate_limit": 100
}
```

**MKFSource.toml**:
```toml
[project]
input_file = "features.sql"
output_file = "deployment.sql"

[jinja2]
enabled = true
vars_file = "enterprise.json"  # Change to basic.json for basic license
```

---

## 8. Template Reuse with Macros

**Use Case**: Define reusable SQL patterns using Jinja2 macros.

### Files

**templates.sql**:
```sql
{# Macro: Create audit columns #}
{% macro audit_columns() %}
    created_by VARCHAR2(50) NOT NULL,
    created_date DATE DEFAULT SYSDATE,
    modified_by VARCHAR2(50),
    modified_date DATE
{% endmacro %}

{# Macro: Create standard table with audit #}
{% macro create_table(name, columns) %}
CREATE TABLE {{ name }} (
    id NUMBER PRIMARY KEY,
{% for col in columns %}
    {{ col.name }} {{ col.type }}{% if col.not_null %} NOT NULL{% endif %},
{% endfor %}
    {{ audit_columns() }}
);
{% endmacro %}

{# Macro: Create audit trigger #}
{% macro audit_trigger(table_name) %}
CREATE OR REPLACE TRIGGER trg_{{ table_name }}_audit
BEFORE UPDATE ON {{ table_name }}
FOR EACH ROW
BEGIN
    :NEW.modified_by := USER;
    :NEW.modified_date := SYSDATE;
END;
/
{% endmacro %}

-- ============================================================================
-- Generate Tables with Macros
-- ============================================================================

{% for table in tables %}
{{ create_table(table.name, table.columns) }}
{{ audit_trigger(table.name) }}

{% endfor %}
```

**tables.json**:
```json
{
  "tables": [
    {
      "name": "employees",
      "columns": [
        {"name": "first_name", "type": "VARCHAR2(50)", "not_null": true},
        {"name": "last_name", "type": "VARCHAR2(50)", "not_null": true},
        {"name": "email", "type": "VARCHAR2(100)", "not_null": true},
        {"name": "salary", "type": "NUMBER(10,2)", "not_null": false}
      ]
    },
    {
      "name": "departments",
      "columns": [
        {"name": "name", "type": "VARCHAR2(100)", "not_null": true},
        {"name": "location", "type": "VARCHAR2(100)", "not_null": false}
      ]
    }
  ]
}
```

**MKFSource.toml**:
```toml
[project]
input_file = "templates.sql"
output_file = "generated.sql"

[jinja2]
enabled = true
vars_file = "tables.json"
```

---

## Tips and Best Practices

### 1. Organize Variables by Environment

```bash
config/
├── dev.json
├── test.json
├── staging.json
└── prod.json
```

Change `vars_file` in `MKFSource.toml` for each deployment.

### 2. Use Comments to Document Templates

```sql
{# 
  This template generates user tables
  Variables required: schema, table_prefix
#}
```

### 3. Validate Generated SQL

```bash
mergesourcefile
sqlplus user/pass @output.sql
```

### 4. Version Control Your Configurations

```bash
git add MKFSource.toml variables.json
git commit -m "Update deployment configuration"
```

### 5. Use Verbose Mode for Debugging

```toml
[project]
verbose = true  # Shows detailed processing steps
```

### 6. Always Use Backups When Overwriting

```toml
[project]
output_file = "schema.sql"  # Same as input
backup = true  # Creates schema.sql.bak
```

### 7. Escape User Input in SQL

```sql
SELECT * FROM users WHERE name = '{{ username|sql_escape }}';
```

---

## Advanced Patterns

### Dynamic Table Generation

```sql
{% for i in range(1, 13) %}
CREATE TABLE sales_{{ "%02d"|format(i) }}_{{ year }} (
    id NUMBER PRIMARY KEY,
    amount NUMBER(10,2),
    sale_date DATE
);
{% endfor %}
```

### Conditional Indexes

```sql
{% if environment == "production" %}
CREATE INDEX idx_large_table ON large_table(column1, column2)
    TABLESPACE index_tbs
    PARALLEL 4;
{% else %}
CREATE INDEX idx_large_table ON large_table(column1, column2);
{% endif %}
```

### Loop with Conditionals

```sql
{% for user in users %}
{% if user.active %}
GRANT {{ user.role }} TO {{ user.username }};
{% endif %}
{% endfor %}
```

---

## References

- [Configuration Guide](CONFIGURATION.md) - Complete TOML reference
- [Architecture Documentation](ARCHITECTURE.md) - System design
- [API Documentation](API_DOCUMENTATION.md) - Python API
- [Jinja2 Documentation](https://jinja.palletsprojects.com/) - Template syntax

---

**Need help?** Open an issue on [GitHub](https://github.com/alegorico/MergeSourceFile/issues)
