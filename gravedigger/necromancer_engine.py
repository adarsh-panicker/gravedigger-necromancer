import os
import shutil
from typing import Optional, Dict, Any, List
from .models import Tombstone, ExcavationReport, ResurrectionResult
from .git_archeologist import GitArcheologist
from .ast_scanner import ASTGraveyardScanner

class NecromancerEngine:
    """
    Orchestrates codebase graveyard excavations, zombie diagnostics,
    and automatic code resurrection patch generation.
    """

    def __init__(self, repo_path: str = "."):
        self.repo_path = os.path.abspath(repo_path)
        self.archeologist = GitArcheologist(self.repo_path)
        self.ast_scanner = ASTGraveyardScanner(self.repo_path)
        self.resurrect_dir = os.path.join(self.repo_path, "resurrected")
        self._cached_report: Optional[ExcavationReport] = None

    def run_excavation(self) -> ExcavationReport:
        """Executes full archeological excavation across Git and AST."""
        deleted_files = self.archeologist.excavate_deleted_files()
        abandoned_branches = self.archeologist.excavate_abandoned_branches()
        zombie_code = self.ast_scanner.scan_for_zombie_symbols()

        all_tombstones = deleted_files + abandoned_branches + zombie_code
        dead_loc = sum(t.metadata.get("dead_loc", 15) for t in all_tombstones)

        report = ExcavationReport(
            repo_path=self.repo_path,
            total_tombstones=len(all_tombstones),
            deleted_files_count=len(deleted_files),
            zombie_functions_count=len(zombie_code),
            abandoned_branches_count=len(abandoned_branches),
            dead_loc=dead_loc,
            tombstones=all_tombstones
        )
        self._cached_report = report
        return report

    def resurrect_tombstone(self, tombstone_id: str) -> ResurrectionResult:
        """Brings an excavated dead artifact back to life as a clean patch."""
        if not self._cached_report:
            self.run_excavation()

        target = next((t for t in self._cached_report.tombstones if t.id == tombstone_id), None)
        if not target:
            return ResurrectionResult(
                tombstone_id=tombstone_id,
                success=False,
                resurrected_path="",
                patch_path=None,
                message=f"Tombstone ID '{tombstone_id}' not found in repository graveyard."
            )

        os.makedirs(self.resurrect_dir, exist_ok=True)
        safe_name = os.path.basename(target.path)
        out_file_path = os.path.join(self.resurrect_dir, safe_name)
        patch_file_path = os.path.join(self.resurrect_dir, f"{safe_name}.patch")

        # Fetch full historical content if from git, otherwise use snippet
        full_content = target.content_snippet
        if self.archeologist.is_git_repo and target.metadata.get("raw_commit"):
            raw_sha = target.metadata["raw_commit"]
            git_blob = self.archeologist._run_git(["show", f"{raw_sha}^:{target.path}"])
            if git_blob:
                full_content = git_blob

        # Generate resurrected source with necromancy header
        resurrected_content = (
            f"# ====================================================================\n"
            f"# RESURRECTED ARTIFACT: {target.name}\n"
            f"# Original Path: {target.path}\n"
            f"# Death Commit: {target.death_commit} | Buried: {target.death_date}\n"
            f"# Original Author: {target.author}\n"
            f"# Raised by: GraveDigger (Kiroween Necromancer Engine)\n"
            f"# ====================================================================\n\n"
            f"{full_content}\n"
        )

        with open(out_file_path, "w", encoding="utf-8") as f:
            f.write(resurrected_content)

        # Generate standard git unified diff patch
        patch_diff = (
            f"--- /dev/null\n"
            f"+++ b/{target.path}\n"
            f"@@ -0,0 +1,{len(resurrected_content.splitlines())} @@\n"
            + "\n".join("+" + line for line in resurrected_content.splitlines())
            + "\n"
        )

        with open(patch_file_path, "w", encoding="utf-8") as f:
            f.write(patch_diff)

        return ResurrectionResult(
            tombstone_id=tombstone_id,
            success=True,
            resurrected_path=out_file_path,
            patch_path=patch_file_path,
            message=f"Successfully resurrected '{target.name}' from {target.death_commit} into {out_file_path}!",
            diff_preview=patch_diff[:500]
        )
