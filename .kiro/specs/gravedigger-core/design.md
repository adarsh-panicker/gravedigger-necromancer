# Spec: GraveDigger Technical Architecture & Design

## 1. System Components

### 1.1 `GitArcheologist`
* Uses `git log --diff-filter=D --summary` to detect historical file deletions.
* Extracts commit metadata, commit messages, and the precise blob content from the commit immediately preceding deletion (`git show <sha>^:<file>`).
* Inspects local and remote branches to detect stale/dead feature branches.

### 1.2 `ASTGraveyardScanner`
* Utilizes Python's built-in `ast` module (`ast.parse`, `ast.walk`, `ast.NodeVisitor`).
* Constructs two sets:
  * `DefinedSymbols`: all `FunctionDef`, `AsyncFunctionDef`, `ClassDef`.
  * `ReferencedSymbols`: all `Call`, `Name`, `Attribute` occurrences.
* Set difference `DefinedSymbols - ReferencedSymbols` identifies zombie routines that can either be purged or cataloged.

### 1.3 `NecromancerEngine`
* Orchestrates excavation results from `GitArcheologist` and `ASTGraveyardScanner`.
* Synthesizes repair strategies:
  * Restores deleted blobs into `resurrected/` destination.
  * Formats unified Git diffs and patch headers.
  * Emits event telemetry for Kiro hooks.

### 1.4 `GraveyardDashboard`
* Built-in HTTP server using `http.server` serving a rich, atmospheric dark-gothic UI.
* Real-time WebSocket or REST JSON endpoints:
  * `GET /api/graveyard`: returns JSON list of dead files, zombie functions, and branches.
  * `POST /api/resurrect`: triggers instant restoration and generates a patch.

## 2. Data Models (JSON Schema)
```json
{
  "tombstones": [
    {
      "id": "tomb_001",
      "type": "DELETED_FUNCTION",
      "name": "calculate_legacy_metrics",
      "file": "utils/analytics.py",
      "deleted_at_commit": "a1b2c3d",
      "author": "Dr. Frankenstein <dev@lab.io>",
      "death_date": "2025-10-31",
      "cause_of_death": "Refactored during v2 migration",
      "code_snippet": "def calculate_legacy_metrics(): ...",
      "resurrectable": true
    }
  ]
}
```
