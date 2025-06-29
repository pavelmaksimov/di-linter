# Dependency Injection Linter

A static code analysis tool that detects dependency injection anti-patterns in Python projects. This linter helps enforce clean architecture principles by identifying direct instantiation or usage of project-specific dependencies within your code.


## What is Dependency Injection?

Dependency Injection is a design pattern where a class or function receives its dependencies from external sources rather than creating them internally. This pattern promotes:

- **Loose coupling** between components
- **Better testability** through easier mocking of dependencies
- **Improved maintainability** by centralizing dependency management
- **Enhanced flexibility** for swapping implementations


## What This Linter Detects

This linter identifies cases where project-specific dependencies are directly created or used within functions or methods, rather than being injected as parameters. It helps enforce the principle that dependencies should be passed in, not created internally.

Additionally, the linter detects patch usage in test files, which is considered a bad practice as it can lead to brittle tests and make refactoring more difficult.


### Examples of Dependency Injection Issues

```python
from project.user.repo import UserRepository

def process_data():
    # BAD: Direct instantiation of project dependencies
    repository = UserRepository()  # DI001: Dependency injection
    data = repository.get_all()
    return data

from project.notifications import send_email

def send_notification():
    # BAD: Direct usage of project module functions
    send_email("user@example.com", "Hello")  # DI001: Dependency injection

from project.db import context_manager

def backup_data():
    # BAD: Using context managers from project modules
    with context_manager():  # DI001: Dependency injection
        # do something
        pass
```

See more examples in [my_module.py](example/project/packet/my_module.py)


### Examples of Patch Usage in Tests

```python
import unittest
from unittest.mock import patch

class TestExample(unittest.TestCase):
    # BAD: Using patch decorator
    @patch('module.function')  # Patch usage in tests
    def test_function(self, mock_function):
        mock_function.return_value = 'mocked'
        self.assertEqual(mock_function(), 'mocked')

    def test_function_with_context_manager(self):
        # BAD: Using patch as context manager
        with patch('module.function') as mock_function:  # Patch usage in tests
            mock_function.return_value = 'mocked'
            self.assertEqual(mock_function(), 'mocked')

import pytest

def test_with_monkeypatch(monkeypatch):
    # BAD: Using pytest monkeypatch
    monkeypatch.setattr('module.function', lambda: 'mocked')  # Patch usage in tests
    assert 'mocked' == 'mocked'
```


### Correct Approaches

```python
# GOOD: Dependencies injected as parameters
def process_data(repository):
    data = repository.get_all()
    return data

# GOOD: Dependencies passed as arguments
def send_notification(email_sender):
    email_sender("user@example.com", "Hello")

# GOOD: Context managers passed as parameters
def backup_data(context_manager):
    with context_manager():
        # do something
        pass
```


## Installation

```bash
pip install di-linter
```


## Usage


### As a standalone tool

1. Run the linter specifying the project directory:

```bash
di-linter path/to/project
```

2. Run the linter using a configuration file:
```bash
di-linter --config-path di.toml
```

3. Run the linter with custom test paths for patch detection:
```bash
di-linter path/to/project --tests-path tests/unit tests/integration
```


### As a flake8 plugin

```bash
flake8 --select=DI path/to/your/project
```


## Configuration


### Standalone tool configuration

The configuration file `di.toml` is optional. 
If not provided, the linter will work with default settings.

```toml
# Required: The root directory of your project
project-root = "project"

# Optional: Objects to exclude from dependency injection checks
# Supports fnmatch pattern syntax with wildcards (*)
exclude-objects = [
    "Settings",              # Exact match
    "DIContainer",           # Exact match
    "Config*",               # All objects starting with Config
    "*Repository",           # All objects ending with Repository
    "*Factory*"              # All objects containing Factory
]

# Optional: Module patterns to exclude from dependency injection checks
# Supports fnmatch pattern syntax with wildcards (*)
exclude-modules = [
    "project.endpoints",     # Exact match
    "project.api.*",         # All modules in the api package
    "*.endpoints",           # All modules ending with endpoints
    "project.*.models"       # All models modules in any subpackage of project
]

# Optional: Paths to test directories or files for patch usage detection
tests-path = [
    "tests",                 # Default test directory
    "tests/unit",            # Specific test subdirectory
    "tests/integration"      # Another test subdirectory
]
```


#### Configuration File Location

The linter looks for the configuration file in the following locations:
1. The current working directory (`./di.toml`)
2. The parent directory of the project root

You can also specify a custom path to the configuration file using the `--config-path` option:

```bash
di-linter path/to/project --config-path /path/to/custom/di.toml
```


#### Project Root Detection

The project root is automatically detected by looking for marker files such as:
- `setup.py`
- `setup.cfg`
- `pyproject.toml`
- `requirements.txt`

Or by finding the directory where `__init__.py` is no longer present in the parent directory.


### flake8 plugin configuration

The configuration file `di.toml` is optional for the flake8 plugin as well. 
If not provided, the plugin will work with default settings and follow 
the same configuration file search logic as the standalone tool.

Add the following to your flake8 configuration file (e.g., `.flake8`, `setup.cfg`, or `tox.ini`):

```ini
[flake8]
select = DI
di-exclude-objects = Settings,DIContainer
di-exclude-modules = project.endpoints,project.api.*,*.endpoints,project.*.models
di-tests-path = tests,tests/unit,tests/integration  # Optional: paths to test directories for patch detection
di-config = path/to/di.toml  # Optional: custom path to configuration file
```

You can also specify these options on the command line:

```bash
flake8 --select=DI --di-exclude-objects=Settings,DIContainer --di-exclude-modules=project.endpoints,project.api.* --di-tests-path=tests,tests/unit --di-config=path/to/di.toml path/to/your/project
```

The `--di-config` option allows you to specify a custom path to the configuration file, 
which is useful when you want to use a configuration file that's not in one of the default locations.


## Pattern Exclusions

The linter supports excluding specific objects and modules from dependency injection checks using pattern matching. This is useful when you have certain objects or modules that you want to exempt from the dependency injection rules.

### Pattern Matching Syntax

Both `exclude-objects` and `exclude-modules` support pattern matching using the `fnmatch` syntax, which allows for flexible wildcard matching:

- `*` matches any sequence of characters (including none)
- Exact string matches the exact name
- Pattern matching is case-insensitive (e.g., "Local*" will match both "LocalKlass" and "local_func")

### Object Pattern Examples

- `"Settings"` - Matches exactly the object named "Settings"
- `"Config*"` - Matches all objects starting with "Config" (e.g., "Config", "ConfigLoader", "ConfigManager")
- `"*Repository"` - Matches all objects ending with "Repository" (e.g., "UserRepository", "ProductRepository")
- `"*Factory*"` - Matches all objects containing "Factory" (e.g., "Factory", "UserFactory", "FactoryMethod")

### Module Pattern Examples

- `"project.endpoints"` - Matches exactly the module named "project.endpoints"
- `"project.api.*"` - Matches all modules in the "project.api" package (e.g., "project.api.users", "project.api.products")
- `"*.endpoints"` - Matches all modules ending with "endpoints" (e.g., "api.endpoints", "web.endpoints")
- `"project.*.models"` - Matches all "models" modules in any subpackage of "project" (e.g., "project.users.models", "project.products.models")

### How Exclusions Work

- **Object exclusions** match against the object name in the issue message (e.g., "LocalKlass", "func_from_other_module")
- **Module exclusions** match against the module path of the file where the issue is reported, not the imported module
- To exclude issues related to a specific imported module, you can:
  1. Use `exclude-objects` with patterns matching the imported module name (e.g., "other_module*")
  2. Use `exclude-modules` to exclude the entire file where the imports are used

## Skipping Specific Lines

You can skip specific lines by adding a comment with `# di: skip`:

```python
def myfunc():
    repository = UserRepository()  # di: skip
```


## Error Codes

| Code  | Description                                                |
|-------|------------------------------------------------------------|
| DI001 | Dependency injection: Direct usage of project dependencies |
| DI002 | Patch usage in tests: Using mocks or patches in test files |


## Output Examples


### Standalone Tool Output

```
DI Linter scanning modules:
Analyzing: /path/to/project
Analyzing tests in ['/path/to/tests']
/path/to/project/module.py:10: Dependency injection: UserRepository()
/path/to/project/module.py:15: Dependency injection: with db_transaction():
/path/to/tests/test_module.py:8: Patch usage in tests: @patch('module.function')
/path/to/tests/test_module.py:15: Patch usage in tests: with patch('module.function') as mock_function:
/path/to/tests/test_module.py:22: Patch usage in tests: monkeypatch.setattr('module.function', lambda: 'mocked')

┌─────────────────────────────────────────────── DI Linter ───────────────────────────────────────────────┐
│ Project path: /path/to/project                                                                          │
│ Project root: project                                                                                   │
│ Exclude objects: []                                                                                     │
│ Exclude modules: []                                                                                     │
│ Tests paths: ['/path/to/tests']                                                                         │
│ Found 2 dependency injection problems and 3 patch usage problems!                                       │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```


### flake8 Plugin Output

```
/path/to/project/module.py:10:5: DI001 Dependency injection: UserRepository()
/path/to/project/module.py:15:10: DI001 Dependency injection: with db_transaction():
/path/to/tests/test_module.py:8:5: DI002 Patch usage in tests: @patch('module.function')
/path/to/tests/test_module.py:15:10: DI002 Patch usage in tests: with patch('module.function') as mock_function:
/path/to/tests/test_module.py:22:5: DI002 Patch usage in tests: monkeypatch.setattr('module.function', lambda: 'mocked')
```
