import os
import ast
from typing import List, Dict, Set, Any
from .models import Tombstone

class ASTGraveyardScanner:
    """
    Parses Abstract Syntax Trees (AST) across source trees to detect
    unreferenced functions, zombie routines, and dead code weight.
    """

    def __init__(self, root_dir: str = "."):
        self.root_dir = os.path.abspath(root_dir)

    def scan_for_zombie_symbols(self, ignore_tests: bool = True) -> List[Tombstone]:
        """
        Builds a cross-module reference graph:
        1. Definitions: FunctionDef, AsyncFunctionDef, ClassDef
        2. Usages: ast.Name (with ctx=Load), ast.Call, ast.Attribute
        Identifies symbols with 0 references across the entire repository.
        """
        defined_symbols: Dict[str, Dict[str, Any]] = {}
        referenced_symbol_names: Set[str] = set()

        # First pass: Parse AST across all files
        for root, dirs, files in os.walk(self.root_dir):
            dirs[:] = [d for d in dirs if d not in {'.git', '.kiro', '__pycache__', 'venv', '.venv', 'build', 'dist', 'node_modules', 'resurrected', '_vendor', 'site-packages', '__pypackages__'}]
            
            for file in files:
                if not file.endswith('.py'):
                    continue
                if ignore_tests and ('test' in file.lower() or 'conftest' in file.lower()):
                    continue

                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, self.root_dir)

                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        source = f.read()
                    tree = ast.parse(source, filename=rel_path)

                    for node in ast.walk(tree):
                        # Collect function and class definitions
                        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            if not node.name.startswith("__"):
                                defined_symbols[f"{rel_path}:{node.name}"] = {
                                    "name": node.name,
                                    "path": rel_path,
                                    "line": node.lineno,
                                    "docstring": ast.get_docstring(node) or "",
                                    "code_length": (getattr(node, 'end_lineno', node.lineno) - node.lineno) + 1
                                }

                        # Collect referenced names (calls, variable accesses, decorators)
                        if isinstance(node, ast.Name):
                            referenced_symbol_names.add(node.id)
                        elif isinstance(node, ast.Attribute):
                            referenced_symbol_names.add(node.attr)

                except SyntaxError:
                    continue

        # Second pass: Check which defined symbols are never referenced anywhere
        zombie_tombstones = []
        tomb_idx = 1

        for symbol_key, meta in defined_symbols.items():
            sym_name = meta["name"]
            
            # Skip entrypoints or framework hooks
            if sym_name in ["main", "cli", "run", "setup", "teardown"]:
                continue

            # If the symbol's name is NEVER loaded/called/referenced in any AST
            if sym_name not in referenced_symbol_names:
                zombie_tombstones.append(Tombstone(
                    id=f"tomb_zombie_{tomb_idx:03d}",
                    artifact_type="ZOMBIE_CODE",
                    name=sym_name,
                    path=meta["path"],
                    death_commit="CURRENT_HEAD",
                    author="Living Codebase",
                    death_date="Undetected Decay",
                    cause_of_death=f"Zero active callers detected across repository AST ({meta['code_length']} dead LOC)",
                    content_snippet=f"def {sym_name}(...):\n    \"\"\"{meta['docstring'] or 'No docstring found.'}\"\"\"\n    # Unreferenced function defined at line {meta['line']}",
                    line_number=meta["line"],
                    resurrectable=False,
                    metadata={"dead_loc": meta["code_length"]}
                ))
                tomb_idx += 1

        return zombie_tombstones
