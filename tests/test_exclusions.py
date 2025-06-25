import os
import subprocess
import tempfile
from pathlib import Path

import pytest

from di_linter.main import iterate_issue

EXAMPLE_DIR = Path(__file__).parent.parent / "example"
PROJECT_DIR = EXAMPLE_DIR / "project"
PACKET_DIR = PROJECT_DIR / "packet"
MY_MODULE_PATH = PACKET_DIR / "my_module.py"


def test_exclude_object_by_fullname():
    """Test that objects can be excluded by their full name."""
    # Test with exact match exclusion
    exclude_objects = ["LocalKlass"]
    exclude_modules = []

    issues = list(iterate_issue(MY_MODULE_PATH, PROJECT_DIR, exclude_objects, exclude_modules))

    # These should not be found because LocalKlass is excluded
    not_expected_injections = [
        "LocalKlass()",
        "lc = LocalKlass()",
        "LocalKlass().method2()",
        "x = LocalKlass.attr",
        "x2 = LocalKlass().attr",
    ]

    for not_injection in not_expected_injections:
        assert not any(not_injection == issue.code_line for issue in issues), (
            f"Injection should be excluded but was found: {not_injection}"
        )

    # These should still be found because they are not excluded
    expected_injections = [
        "local_func()",
        "func_from_other_module()",
    ]

    for injection in expected_injections:
        assert any(injection == issue.code_line for issue in issues), (
            f"Injection should be found but was not: {injection}"
        )


def test_exclude_object_by_pattern():
    """Test that objects can be excluded by pattern using fnmatch."""
    # Test with pattern match exclusion
    exclude_objects = ["Local*"]
    exclude_modules = []

    issues = list(iterate_issue(MY_MODULE_PATH, PROJECT_DIR, exclude_objects, exclude_modules))

    # These should not be found because they match the pattern Local*
    not_expected_injections = [
        "LocalKlass()",
        "lc = LocalKlass()",
        "LocalKlass().method2()",
        "x = LocalKlass.attr",
        "x2 = LocalKlass().attr",
        "local_func()",
        "with local_context_manager():",
    ]

    for not_injection in not_expected_injections:
        assert not any(not_injection == issue.code_line for issue in issues), (
            f"Injection should be excluded but was found: {not_injection}"
        )

    # These should still be found because they don't match the pattern
    expected_injections = [
        "func_from_other_module()",
        "alc = KlassFromOtherModule()",
    ]

    for injection in expected_injections:
        assert any(injection == issue.code_line for issue in issues), (
            f"Injection should be found but was not: {injection}"
        )


def test_exclude_multiple_patterns():
    """Test that multiple patterns can be used for exclusion."""
    # Test with multiple pattern match exclusions
    exclude_objects = ["Local*", "*FromOtherModule"]
    exclude_modules = []

    issues = list(iterate_issue(MY_MODULE_PATH, PROJECT_DIR, exclude_objects, exclude_modules))

    # These should not be found because they match one of the patterns
    not_expected_injections = [
        "LocalKlass()",
        "local_func()",
        "KlassFromOtherModule()",
        "KlassFromOtherModule().method2()",
        "a1 = KlassFromOtherModule.attr",
    ]

    for not_injection in not_expected_injections:
        assert not any(not_injection == issue.code_line for issue in issues), (
            f"Injection should be excluded but was found: {not_injection}"
        )

    # These should still be found because they don't match any pattern
    expected_injections = [
        "func_from_other_module()",
    ]

    for injection in expected_injections:
        assert any(injection == issue.code_line for issue in issues), (
            f"Injection should be found but was not: {injection}"
        )
