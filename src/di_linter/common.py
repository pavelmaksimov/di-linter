import ast
from dataclasses import dataclass
from pathlib import Path
from typing import NewType, Dict

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
