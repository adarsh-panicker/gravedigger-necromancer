import os
import sys
import argparse
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from .necromancer_engine import NecromancerEngine

# ANSI color codes
C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_RED = "\033[91m"
C_GREEN = "\033[92m"
C_YELLOW = "\033[93m"
C_PURPLE = "\033[95m"
C_CYAN = "\033[96m"
C_GRAY = "\033[90m"

BANNER = f"""{C_PURPLE}
      .---.
     /     \\      {C_BOLD}{C_GREEN}GRAVEDIGGER: THE CODEBASE NECROMANCER{C_RESET}{C_PURPLE}
    | () () |     {C_CYAN}Kiroween Hackathon 2026 // Track: Frankenstein{C_RESET}{C_PURPLE}
     \\  ^  /      {C_BOLD}{C_PURPLE}By Adarsh Panicker{C_RESET}{C_PURPLE}
      |||||       {C_GRAY}Git Archeology + AST Syntax Trees + Kiro Hooks{C_RESET}{C_PURPLE}
      |||||       {C_RED}[+] Raking through the repository cemetery...{C_RESET}{C_PURPLE}
    ========={C_RESET}
"""

def print_tombstone_card(tombstone):
    t_type = tombstone.artifact_type
    badge_color = C_RED if "DELETED" in t_type else (C_YELLOW if "ZOMBIE" in t_type else C_CYAN)

    print(f"{C_BOLD}{badge_color}+----------------------------------------------------------------------+{C_RESET}")
    print(f"{C_BOLD}{badge_color}| [{t_type}] ID: {tombstone.id:<18} Name: {tombstone.name:<25} |{C_RESET}")
    print(f"| {C_GRAY}Path:{C_RESET} {tombstone.path:<62} |")
    print(f"| {C_GRAY}Buried by:{C_RESET} {tombstone.author:<20} {C_GRAY}Date:{C_RESET} {tombstone.death_date:<27} |")
    print(f"| {C_GRAY}Epitaph:{C_RESET} {tombstone.cause_of_death[:60]:<60} |")
    print(f"{C_BOLD}{badge_color}+----------------------------------------------------------------------+{C_RESET}")

def main():
    parser = argparse.ArgumentParser(description="GraveDigger: The Codebase Necromancer (Kiroween)")
    subparsers = parser.add_subparsers(dest="command", help="Necromancer commands")

    # Command: dig
    p_dig = subparsers.add_parser("dig", help="Excavate dead files, zombie code, and abandoned branches")
    p_dig.add_argument("--path", "-p", default=".", help="Target repository path")
    p_dig.add_argument("--json", action="store_true", help="Output raw JSON")

    # Command: resurrect
    p_res = subparsers.add_parser("resurrect", help="Raise a dead tombstone artifact back to life")
    p_res.add_argument("tombstone_id", help="ID of the tombstone to resurrect (e.g., tomb_mock_001)")
    p_res.add_argument("--path", "-p", default=".", help="Target repository path")

    # Command: zombies
    p_zomb = subparsers.add_parser("zombies", help="Scan AST for unreferenced living dead routines")
    p_zomb.add_argument("--path", "-p", default=".", help="Target repository path")

    # Command: web
    p_web = subparsers.add_parser("web", help="Launch the interactive Gothic Graveyard Web Dashboard")
    p_web.add_argument("--port", type=int, default=6660, help="Web dashboard port (default: 6660)")
    p_web.add_argument("--path", "-p", default=".", help="Target repository path")

    # Command: audit (for Kiro hooks)
    p_audit = subparsers.add_parser("audit", help="Automated audit for Kiro pre-commit / post-save hooks")
    p_audit.add_argument("--strict", action="store_true", help="Fail if zombie count exceeds threshold")
    p_audit.add_argument("--path", "-p", default=".", help="Target repository path")

    args = parser.parse_args()

    if not args.command or args.command == "dig":
        repo_path = getattr(args, "path", ".")
        engine = NecromancerEngine(repo_path)
        report = engine.run_excavation()

        if getattr(args, "json", False):
            print(json.dumps(report.to_dict(), indent=2))
            return

        print(BANNER)
        print(f"{C_BOLD}{C_GREEN}[+] Cemetery Excavation Complete for:{C_RESET} {report.repo_path}")
        print(f"    - {C_RED}Deleted Files Excavated:{C_RESET} {report.deleted_files_count}")
        print(f"    - {C_YELLOW}Zombie Functions (AST):{C_RESET} {report.zombie_functions_count}")
        print(f"    - {C_CYAN}Abandoned Branches:{C_RESET} {report.abandoned_branches_count}")
        print(f"    - {C_PURPLE}Estimated Dead Code Weight:{C_RESET} ~{report.dead_loc} LOC\n")

        print(f"{C_BOLD}Discovered Crypt Tombstones:{C_RESET}\n")
        for tomb in report.tombstones:
            print_tombstone_card(tomb)
            print()

        print(f"{C_GREEN}[Tip] Resurrect any artifact with:{C_RESET} python -m gravedigger.cli resurrect <ID>")
        print(f"{C_CYAN}[Tip] Launch visual cemetery with:{C_RESET} python -m gravedigger.cli web\n")

    elif args.command == "resurrect":
        engine = NecromancerEngine(args.path)
        result = engine.resurrect_tombstone(args.tombstone_id)
        if result.success:
            print(f"\n{C_BOLD}{C_GREEN}⚡ [RITUAL COMPLETE] ⚡{C_RESET}")
            print(f"{C_GREEN}{result.message}{C_RESET}")
            print(f"Restored File: {C_BOLD}{result.resurrected_path}{C_RESET}")
            print(f"Unified Patch: {C_BOLD}{result.patch_path}{C_RESET}\n")
            print(f"{C_GRAY}Patch Diff Preview:\n{result.diff_preview}{C_RESET}")
        else:
            print(f"\n{C_RED}[!] Necromancy Failed: {result.message}{C_RESET}\n")

    elif args.command == "zombies":
        engine = NecromancerEngine(args.path)
        zombies = engine.ast_scanner.scan_for_zombie_symbols()
        print(BANNER)
        print(f"{C_YELLOW}[+] Found {len(zombies)} Zombie Routine(s) via AST static analysis:{C_RESET}\n")
        for z in zombies:
            print_tombstone_card(z)
            print()

    elif args.command == "web":
        from .web_dashboard import launch_graveyard_server
        launch_graveyard_server(repo_path=args.path, port=args.port)

    elif args.command == "audit":
        engine = NecromancerEngine(args.path)
        report = engine.run_excavation()
        print(f"[Kiro Hook Audit] Tombstones: {report.total_tombstones} (Zombies: {report.zombie_functions_count})")
        if args.strict and report.zombie_functions_count > 5:
            print(f"{C_RED}[Kiro Guard Alert] Dead code threshold exceeded. Clean up zombie functions before committing.{C_RESET}")
            sys.exit(1)
        sys.exit(0)

if __name__ == "__main__":
    main()
