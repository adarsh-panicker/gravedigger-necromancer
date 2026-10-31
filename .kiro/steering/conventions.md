# GraveDigger: Coding Standards & Steering Conventions

## 1. Codebase Standards
* **Language & Runtime:** Python 3.10+ compatible across Linux, macOS, and Windows.
* **Standard Library Priority:** Prioritize standard library (`ast`, `subprocess`, `argparse`, `json`, `dataclasses`, `http.server`) to minimize dependency weight while maximizing portability.
* **Typing & Documentation:** All functions and methods must contain type hints and clear docstrings explaining the archeology / necromancy logic.

## 2. Kiro Alignment Rules
* The `.kiro/` directory must remain tracked in git at all times and never added to `.gitignore`.
* Agent tasks must follow the Kiro Spec format (`requirements.md`, `design.md`, `tasks.md`).
* Hooks must use standardized JSON configurations triggered by lifecycle events (`PostFileSave`, `PreCommit`).
