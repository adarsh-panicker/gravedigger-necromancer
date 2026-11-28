import ast
import json
import os
import re
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional, Set, Tuple

from .models import ExcavationReport, Tombstone


GITHUB_REPO_RE = re.compile(
    r"^(?:https?://(?:www\.)?github\.com/)?([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?/?$"
)


def parse_github_repo(repo_input: str) -> Optional[Tuple[str, str]]:
    """Parses 'https://github.com/owner/repo' or 'owner/repo' into (owner, repo)."""
    cleaned = repo_input.strip()
    if not cleaned:
        return None
    match = GITHUB_REPO_RE.match(cleaned)
    if not match:
        return None
    return match.group(1), match.group(2)


def _http_get_json(url: str, timeout: int = 10) -> Any:
    headers = {
        "User-Agent": "GraveDigger-Necromancer/1.0",
        "Accept": "application/vnd.github+json",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def _http_get_text(url: str, timeout: int = 10) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "GraveDigger-Necromancer/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def scan_python_sources(
    sources: Dict[str, str],
    repo_label: str,
    commit_label: str = "CURRENT_HEAD",
) -> Tuple[List[Tombstone], Dict[str, str]]:
    """Scans a dict of {rel_path: source_code} for unreferenced zombie functions."""
    defined_symbols: Dict[str, Dict[str, Any]] = {}
    referenced_names: Set[str] = set()

    for rel_path, source in sources.items():
        try:
            tree = ast.parse(source, filename=rel_path)
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith("__"):
                    defined_symbols[f"{rel_path}:{node.name}"] = {
                        "name": node.name,
                        "path": rel_path,
                        "line": node.lineno,
                        "docstring": ast.get_docstring(node) or "",
                        "code_length": (getattr(node, "end_lineno", node.lineno) - node.lineno) + 1,
                        "source_segment": ast.get_source_segment(source, node) or "",
                    }
            if isinstance(node, ast.Name):
                referenced_names.add(node.id)
            elif isinstance(node, ast.Attribute):
                referenced_names.add(node.attr)

    tombstones: List[Tombstone] = []
    blobs: Dict[str, str] = {}
    idx = 1

    for _, sym in defined_symbols.items():
        if sym["name"] in referenced_names:
            continue
        tomb_id = f"tomb_ast_{idx:03d}"
        idx += 1

        doc = sym["docstring"].strip() or "No docstring found."
        snippet = (
            f"def {sym['name']}(...):\n"
            f"    \"\"\"{doc[:100]}\"\"\"\n"
            f"    # Unreferenced function at line {sym['line']}"
        )
        blobs[tomb_id] = sym["source_segment"] or snippet
        tombstones.append(
            Tombstone(
                id=tomb_id,
                artifact_type="ZOMBIE_CODE",
                name=sym["name"],
                path=sym["path"],
                death_commit=commit_label,
                author="Living Codebase",
                death_date="Undetected Decay",
                cause_of_death=f"Zero callers detected across scanned AST ({sym['code_length']} dead LOC)",
                content_snippet=snippet,
                line_number=sym["line"],
                resurrectable=True,
                metadata={"dead_loc": sym["code_length"], "repo": repo_label},
            )
        )
        if len(tombstones) >= 15:
            break

    return tombstones, blobs


def scan_pasted_code(source_code: str, filename: str = "pasted_snippet.py") -> Tuple[ExcavationReport, Dict[str, str]]:
    """Scans raw Python code pasted by a user/judge in the Web Dashboard."""
    tombstones, blobs = scan_python_sources({filename: source_code}, repo_label="Custom Pasted Code", commit_label="SNIPPET")
    dead_loc = sum(t.metadata.get("dead_loc", 10) for t in tombstones)
    report = ExcavationReport(
        repo_path="Custom Pasted Python Snippet",
        total_tombstones=len(tombstones),
        deleted_files_count=0,
        zombie_functions_count=len(tombstones),
        abandoned_branches_count=0,
        dead_loc=dead_loc,
        tombstones=tombstones,
    )
    return report, blobs


class GitHubRepoScanner:
    """
    Lightweight, zero-dependency remote GitHub repository excavator.
    Uses GitHub REST API + raw.githubusercontent.com + Python AST to excavate
    deleted files and unreferenced zombie functions from any public GitHub repo.
    """

    def __init__(self, owner: str, repo: str):
        self.owner = owner
        self.repo = repo
        self.repo_slug = f"{owner}/{repo}"

    def run_excavation(self) -> Tuple[ExcavationReport, Dict[str, str]]:
        repo_meta = _http_get_json(f"https://api.github.com/repos/{self.repo_slug}")
        default_branch = repo_meta.get("default_branch", "main")

        tombstones: List[Tombstone] = []
        blob_cache: Dict[str, str] = {}

        deleted_tombstones, deleted_blobs = self._excavate_deleted_files()
        tombstones.extend(deleted_tombstones)
        blob_cache.update(deleted_blobs)

        zombie_tombstones, zombie_blobs = self._excavate_zombie_symbols(default_branch)
        tombstones.extend(zombie_tombstones)
        blob_cache.update(zombie_blobs)

        dead_loc = sum(t.metadata.get("dead_loc", 15) for t in tombstones)
        report = ExcavationReport(
            repo_path=f"https://github.com/{self.repo_slug}",
            total_tombstones=len(tombstones),
            deleted_files_count=len(deleted_tombstones),
            zombie_functions_count=len(zombie_tombstones),
            abandoned_branches_count=0,
            dead_loc=dead_loc,
            tombstones=tombstones,
        )
        return report, blob_cache

    def _excavate_deleted_files(self) -> Tuple[List[Tombstone], Dict[str, str]]:
        tombstones: List[Tombstone] = []
        blobs: Dict[str, str] = {}

        commits = _http_get_json(
            f"https://api.github.com/repos/{self.repo_slug}/commits?per_page=8"
        )
        if not isinstance(commits, list):
            return tombstones, blobs

        def fetch_commit(sha: str):
            return _http_get_json(
                f"https://api.github.com/repos/{self.repo_slug}/commits/{sha}"
            )

        commit_details = []
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = [pool.submit(fetch_commit, c["sha"]) for c in commits[:4] if c.get("sha")]
            for fut in as_completed(futures):
                try:
                    commit_details.append(fut.result())
                except Exception:
                    pass

        idx = 1
        for cdata in commit_details:
            sha = cdata.get("sha", "")
            short_sha = sha[:7]
            parents = cdata.get("parents") or []
            parent_sha = parents[0]["sha"] if parents else None
            commit_info = cdata.get("commit") or {}
            author_info = commit_info.get("author") or {}
            author = author_info.get("name", "Unknown")
            death_date = author_info.get("date", "Unknown")
            message = (commit_info.get("message") or "").splitlines()[0][:80]

            for f in cdata.get("files") or []:
                if f.get("status") != "removed":
                    continue
                filepath = f.get("filename", "")
                if not filepath:
                    continue

                tomb_id = f"tomb_gh_del_{idx:03d}"
                idx += 1

                full_content = f"# Excavated from {self.repo_slug} commit {short_sha}\n# File: {filepath}\n"
                if parent_sha:
                    raw_url = f"https://raw.githubusercontent.com/{self.repo_slug}/{parent_sha}/{filepath}"
                    try:
                        full_content = _http_get_text(raw_url, timeout=8)
                    except Exception:
                        pass

                blobs[tomb_id] = full_content
                loc_count = max(1, len(full_content.splitlines()))
                tombstones.append(
                    Tombstone(
                        id=tomb_id,
                        artifact_type="DELETED_FILE",
                        name=os.path.basename(filepath),
                        path=filepath,
                        death_commit=short_sha,
                        author=author,
                        death_date=death_date,
                        cause_of_death=f"Commit: {message}",
                        content_snippet=full_content[:350],
                        resurrectable=True,
                        metadata={"dead_loc": loc_count, "repo": self.repo_slug},
                    )
                )
                if len(tombstones) >= 6:
                    return tombstones, blobs

        return tombstones, blobs

    def _excavate_zombie_symbols(self, branch: str) -> Tuple[List[Tombstone], Dict[str, str]]:
        tree_data = _http_get_json(
            f"https://api.github.com/repos/{self.repo_slug}/git/trees/{branch}?recursive=1"
        )
        tree_items = tree_data.get("tree") or []

        py_paths = []
        for item in tree_items:
            if item.get("type") != "blob":
                continue
            path = item.get("path", "")
            if not path.endswith(".py"):
                continue
            lower = path.lower()
            if any(skip in lower for skip in ("test", "conftest", "setup.py", "docs/", "examples/")):
                continue
            py_paths.append(path)
            if len(py_paths) >= 16:
                break

        if not py_paths:
            return [], {}

        def fetch_raw(path: str) -> Tuple[str, str]:
            url = f"https://raw.githubusercontent.com/{self.repo_slug}/{branch}/{path}"
            return path, _http_get_text(url, timeout=8)

        sources: Dict[str, str] = {}
        with ThreadPoolExecutor(max_workers=6) as pool:
            futures = [pool.submit(fetch_raw, p) for p in py_paths]
            for fut in as_completed(futures):
                try:
                    p, src = fut.result()
                    sources[p] = src
                except Exception:
                    pass

        return scan_python_sources(sources, repo_label=self.repo_slug, commit_label=branch)
