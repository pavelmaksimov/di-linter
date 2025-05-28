import argparse
import ast
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set, Optional, NewType

from di_linter.utils import validate_path, find_project_root, load_config

CodeLine = NewType("CodeLine", str)
NumLine = NewType("NumLine", int)
Line = Dict[NumLine, CodeLine]


@dataclass
class Issue:
    """Represents a dependency injection issue found in the code.

    Attributes:
        filepath: Path to the file where the issue was found
        line_num: Line number where the issue was found
        message: Description of the issue
        code_line: The actual code line containing the issue
        col: Column number where the issue starts
    """

    filepath: Path
    line_num: int
    message: str
    code_line: str
    col: int


class ASTParentTransformer(ast.NodeTransformer):
    """Adds parental links to AST nodes.

    This transformer traverses the AST and adds a 'parent' attribute to each node,
    pointing to its parent node. This is useful for analyzing the context of a node
    in the AST, such as determining if a function call is part of a raise statement.
    """

    def visit(self, node):
        """Visit a node in the AST and add parent links to its children.

        Args:
            node: The AST node to visit

        Returns:
            The original node with parent links added to its children
        """
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        item.parent = node
                        self.visit(item)
            elif isinstance(value, ast.AST):
                value.parent = node
                self.visit(value)
        return node


class ProjectImportsCollector(ast.NodeVisitor):
    """Collects information about project imports.

    This visitor collects information about imports from the project,
    identified by a common prefix. It tracks both direct imports and
    imports from specific modules.

    Attributes:
        project_prefix: The prefix that identifies project modules
        imported_modules: Dictionary mapping import aliases to module names
    """

    def __init__(self, project_prefix: str):
        """Initialize the ProjectImportsCollector.

        Args:
            project_prefix: The prefix that identifies project modules
        """
        self.project_prefix = project_prefix
        self.imported_modules: Dict[str, str] = {}

    def visit_Import(self, node):
        """Visit an import statement in the AST.

        Collects information about direct imports from the project.

        Args:
            node: The AST node representing an import statement
        """
        for alias in node.names:
            if alias.name.startswith(self.project_prefix):
                self._add_import(alias.name, alias.asname)

    def visit_ImportFrom(self, node):
        """Visit an import-from statement in the AST.

        Collects information about imports from specific project modules.

        Args:
            node: The AST node representing an import-from statement
        """
        if node.module and node.module.startswith(self.project_prefix):
            for alias in node.names:
                self._add_import(node.module, alias.asname or alias.name)

    def _add_import(self, module: str, alias: Optional[str]):
        """Add an import to the collection.

        Args:
            module: The name of the imported module
            alias: The alias used for the import, or None if no alias was specified
        """
        if not alias:
            alias = module.split(".", 1)[0]
        self.imported_modules[alias] = module


class DependencyChecker:
    """The main class for checking dependencies in a project.

    This class analyzes Python files to find dependency injection issues.
    It collects information about imports, local definitions, and function calls
    to identify places where project dependencies are used without being passed
    as parameters.

    Attributes:
        path: Path to the file or directory to analyze
        project_name: Name of the project
        issues: List of dependency injection issues found
    """

    def __init__(self, path: Path, project_name: str):
        """Initialize the DependencyChecker.

        Args:
            path: Path to the file or directory to analyze
            project_name: Name of the project
        """
        self.path = path
        self.project_name = project_name
        self.issues: List[Issue] = []

    def analyze_project(self):
        """Analyze the project for dependency injection issues.

        If path is a file, analyzes only that file.
        If path is a directory, recursively analyzes all Python files in it.

        Returns:
            List of dependency injection issues found
        """
        if self.path.is_file():
            self._analyze_file(self.path)
        else:
            for file in self.path.rglob("*.py"):
                self._analyze_file(file)

        return self.issues

    def _analyze_file(self, filepath: Path):
        """Analyze a single file for dependency injection issues.

        Args:
            filepath: Path to the file to analyze
        """
        content = filepath.read_text()

        lines = self._get_file_lines(content)
        tree = self._parse_ast(content)
        imports = self._collect_imports(tree)
        local_defs = self._collect_local_definitions(tree)

        FunctionVisitor(
            filepath=filepath,
            imports=imports,
            local_defs=local_defs,
            lines=lines,
            issues=self.issues,
        ).visit(tree)

    def _get_file_lines(self, content: str) -> Line:
        """Returns all lines of the file with their numbers.

        Args:
            content: Content of the file

        Returns:
            Dictionary mapping line numbers to line content
        """
        return {
            NumLine(num): CodeLine(line.strip()) for num, line in enumerate(content.splitlines(), 1)
        }

    def _parse_ast(self, content: str) -> ast.AST:
        """Parse the content into an AST and add parent links.

        Args:
            content: Content of the file

        Returns:
            AST with parent links
        """
        tree = ast.parse(content)
        return ASTParentTransformer().visit(tree)

    def _collect_imports(self, tree: ast.AST) -> Dict[str, str]:
        """Collect information about project imports.

        Args:
            tree: AST of the file

        Returns:
            Dictionary mapping import aliases to module names
        """
        collector = ProjectImportsCollector(self.project_name)
        collector.visit(tree)
        return collector.imported_modules

    def _collect_local_definitions(self, tree: ast.AST) -> Set[str]:
        """Collect names of all functions and classes defined in the file.

        Args:
            tree: AST of the file

        Returns:
            Set of function and class names
        """
        definitions = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                definitions.add(node.name)
        return definitions


class FunctionVisitor(ast.NodeVisitor):
    """Visits function definitions in the AST and processes them for dependency injection checks.

    This visitor finds all function and async function definitions in the code and
    analyzes them for potential dependency injection issues.
    """

    def __init__(
        self,
        filepath: Path,
        imports: Dict[str, str],
        local_defs: Set[str],
        lines: Line,
        issues: List[Issue],
    ):
        self.filepath = filepath
        self.imports = imports
        self.local_defs = local_defs
        self.lines = lines
        self.issues = issues

    def visit_FunctionDef(self, node):
        """Visit a function definition node in the AST.

        Args:
            node: The AST node representing a function definition
        """
        self._process_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        """Visit an async function definition node in the AST.

        Args:
            node: The AST node representing an async function definition
        """
        self._process_function(node)
        self.generic_visit(node)

    def _process_function(self, node):
        """Process a function or async function node for dependency injection checks.

        Extracts function parameters and creates a DependencyVisitor to check
        for dependency injection issues within the function body.

        Args:
            node: The AST node representing a function or async function
        """
        params = self._get_function_parameters(node)
        visitor = DependencyVisitor(
            local_defs=self.local_defs,
            imported_modules=self.imports,
            params=params,
            lines=self.lines,
            filepath=self.filepath,
            skip_comment="di: skip",
        )
        visitor.visit(node)
        self.issues.extend(visitor.issues)

    def _get_function_parameters(self, node) -> Set[str]:
        """Extract all parameter names from a function definition.

        Args:
            node: The AST node representing a function definition

        Returns:
            A set of parameter names
        """
        params = set()
        for arg in node.args.posonlyargs:
            params.add(arg.arg)
        for arg in node.args.args:
            params.add(arg.arg)
        if node.args.vararg:
            params.add(node.args.vararg.arg)
        for arg in node.args.kwonlyargs:
            params.add(arg.arg)
        if node.args.kwarg:
            params.add(node.args.kwarg.arg)
        return params


class DependencyVisitor(ast.NodeVisitor):
    """Checks the dependence inside the function."""

    def __init__(
        self,
        local_defs: Set[str],
        imported_modules: Dict[str, str],
        params: Set[str],
        lines: Line,
        filepath: Path,
        skip_comment: str,
    ):
        self.local_defs = local_defs
        self.imported_modules = imported_modules
        self.params = params
        self.lines = lines
        self.filepath = filepath
        self.skip_comment = skip_comment
        self.issues: List[Issue] = []

    def visit_Call(self, node):
        """Visit a function call node in the AST.

        Checks if the function call represents a dependency injection.
        Ignores calls in raise statements.

        Args:
            node: The AST node representing a function call
        """
        if self._is_in_raise_statement(node):
            return

        if self._is_project_dependency(node.func):
            root_name = self._get_root_name(node.func)
            if root_name not in self.params and not self._is_line_skipped(node.lineno):
                self._add_issue(line=node.lineno, col=node.col_offset, message=root_name)

        self.generic_visit(node)

    def visit_Attribute(self, node):
        """Visit an attribute access node in the AST.

        Checks if the attribute access represents a dependency injection.

        Args:
            node: The AST node representing an attribute access
        """
        if not isinstance(node.parent, ast.Call) and self._is_project_dependency(node):
            root_name = self._get_root_name(node)
            if root_name not in self.params and not self._is_line_skipped(node.lineno):
                self._add_issue(line=node.lineno, col=node.col_offset, message=root_name)
        self.generic_visit(node)

    def _is_in_raise_statement(self, node) -> bool:
        """Check if the node is part of a raise statement.

        Args:
            node: The AST node to check

        Returns:
            True if the node is part of a raise statement, False otherwise
        """
        return isinstance(node.parent, ast.Raise)

    def _is_project_dependency(self, node) -> bool:
        """Check if the node represents a project dependency.

        A project dependency is either a local definition or an imported module.

        Args:
            node: The AST node to check

        Returns:
            True if the node is a project dependency, False otherwise
        """
        if isinstance(node, ast.Name):
            return node.id in self.local_defs or node.id in self.imported_modules
        elif isinstance(node, ast.Attribute):
            return self._is_project_dependency(node.value)
        return False

    def _get_root_name(self, node) -> str:
        """Get the root name of a node.

        For a Name node, returns the identifier.
        For an Attribute node, returns the root name of the value.

        Args:
            node: The AST node to get the root name from

        Returns:
            The root name as a string
        """
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return self._get_root_name(node.value)
        return "<unknown>"

    def _is_line_skipped(self, line_num: int) -> bool:
        """Checks whether the line contains a commentary for passing."""
        line = self.lines.get(NumLine(line_num), "")
        return self.skip_comment in line

    def _add_issue(self, line: int, col, message: str):
        """Add a dependency injection issue to the list of issues.

        Args:
            line: The line number where the issue was found
            col: The column number where the issue starts
            message: Description of the issue
        """
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


def iterate_issue(paths: list[Path] | Path, project_root, exclude_modules, exclude_objects):
    """Iterate through dependency injection issues found in the given paths.

    Args:
        paths: A single path or a list of paths to analyze
        project_root: The root directory of the project
        exclude_modules: List of module names to exclude from checks
        exclude_objects: List of object names to exclude from checks

    Yields:
        Issue objects representing dependency injection issues
    """
    if not isinstance(paths, list):
        paths = [paths]

    for path in paths:
        checker = DependencyChecker(path.absolute(), project_root.name)
        issues = checker.analyze_project()
        if issues:
            for issue in issues:
                if (
                    issue.message not in exclude_objects
                    and Path(issue.filepath).name not in exclude_modules
                ):
                    yield issue


def linter(path: Path, project_root: Path, exclude_objects=None, exclude_modules=None):
    """Run the dependency injection linter on the given path.

    Args:
        path: Path to the file or directory to analyze
        project_root: The root directory of the project
        exclude_objects: List of object names to exclude from checks
        exclude_modules: List of module names to exclude from checks

    Returns:
        None. Exits with code 1 if dependency injections are found.
    """
    exclude_objects = exclude_objects or ()
    exclude_modules = exclude_modules or ()

    print(f"Analyzing {path.absolute()}")

    has_di = False
    for issue in iterate_issue(path, project_root, exclude_modules, exclude_objects):
        has_di = True
        print(
            f"{issue.filepath}:{issue.line_num}: Dependency injection: {issue.code_line}",
            file=sys.stderr,
        )

    if has_di:
        sys.exit(1)

    print("All checks have been successful!")


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
        "--exclude-modules", nargs="+", help="List of modules to exclude from checks"
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

    if "exclude-objects" in config:
        exclude_objects = config.get("exclude-objects", [])
    if "exclude-modules" in config:
        exclude_modules = config.get("exclude-modules", [])

    if args.exclude_objects:
        exclude_objects = args.exclude_objects
    if args.exclude_modules:
        exclude_modules = args.exclude_modules

    print(f"Analyzing: {path}")
    print(f"Project name: {project_root.name}")
    print(f"Exclude objects: {exclude_objects}")
    print(f"Exclude modules: {exclude_modules}")

    linter(path, project_root, exclude_objects, exclude_modules)
