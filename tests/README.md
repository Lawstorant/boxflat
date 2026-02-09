# Boxflat Tests

This directory contains unit tests for the Boxflat application.

## Running Tests

### On Linux

Run all tests:
```bash
python3 -m pytest tests/
```

Or run specific test file:
```bash
python3 -m unittest tests/test_process_handler.py
```

Or with verbose output:
```bash
python3 tests/test_process_handler.py
```

### Requirements

Install test dependencies:
```bash
pip install pytest
```

## Test Coverage

- **test_process_handler.py**: Tests for the process handler, including:
  - ProcessInfo class functionality
  - Command-line pattern matching
  - Process discovery and filtering

## Notes

- Some tests require a Linux environment as they test Linux-specific functionality
- Tests that require Linux will be skipped automatically when run on other platforms
- The process observer tests need actual processes running to be fully tested

## Adding New Tests

1. Create a new file `test_<module>.py` in this directory
2. Import `unittest` and the module you want to test
3. Create test classes that inherit from `unittest.TestCase`
4. Name test methods starting with `test_`
5. Run tests to verify they work
