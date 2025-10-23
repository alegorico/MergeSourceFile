# Scripts Directory

This directory contains utility scripts for development tasks.

## Development Scripts

- **`run_tests.py`** - Python script to run tests with coverage

## Internal Scripts

This directory also contains deployment and maintenance scripts that are used internally by project maintainers. See `DEPLOYMENT.md` for maintainer-only documentation.

## Usage

### Running Tests with Coverage

From project root directory:
```bash
# Run specific tests with coverage report
python .\scripts\run_tests.py

# Run all tests (recommended for development)
python -m pytest
```

From scripts directory:
```bash
cd scripts
python run_tests.py
```

## Notes

- ✅ **Auto-navigation**: Scripts automatically change to the project root directory when needed
- 🧪 **Testing**: The test script runs comprehensive test suites with coverage reporting  
- � **Coverage Reports**: HTML coverage reports are generated in `htmlcov/index.html`
- 🔧 **Dependencies**: Test script uses the project's virtual environment automatically