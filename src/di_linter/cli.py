import argparse
import sys
from pathlib import Path

from di_linter.main import linter
from di_linter.patch_linter import patch_linter
from di_linter.utils import validate_path, find_project_root, load_config, frame_text_with_centered_title


def main():
    """Main entry point for the DI Linter command-line tool.

    Parses command-line arguments, loads configuration, and runs the linter.
    """
    parser = argparse.ArgumentParser(
        description="DI Linter - Static code analysis for dependency injection"
    )
    parser.add_argument("path", help="Module or project path to analyze")
    parser.add_argument("-c", "--config-path", help="Path to the configuration file")
    parser.add_argument(
        "--exclude-objects", nargs="+", help="List of objects to exclude from checks"
    )
    parser.add_argument(
        "--exclude-modules", nargs="+", help="List of module patterns to exclude from checks"
    )
    parser.add_argument(
        "--tests-path", nargs="+", help="List of paths to test directories or files", default="tests"
    )
    args = parser.parse_args()

    path = Path(args.path)
    validate_path(path)
    project_root = find_project_root(Path(args.path))

    config_path = None
    if args.config_path:
        config_path = Path(args.config_path)

    config = load_config(config_path)

    exclude_objects = []
    exclude_modules = []
    tests_paths = []

    if "exclude-objects" in config:
        exclude_objects = config.get("exclude-objects", [])
    if "exclude-modules" in config:
        exclude_modules = config.get("exclude-modules", [])
    if "tests-path" in config:
        tests_paths = config.get("tests-path", [])

    if args.exclude_objects:
        exclude_objects = args.exclude_objects
    if args.exclude_modules:
        exclude_modules = args.exclude_modules
    if args.tests_path:
        tests_paths = args.tests_path

    text = (
        f"Project path: {path.absolute()}\n"
        f"Project root: {project_root.name}\n"
        f"Exclude objects: {exclude_objects}\n"
        f"Exclude modules: {exclude_modules}\n"
        f"Tests paths: {tests_paths}\n"
        "{info}"
    )
    print("DI Linter scanning modules:")
    count = linter(path, project_root, exclude_objects, exclude_modules)

    patch_count = patch_linter(tests_paths)
    total_count = count + patch_count

    if total_count:
        print(frame_text_with_centered_title(
            text.format(info=f"Found {count} dependency injection problems and {patch_count} patch usage problems!"),
            "DI Linter"
        ))
        sys.exit(1)
    else:
        print(
            frame_text_with_centered_title(
                text.format(info="All checks have been successful!"),
                "DI Linter"
            ),
            file=sys.stderr
        )
