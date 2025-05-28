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


### Examples of Dependency Injection Issues

```python
# BAD: Direct instantiation of project dependencies
from project.user.repo import UserRepository

def process_data():
    repository = UserRepository()  # DI001: Dependency injection
    data = repository.get_all()
    return data

# BAD: Direct usage of project module functions
from project.notifications import send_email

def send_notification():
    send_email("user@example.com", "Hello")  # DI001: Dependency injection

# BAD: Using context managers from project modules
from project.db import context_manager

def backup_data():
    with context_manager():  # DI001: Dependency injection
        # do something
        pass
```

See more examples in [my_module.py](example/project/packet/my_module.py)


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
exclude-objects = ["Settings", "DIContainer"]

# Optional: Modules to exclude from dependency injection checks
exclude-modules = ["endpoints.py"]
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
di-exclude-modules = endpoints.py
di-config = path/to/di.toml  # Optional: custom path to configuration file
```

You can also specify these options on the command line:

```bash
flake8 --select=DI --di-exclude-objects=Settings,DIContainer --di-exclude-modules=endpoints.py --di-config=path/to/di.toml path/to/your/project
```

The `--di-config` option allows you to specify a custom path to the configuration file, 
which is useful when you want to use a configuration file that's not in one of the default locations.


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


## Output Examples


### Standalone Tool Output

```
Analyzing: /path/to/project
Project name: project
Exclude objects: []
Exclude modules: []
/path/to/project/module.py:10: Dependency injection: UserRepository()
/path/to/project/module.py:15: Dependency injection: with db_transaction():
```


### flake8 Plugin Output

```
/path/to/project/module.py:10:5: DI001 Dependency injection: UserRepository()
/path/to/project/module.py:15:10: DI001 Dependency injection: with db_transaction():
```


## Visual Example
![img.png](docs/img.png)
