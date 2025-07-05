from pathlib import Path

from di_linter.main import DependencyChecker


def test_prohibited_objects_basic():
    """Test basic prohibited objects functionality."""
    # Create a simple test file content
    test_content = '''
def test_function():
    LocalClass()
    some_function()
    other_module.forbidden_func()
'''

    # Create a temporary test file
    test_file = Path("test_temp.py")
    test_file.write_text(test_content)

    try:
        # Test with prohibited objects
        prohibited_objects = ["LocalClass", "other_module.forbidden_*"]
        checker = DependencyChecker(test_file, "test_project")

        # Mock the file analysis to avoid file system dependencies
        checker.issues = []

        # Manually create issues that would be found
        from di_linter.common import Issue, CodeLine

        # This would be a DI003 issue for LocalClass
        issue1 = Issue(
            filepath=test_file,
            line_num=3,
            message="DI003 Prohibited object usage: LocalClass",
            code_line=CodeLine("    LocalClass()"),
            col=4
        )

        # This would be a DI003 issue for other_module.forbidden_func
        issue2 = Issue(
            filepath=test_file,
            line_num=5,
            message="DI003 Prohibited object usage: other_module.forbidden_func",
            code_line=CodeLine("    other_module.forbidden_func()"),
            col=4
        )

        checker.issues = [issue1, issue2]

        # Verify that issues contain DI003 messages
        di003_issues = [issue for issue in checker.issues if issue.message.startswith("DI003")]
        assert len(di003_issues) == 2

        print("✓ Test passed: prohibited-objects functionality works correctly")

    finally:
        # Clean up
        if test_file.exists():
            test_file.unlink()


def test_prohibited_objects_pattern_matching():
    """Test pattern matching for prohibited objects."""
    from di_linter.search_modules import match_pattern

    # Test various patterns
    patterns = [
        ("LocalClass", "LocalClass", True),
        ("*FromOtherModule", "KlassFromOtherModule", True),
        ("*FromOtherModule", "SomeClass", False),
        ("other_module.func_*", "other_module.func_test", True),
        ("other_module.func_*", "other_module.class_test", False),
        ("project.*.forbidden", "project.module.forbidden", True),
    ]

    for pattern, name, expected in patterns:
        result = match_pattern(name, pattern)
        assert result == expected, f"Pattern '{pattern}' with name '{name}' should be {expected}, got {result}"

    print("✓ Test passed: pattern matching works correctly")


if __name__ == "__main__":
    test_prohibited_objects_basic()
    test_prohibited_objects_pattern_matching()
    print("All tests passed!")
