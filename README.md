# ⚡ GraveDigger: The Codebase Necromancer

> **Kiroween Hackathon 2026 Submission**  
> **Track:** Frankenstein 🧟  
> **Repository:** Public GitHub Repository (MIT Licensed)  
> **Kiro Integration:** Full `/.kiro/` architecture (`steering/`, `specs/`, `hooks/`)

---

## 💀 Overview: The Frankenstein Chimera

Codebases are graveyards of dead ideas: abandoned feature branches, deleted helper routines, forgotten refactors, and living "zombie" functions that linger uncalled for years.

**GraveDigger** stitches together a terrifyingly powerful chimera of four disparate technologies into one unified tool:
1. **Low-level Git Archeology:** Mines commit trees (`diff-filter=D`, tree-deltas, reflogs) to excavate buried files and abandoned branches.
2. **Static Abstract Syntax Tree (AST) Analysis:** Walks code graphs to detect unreferenced living-dead functions ("zombie code") and calculate dead code weight.
3. **Kiro Agent Hooks & Steering Engine:** Event-driven automation that triggers audits on `PostFileSave` and guards against commit bloat on `PreCommit`.
4. **Gothic TUI & Cemetery Web Dashboard:** An atmospheric, dark-crypt interface with interactive tombstone cards and one-click code resurrection.

---

## 🏗️ The `/.kiro/` Architecture

Per Kiroween requirements, the project is steered and governed by the root `/.kiro` system:

```
/.kiro/
├── steering/
│   ├── architecture.md       # High-level system context, AST models, and flows
│   └── conventions.md        # Codebase standards, typing, and Kiro compliance
├── specs/
│   └── gravedigger-core/
│       ├── requirements.md   # Functional specs & user stories
│       ├── design.md         # Technical architecture & JSON models
│       └── tasks.md          # Sequenced execution checklist
└── hooks/
    ├── post-file-save.json   # Auto-detects zombie routines on file save
    └── pre-commit-audit.json # Blocks burial of critical functions before commit
```

---

## 🚀 Quickstart & Verification

GraveDigger is built using pure Python 3.10+ with zero external runtime dependencies.

### 1. Run the Unit Test Suite
```bash
python -m unittest discover -s tests
```

### 2. Run the Live Demonstration
```bash
python run_demo.py
```

### 3. CLI Commands

#### 🪦 Excavate the Codebase Graveyard
```bash
python -m gravedigger.cli dig
```
*Outputs excavated tombstones for deleted files, stale branches, and zombie AST functions.*

#### ⚡ Resurrect a Dead Artifact
```bash
python -m gravedigger.cli resurrect tomb_mock_001
```
*Restores the buried file into `resurrected/` and generates a unified `.patch` ready for git pull request submission.*

#### 🧟 Scan AST for Living-Dead Zombie Code
```bash
python -m gravedigger.cli zombies
```

#### 🌐 Launch the Interactive Web Dashboard
```bash
python -m gravedigger.cli web --port 6660
```
*Opens `http://localhost:6660` with a dark-crypt UI, tombstone cards, and live resurrection diff previews.*

#### 🛡️ Kiro Hook Audit (CI / Git Hook Mode)
```bash
python -m gravedigger.cli audit --strict
```

---

## 🎬 2-Minute Demo Video Pitch Script (For Devpost)

1. **0:00 - 0:30 (The Problem & The Track):**  
   *"Welcome to GraveDigger, built for Kiroween's Frankenstein track. We stitched together Git forensic plumbing, AST syntax analysis, Kiro agent hooks, and a gothic dashboard to solve code rot."*
2. **0:30 - 1:00 (The Excavation):**  
   *Show running `python -m gravedigger.cli dig` in the terminal. Show the ASCII crypt banner, excavated deleted files, and detected zombie functions.*
3. **1:00 - 1:30 (The Resurrection):**  
   *Show `python -m gravedigger.cli resurrect <id>`. Explain how GraveDigger extracts the historical blob and writes a clean, ready-to-merge unified git patch.*
4. **1:30 - 2:00 (The Web Cemetery & Kiro Hooks):**  
   *Show the browser dashboard at `localhost:6660` with animated tombstone cards, click 'Resurrect', and highlight the `/.kiro` steering and hooks running in the background.*

---

## ⚖️ License
Distributed under the **MIT License**. See `LICENSE` for details.
