# Spec: GraveDigger Core Engine Requirements

## User Stories & Functional Requirements

### 1. Codebase Graveyard Archeology
* **FR-1.1:** The system shall scan Git commit logs, branch histories, and tree deltas to locate deleted source code files and functions.
* **FR-1.2:** The system shall identify orphaned or stale branches that have not seen commits for > 30 days.
* **FR-1.3:** The system shall extract the exact commit SHA, deletion author, timestamp, and diff for every excavated graveyard artifact.

### 2. AST Static Analysis
* **FR-2.1:** The system shall parse repository source files into Abstract Syntax Trees to construct symbol dependency graphs.
* **FR-2.2:** The system shall detect "Zombie Code": functions, classes, and helper routines defined in the repository that are unreferenced and never called anywhere.
* **FR-2.3:** The system shall calculate dead code weight (lines of code, byte count, cyclomatic complexity).

### 3. Necromancy & Resurrection Patching
* **FR-3.1:** The user shall be able to resurrect any excavated function or file with a single CLI command or dashboard click.
* **FR-3.2:** The Necromancer Engine shall automatically refactor resurrected code to resolve import errors against current HEAD.
* **FR-3.3:** The engine shall output clean Git patch files (`.patch`) ready for review and pull request creation.

### 4. Interactive Surfaces
* **FR-4.1:** A gothic terminal UI (TUI) featuring tombstone meters, ASCII crypt art, and interactive excavation commands.
* **FR-4.2:** A standalone zero-dependency web dashboard visualizing the repository cemetery with interactive "Resurrect" buttons.
