from pathlib import Path

from flake8.options.manager import OptionManager

from .main import iterate_issue
from .utils import find_project_root, load_config


class DIChecker:
    """Flake8 plugin for checking dependency injections.

    This plugin integrates the dependency injection linter with Flake8,
    allowing it to be run as part of Flake8's static analysis.

    Attributes:
        name: Name of the plugin
        version: Version of the plugin
    """

    name = "di-linter"
    version = "0.1.0"

    def __init__(self, tree, filename, options=None):
        """Initialize the DIChecker.

        Args:
            tree: AST of the file to check
            filename: Path to the file to check
            options: Flake8 options object
        """
        self.tree = tree
        self.path = Path(filename)
        self.project_root = find_project_root(self.path)
        self.options = options

        # Load configuration
        config_path = None
        if self.options and hasattr(self.options, "di_config") and self.options.di_config:
            config_path = Path(self.options.di_config)

        self.config = load_config(config_path)

        # Get exclude lists from config or options
        self.exclude_objects = []
        self.exclude_modules = []

        # First try to get from config file
        if "exclude-objects" in self.config:
            self.exclude_objects = self.config.get("exclude-objects", [])
        if "exclude-modules" in self.config:
            self.exclude_modules = self.config.get("exclude-modules", [])

        # Then override with options if available
        if self.options:
            if hasattr(self.options, "di_exclude_objects") and self.options.di_exclude_objects:
                self.exclude_objects = self.options.di_exclude_objects
            if hasattr(self.options, "di_exclude_modules") and self.options.di_exclude_modules:
                self.exclude_modules = self.options.di_exclude_modules

    def run(self):
        """Run the dependency injection checker.

        Yields:
            Tuples containing (line_number, column, message, checker_type)
            for each dependency injection issue found
        """
        for issue in iterate_issue(
            self.path, self.project_root, self.exclude_objects, self.exclude_modules
        ):
            message = f"DI001 Dependency injection: {issue.code_line}"
            yield issue.line_num, issue.col, message, type(DIChecker)


def register_options(option_manager: OptionManager):
    """Register options for the DIChecker plugin with Flake8.

    This function is called by Flake8 to register command-line options
    and configuration file options for the plugin.

    Args:
        option_manager: Flake8's option manager
    """
    option_manager.add_option(
        "--di-exclude-objects",
        default="",
        parse_from_config=True,
        comma_separated_list=True,
        help="List of objects to exclude from dependency injection checks",
    )
    option_manager.add_option(
        "--di-exclude-modules",
        default="",
        parse_from_config=True,
        comma_separated_list=True,
        help="List of modules to exclude from dependency injection checks",
    )
    option_manager.add_option(
        "--di-config",
        default="",
        parse_from_config=True,
        help="Path to the di.toml configuration file",
    )
