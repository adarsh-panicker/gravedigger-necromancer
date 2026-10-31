import os
import sys
import shutil
import tempfile
import time

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from gravedigger.necromancer_engine import NecromancerEngine
from gravedigger.cli import print_tombstone_card, BANNER, C_BOLD, C_GREEN, C_RESET, C_CYAN, C_RED

def run_live_demonstration():
    print(BANNER)
    print(f"{C_BOLD}{C_GREEN}=== GRAVEDIGGER LIVE RITUAL DEMONSTRATION ==={C_RESET}\n")

    # Step 1: Create a mock playground repository
    demo_dir = tempfile.mkdtemp(prefix="gravedigger_cemetery_")
    print(f"[1] Initializing playground codebase at: {demo_dir}")

    # Create active code
    math_lib = os.path.join(demo_dir, "vector_math.py")
    with open(math_lib, "w") as f:
        f.write(
            "def calculate_vector_dot(v1, v2):\n"
            "    '''Active living routine.'''\n"
            "    return sum(x * y for x, y in zip(v1, v2))\n\n"
            "def zombie_matrix_inversion(m):\n"
            "    '''Abandoned zombie function with zero callers in the AST.'''\n"
            "    return [[1, 0], [0, 1]]\n\n"
            "result = calculate_vector_dot([1, 2], [3, 4])\n"
            "print('Result:', result)\n"
        )

    time.sleep(0.5)

    # Step 2: Excavate
    print("\n[2] Excavating repository cemetery (Git Logs + AST Syntax Trees)...")
    engine = NecromancerEngine(demo_dir)
    report = engine.run_excavation()

    print(f"\n[+] Total Cemetery Artifacts: {report.total_tombstones}")
    print(f"[+] Deleted Git Blobs: {report.deleted_files_count}")
    print(f"[+] Zombie AST Routines: {report.zombie_functions_count}")
    print(f"[+] Dead Code Weight: ~{report.dead_loc} LOC\n")

    time.sleep(0.5)
    print(f"{C_BOLD}Displaying Excavated Tombstones:{C_RESET}\n")
    for t in report.tombstones:
        print_tombstone_card(t)
        print()

    time.sleep(0.5)

    # Step 3: Resurrect an artifact
    target = report.tombstones[0]
    print(f"[3] Raising tombstone '{target.id}' ({target.name}) from the dead...")
    res = engine.resurrect_tombstone(target.id)

    if res.success:
        print(f"\n{C_BOLD}{C_GREEN}⚡ RITUAL SUCCEEDED! ⚡{C_RESET}")
        print(f"Resurrected Source: {res.resurrected_path}")
        print(f"Unified Git Patch: {res.patch_path}")
        print(f"\n{C_CYAN}Patch Preview Header:{C_RESET}\n{res.diff_preview}\n")

    # Cleanup
    shutil.rmtree(demo_dir, ignore_errors=True)
    print(f"{C_BOLD}{C_GREEN}=== DEMONSTRATION COMPLETE: ALL SYSTEMS NOMINAL ==={C_RESET}\n")

if __name__ == "__main__":
    run_live_demonstration()
