import ast
from typing import List, Tuple

from di_linter.flake8_plugin import DIChecker


def run_checker_on_code(code: str, filename: str = "test.py") -> List[Tuple[int, int, str, type]]:
    """Run the DIChecker on the given code and return the issues."""
    tree = ast.parse(code)
    checker = DIChecker(tree, filename)
    # Manually set the lines for testing
    checker.lines = code.splitlines()
    return list(checker.run())


def test_no_dependency_injection():
    """Test that no issues are reported when there are no dependency injections."""
    code = """
def function():
    pass
"""
    issues = run_checker_on_code(code)
    assert not issues
