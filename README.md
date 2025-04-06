# Dependency Injection Linter
Static code analysis for search of dependencies injection

## Installation
```bash
pip install di-linter
```
Or
```bash
uv add --dev di-linter
```

## Usage
1. Run the script in the project's root directory and specify the project directory name
```bash
  di-linter project
```
Or
```bash
  uv run di-linter project
```

2. Run the script in the project's root directory without arguments. 
It contains a toml config file where the project directory name is specified.
```bash
  di-linter
```
Or
```bash
  uv run di-linter
```

## Configuration
Create a file `toml` in project root directory:
```toml
project-root = "project"
exclude-objects = ["Settings", "DIContainer"]
exclude-modules = ["endpoints.py"]
```
