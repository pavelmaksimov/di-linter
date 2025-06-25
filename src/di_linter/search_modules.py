import fnmatch
from pathlib import Path
from typing import NewType


def match_pattern(module_name: str, pattern: str) -> bool:
    """
    Check if module name matches the given pattern.

    Args:
        module_name: Full module name (e.g., 'project.domains.crm.models')
        pattern: Pattern to match (e.g., "project.crm", "project.crm.*", "*.crm", "crm.*", "*.crm.*", "project.*.crm")

    Returns:
        True if the module name matches the pattern, False otherwise

    Examples for pattern
        "project.crm"
        "project.domains.crm"
        "project.domains.crm.*"
        "*.crm",
        "crm.*",
        "*.crm.*",
        "project.*.crm"
    """
    return fnmatch.fnmatch(module_name, pattern)


def get_module_path(issue, project_root):
    # Convert file path to module path format
    file_path = Path(issue.filepath).resolve()
    project_parent = project_root.parent.resolve()
    try:
        # Try to compute the relative path
        relative_path = file_path.relative_to(project_parent)
        module_path = ".".join(relative_path.with_suffix("").parts)
    except ValueError:
        # If the file is not in the project, use the file name as the module path
        module_path = file_path.stem

    return module_path
