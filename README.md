# Dependency Injection Linter
Static code analysis for search of dependencies injection

## Installation

## Usage
1. Run the script in the project's root directory and specify the project directory name
```bash
  di-linter project
```

2. Run the script in the project's root directory without arguments. 
It contains a toml config file where the project directory name is specified.
```bash
  di-linter
```

## Configuration
Create a file `toml` in project root directory:
```toml
project-root = "project"
exclude-objects = ["Settings", "DIContainer"]
exclude-modules = ["endpoints.py"]
```
