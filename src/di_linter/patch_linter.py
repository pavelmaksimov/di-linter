import ast
import sys
from pathlib import Path
from typing import List

from di_linter.common import CodeLine, NumLine, Line, Issue, ASTParentTransformer


class PatchChecker:
    """
    The class for checking patches in test files.

    This class analyzes Python test files to find patch usage, which is forbidden.
    """

    def __init__(self, path: Path):
        """Initialize the TestChecker."""
        self.path = path
        self.issues: List[Issue] = []

    def analyze_tests(self):
        """Analyze the test files for patch usage."""
        if self.path.is_file():
            self._analyze_file(self.path)
        else:
            for file in self.path.rglob("*.py"):
                self._analyze_file(file)

        return self.issues

    def _analyze_file(self, filepath: Path):
        """Analyze a single file for patch usage."""
        content = filepath.read_text()

        lines = self._get_file_lines(content)
        tree = self._parse_ast(content)

        visitor = PatchVisitor(
            lines=lines,
            filepath=filepath,
            skip_comment="di: skip",
        )
        visitor.visit(tree)
        self.issues.extend(visitor.issues)

    def _get_file_lines(self, content: str) -> Line:
        """Returns all lines of the file with their numbers."""
        return {
            NumLine(num): CodeLine(line.strip()) for num, line in enumerate(content.splitlines(), 1)
        }

    def _parse_ast(self, content: str) -> ast.AST:
        """Parse the content into an AST and add parent links."""
        tree = ast.parse(content)
        return ASTParentTransformer().visit(tree)


class PatchVisitor(ast.NodeVisitor):
    """Checks for patches in test files.

    This visitor finds all patch usages in test files, which is forbidden.
    It checks for unittest.mock.patch, pytest monkeypatch, and other patch variants.
    """

    def __init__(
        self,
        lines: Line,
        filepath: Path,
        skip_comment: str,
    ):
        self.lines = lines
        self.filepath = filepath
        self.skip_comment = skip_comment
        self.issues: List[Issue] = []

    def visit_Call(self, node):
        """Visit a function call node in the AST.

        Checks if the function call represents a patch.

        Args:
            node: The AST node representing a function call
        """
        if self._is_patch(node.func) and not self._is_line_skipped(node.lineno):
            self._add_issue(line=node.lineno, col=node.col_offset, message="Patch usage in tests")

        self.generic_visit(node)

    def _is_patch(self, node) -> bool:
        """Check if the node represents a patch."""
        if isinstance(node, ast.Name):
            return node.id in {"patch", "monkeypatch"}
        elif isinstance(node, ast.Attribute):
            if node.attr in {"patch", "monkeypatch"}:
                return True
            return self._is_patch(node.value)
        return False

    def _is_line_skipped(self, line_num: int) -> bool:
        """Checks whether the line contains a commentary for passing."""
        line = self.lines.get(NumLine(line_num), "")
        return self.skip_comment in line

    def _add_issue(self, line: int, col, message: str):
        """Add a patch usage issue to the list of issues."""
        code_line = self.lines.get(NumLine(line), "")
        self.issues.append(
            Issue(
                filepath=self.filepath,
                line_num=line,
                message=message,
                code_line=code_line,
                col=col,
            )
        )


def iterate_patch_issue(paths: list[Path] | Path):
    """Iterate through patch usage issues found in the given test paths.

    Args:
        paths: A single path or a list of paths to analyze

    Yields:
        Issue objects representing patch usage issues
    """
    if not isinstance(paths, list):
        paths = [paths]

    for path in paths:
        print(f"Analyzing: {path.absolute()}")

        checker = PatchChecker(path.absolute())
        issues = checker.analyze_tests()
        if issues:
            for issue in issues:
                yield issue


def patch_linter(paths: list[str] | str) -> int:
    """Run the test linter on the given paths."""
    if not paths:
        return 0

    if not isinstance(paths, list):
        paths = [paths]

    test_paths = []
    for test_path_ in paths:
        test_path = Path(test_path_)
        if test_path.exists():
            test_paths.append(test_path)
        else:
            if test_path_ != "tests":
                print(f"Warning: Test path {test_path} does not exist", file=sys.stderr)

    count = 0
    for issue in iterate_patch_issue(test_paths):
        print(
            f"{issue.filepath}:{issue.line_num}: Patch usage in tests: {issue.code_line}",
            file=sys.stderr,
        )
        count += 1

    return count
