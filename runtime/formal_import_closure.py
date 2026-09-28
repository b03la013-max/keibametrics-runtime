from __future__ import annotations

import argparse
import ast
import json
import pathlib
from typing import Dict, Iterable, List, Set

ROOT = pathlib.Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "runtime"


class FormalImportClosureError(ValueError):
    pass


def _module_candidates(module: str, current: pathlib.Path) -> Iterable[pathlib.Path]:
    name = str(module or "").strip()
    if not name:
        return []
    parts = name.split(".")
    candidates: List[pathlib.Path] = []

    if parts and parts[0] == "runtime":
        rel = pathlib.Path(*parts[1:]) if len(parts) > 1 else pathlib.Path()
        candidates.extend([RUNTIME / (str(rel) + ".py"), RUNTIME / rel / "__init__.py"])
    else:
        rel = pathlib.Path(*parts)
        candidates.extend([RUNTIME / (str(rel) + ".py"), RUNTIME / rel / "__init__.py"])
        candidates.extend([current.parent / (str(rel) + ".py"), current.parent / rel / "__init__.py"])

    seen = set()
    out = []
    for p in candidates:
        try:
            rp = p.resolve()
        except Exception:
            continue
        if rp in seen:
            continue
        seen.add(rp)
        try:
            rp.relative_to(ROOT)
        except ValueError:
            continue
        if rp.exists() and rp.is_file():
            out.append(rp)
    return out


def _relative_module(node: ast.ImportFrom, current: pathlib.Path) -> str:
    if not node.level:
        return str(node.module or "")
    try:
        rel_parent = current.parent.relative_to(RUNTIME)
        parent_parts = list(rel_parent.parts)
    except ValueError:
        parent_parts = []
    climb = max(0, int(node.level) - 1)
    if climb:
        parent_parts = parent_parts[:-climb] if climb <= len(parent_parts) else []
    if node.module:
        parent_parts.extend(str(node.module).split("."))
    return ".".join(parent_parts)


def local_imports(path: pathlib.Path, tree: ast.AST) -> List[pathlib.Path]:
    found: List[pathlib.Path] = []
    for node in ast.walk(tree):
        modules: List[str] = []
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = _relative_module(node, path)
            if module:
                modules.append(module)
            # from package import module may resolve to package/module.py.
            base = module
            for alias in node.names:
                if alias.name == "*":
                    continue
                candidate = ".".join(x for x in (base, alias.name) if x)
                if candidate:
                    modules.append(candidate)
        for module in modules:
            found.extend(_module_candidates(module, path))
    unique = sorted(set(found))
    return unique


def build_closure(entry: str | pathlib.Path) -> Dict[str, object]:
    start = pathlib.Path(entry)
    if not start.is_absolute():
        start = ROOT / start
    start = start.resolve()
    if not start.exists():
        raise FormalImportClosureError(f"ENTRY_MISSING:{start}")

    pending = [start]
    visited: Set[pathlib.Path] = set()
    edges: Dict[str, List[str]] = {}
    failures: List[Dict[str, str]] = []

    while pending:
        path = pending.pop()
        if path in visited:
            continue
        visited.add(path)
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(path))
            compile(source, str(path), "exec")
        except SyntaxError as exc:
            failures.append({
                "path": str(path.relative_to(ROOT)),
                "type": "SyntaxError",
                "message": str(exc),
            })
            continue
        except Exception as exc:
            failures.append({
                "path": str(path.relative_to(ROOT)),
                "type": type(exc).__name__,
                "message": str(exc),
            })
            continue

        imports = local_imports(path, tree)
        rel = str(path.relative_to(ROOT))
        edges[rel] = [str(p.relative_to(ROOT)) for p in imports]
        for child in imports:
            if child not in visited:
                pending.append(child)

    files = sorted(str(p.relative_to(ROOT)) for p in visited)
    report = {
        "schema": "KM-FORMAL-IMPORT-CLOSURE-v1",
        "entry": str(start.relative_to(ROOT)),
        "status": "PASS" if not failures else "FAIL",
        "file_count": len(files),
        "files": files,
        "edges": edges,
        "failures": failures,
    }
    if failures:
        first = failures[0]
        raise FormalImportClosureError(
            "FORMAL_IMPORT_CLOSURE_FAILED:"
            + first["path"] + ":"
            + first["type"] + ":"
            + first["message"]
        )
    return report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--entry", default="runtime/non_jra_formal_runner.py")
    ap.add_argument("--output")
    args = ap.parse_args()
    try:
        report = build_closure(args.entry)
    except FormalImportClosureError as exc:
        print(str(exc))
        return 2
    if args.output:
        out = pathlib.Path(args.output)
        if not out.is_absolute():
            out = ROOT / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
