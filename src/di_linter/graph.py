import ast
from pathlib import Path
from typing import Dict, Set, Optional

from di_linter.main import ProjectImportsCollector
from di_linter.utils import find_project_root


class DependencyCollector(ast.NodeVisitor):
    def __init__(self, local_defs: Set[str], imported_modules: Dict[str, str], current_module: str):
        self.dependencies: Set[str] = set()
        self.local_defs = local_defs
        self.imported_modules = imported_modules
        self.current_module = current_module

    def visit_Name(self, node):
        if isinstance(node.ctx, (ast.Load, ast.Del)):
            full_name = self._resolve_name(node)
            if full_name:
                self.dependencies.add(full_name)
        self.generic_visit(node)

    def visit_Attribute(self, node):
        full_name = self._resolve_name(node)
        if full_name:
            self.dependencies.add(full_name)
        self.generic_visit(node)

    def _resolve_name(self, node) -> Optional[str]:
        name_parts = []

        current = node
        while isinstance(current, (ast.Attribute, ast.Name)):
            if isinstance(current, ast.Attribute):
                name_parts.append(current.attr)
                current = current.value
            else:
                name_parts.append(current.id)
                break

        name_parts.reverse()
        if not name_parts:
            return None

        dotted_name = ".".join(name_parts)
        root = name_parts[0]

        if root in self.imported_modules:
            resolved = self.imported_modules[root]
            rest = ".".join(name_parts[1:]) if len(name_parts) > 1 else ""
            return f"{resolved}.{rest}" if rest else resolved
        elif root in self.local_defs:
            return f"{self.current_module}.{dotted_name}"
        else:
            return None


class DependencyGraphBuilder:
    def __init__(self, project_root: Path, project_name: str):
        self.project_root = project_root
        self.project_name = project_name
        self.graph: Dict[str, Set[str]] = {}

    def build_graph(self) -> Dict[str, Set[str]]:
        for file in self.project_root.rglob("*.py"):
            if file.is_file():
                self._process_file(file)
        return self.graph

    def _process_file(self, filepath: Path):
        rel_path = filepath.relative_to(self.project_root.parent)
        module_name = ".".join(rel_path.with_suffix("").parts)

        content = filepath.read_text()
        tree = ast.parse(content)

        # Collect local definitions (functions, classes, variables)
        local_defs = self._collect_local_definitions(tree)

        # Collect imports
        imports_collector = ProjectImportsCollector(self.project_name)
        imports_collector.visit(tree)
        imports = imports_collector.imported_modules

        # Build dependency graph for each definition
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                collector = DependencyCollector(local_defs, imports, module_name)
                collector.visit(node)
                full_name = f"{module_name}.{node.name}"
                self.graph[full_name] = collector.dependencies

        # Handle global variable assignments
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        collector = DependencyCollector(local_defs, imports, module_name)
                        collector.visit(node.value)
                        full_name = f"{module_name}.{target.id}"
                        self.graph[full_name] = collector.dependencies

    def _collect_local_definitions(self, tree: ast.AST) -> Set[str]:
        local_defs = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                local_defs.add(node.name)
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        local_defs.add(target.id)
        return local_defs


def build_dependency_graph(path: Path, project_root: Optional[Path] = None) -> Dict[str, Set[str]]:
    """
    Builds a dependency graph of all functions, classes, and global variables in the project.

    Args:
        path (Path): Path to the project root or a specific file/directory to analyze.
        project_root (Optional[Path]): Optional override for the project root.

    Returns:
        Dict[str, Set[str]]: A graph where keys are fully object path,
                             and values are sets of fully object path they depend on.
        {'example.project.packet.my_module.LocalKlass': set(),
         'example.project.packet.my_module.LocalModuleException': set(),
         'example.project.packet.my_module.MyKlass': {'example.project.packet.my_module.LocalKlass',
                                                      'example.project.packet.my_module.LocalKlass.attr',
                                                      'example.project.packet.my_module.local_func'}}
    """
    if project_root is None:
        project_root = find_project_root(path)

    builder = DependencyGraphBuilder(project_root, project_root.name)
    return builder.build_graph()
