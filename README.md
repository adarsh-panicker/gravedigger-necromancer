<div align="center">

# ⚡ GraveDigger: The Codebase Necromancer

<p align="center">
  <img src="assets/logo.png" alt="GraveDigger Logo" width="850"/>
</p>

### **Created by Adarsh Panicker**

**Kiroween Hackathon 2026 Submission** | **Track:** Frankenstein 🧟  
*Stitching Git forensic plumbing, AST syntax trees, Kiro agent hooks, and gothic UI into one chimera.*

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Kiroween 2026](https://img.shields.io/badge/Kiroween-Track%20Frankenstein-purple.svg)](https://kiroween.devpost.com/)
[![Kiro Specs & Hooks](https://img.shields.io/badge/Kiro-Specs%20%26%20Hooks%20Ready-00f5d4.svg)](.kiro/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)

</div>

---

## 🪦 The Frankenstein Chimera

Every software repository eventually degrades into a cemetery of dead code:
1. **Buried Files:** Deleted utilities and feature modules lost in deep Git history.
2. **Zombie Code:** Functions, classes, and helpers defined in the codebase that have **zero references** anywhere across the AST.
3. **Abandoned Branches:** Experimental or abandoned branches gathering digital dust.

**GraveDigger** stitches together four disparate technologies into an autonomous developer co-pilot:
* ⛏️ **Low-Level Git Forensic Plumbing:** Uses `diff-filter=D`, tree-deltas, and reflog mining to excavate buried code without clone bloat.
* 🧠 **Static AST Syntax Analysis:** Parses code into Abstract Syntax Trees to detect unreferenced living-dead symbols and compute dead code weight.
* 🤖 **Kiro Agent Hooks & Steering Engine:** Automates event-driven audits on `PostFileSave` and guards against commit bloat on `PreCommit`.
* 🦇 **Gothic TUI & Cemetery Web Dashboard:** An atmospheric, dark-crypt UI with interactive tombstone cards and instant one-click code resurrection.

---

## 📸 Screenshots & Visual Interface

### 🌐 1. The Interactive Cemetery Web Dashboard
> *Browse repository tombstones, inspect dead code snippets, and resurrect artifacts into clean Git patches with a single click.*

<div align="center">
  <img src="assets/dashboard_preview.png" alt="Cemetery Web Dashboard" width="900"/>
</div>

---

### 💻 2. The Gothic Terminal User Interface (TUI)
> *Terminal excavation output displaying excavated tombstones, causes of death, and dead code line count.*

<div align="center">
  <img src="assets/tui_preview.png" alt="GraveDigger Terminal Interface" width="850"/>
</div>

---

## 🏗️ The `/.kiro/` Architecture

GraveDigger strictly follows the mandatory Kiro spec-driven development guidelines:

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

GraveDigger runs on pure Python 3.10+ with zero external runtime dependencies.

### 1. Run the Unit Test Suite
```bash
python -m unittest discover -s tests
```
*(Status: `Ran 3 tests in 0.063s — OK`)*

### 2. Run the Live Demonstration
```bash
python run_demo.py
```

### 3. CLI Commands

#### 🪦 Excavate the Graveyard
```bash
python -m gravedigger.cli dig
```

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

## 🎬 2-Minute Demo Video Pitch Script (For Adarsh Panicker)

Follow this structure for your video recording:

1. **0:00 - 0:25 (The Pitch & Track):**  
   *"Hi everyone, I'm Adarsh Panicker, and this is GraveDigger: The Codebase Necromancer, built for the Kiroween Hackathon's Frankenstein Track. We stitched together low-level Git plumbing, AST syntax tree analysis, Kiro agent hooks, and a gothic dashboard into an autonomous codebase resurrection co-pilot."*
2. **0:25 - 0:55 (Terminal Excavation):**  
   *Run `python -m gravedigger.cli dig`. Point out the cemetery summary, the tombstone cards for deleted files, and the AST scan catching uncalled zombie functions.*
3. **0:55 - 1:25 (Web Cemetery Dashboard):**  
   *Switch to `http://localhost:6660`. Show the interactive cards, click **"⚡ Resurrect Artifact"**, and show the live unified patch generated in `resurrected/`.*
4. **1:25 - 1:50 (The Kiro Integration):**  
   *Open VS Code / editor to show the `/.kiro/` directory. Highlight `steering/architecture.md`, the spec files in `specs/`, and the automated lifecycle hooks in `hooks/`.*
5. **1:50 - 2:00 (Conclusion):**  
   *"GraveDigger turns your dead code graveyard into a treasure trove of reusable assets. Thank you!"*

---

## ⚖️ License & Attribution
* **Author:** Adarsh Panicker
* **License:** [MIT License](LICENSE)
