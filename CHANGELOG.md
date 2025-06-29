# Changelog

All notable changes to this project will be documented in this file.

### Added
## [1.2.0] - 2023-07-29

### Added
- New feature: detection of patch usage in test files
- New configuration option `tests-path` for specifying test directories
- Command-line argument `--tests-path` for specifying test directories
- New feature: support for module pattern exclusions using fnmatch syntax
- Enhanced pattern matching for both object and module exclusions
- Comprehensive documentation for pattern exclusion feature

### Changed
- Improved error reporting for patch usage in tests
- Enhanced output to show both dependency injection and patch usage issues

## [1.1.0] - 2023-06-10

### Added
- Support for Python 3.11
- Enhanced dependency injection detection
- New CLI tool `di-linter` for standalone usage
- [CHANGELOG.md](CHANGELOG.md)

### Changed
- Improved performance for large codebases
- Updated flake8 plugin compatibility
- Better error reporting and messages

### Fixed
- Various bug fixes and stability improvements
