import subprocess
import os
import re
from typing import List, Optional
from datetime import datetime
from .models import Tombstone

class GitArcheologist:
    """
    Excavates Git commit histories, tree deltas, reflogs, and abandoned branches.
    """

    def __init__(self, repo_path: str = "."):
        self.repo_path = os.path.abspath(repo_path)
        self.is_git_repo = self._check_git_repo()

    def _check_git_repo(self) -> bool:
        try:
            res = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False
            )
            return res.returncode == 0 and "true" in res.stdout.strip().lower()
        except FileNotFoundError:
            return False

    def _run_git(self, args: List[str]) -> str:
        if not self.is_git_repo:
            return ""
        try:
            res = subprocess.run(
                ["git"] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False
            )
            return res.stdout if res.returncode == 0 else ""
        except Exception:
            return ""

    def excavate_deleted_files(self, limit: int = 20) -> List[Tombstone]:
        """Finds files that were historically deleted in the git log."""
        tombstones = []

        if not self.is_git_repo:
            return self._get_fallback_tombstones()

        # Extract deleted files with commit SHA, author, date, and commit subject
        # Format: SHA|Author|Date|Subject
        raw_log = self._run_git([
            "log",
            f"-n{limit}",
            "--diff-filter=D",
            "--summary",
            "--format=COMMIT_META:%h|%an|%ad|%s"
        ])

        if not raw_log:
            return self._get_fallback_tombstones()

        current_meta = None
        tomb_counter = 1

        for line in raw_log.splitlines():
            line = line.strip()
            if line.startswith("COMMIT_META:"):
                meta_parts = line.replace("COMMIT_META:", "").split("|", 3)
                if len(meta_parts) == 4:
                    current_meta = {
                        "sha": meta_parts[0],
                        "author": meta_parts[1],
                        "date": meta_parts[2],
                        "subject": meta_parts[3]
                    }
            elif line.startswith("delete mode ") and current_meta:
                # Format: delete mode 100644 path/to/file.py
                parts = line.split(" ", 4)
                if len(parts) >= 5:
                    file_path = parts[4]
                    # Try to fetch last known content before deletion
                    content = self._run_git(["show", f"{current_meta['sha']}^:{file_path}"])
                    snippet = content[:300] if content else "# [Historical blob archived in commit tree]"

                    tombstones.append(Tombstone(
                        id=f"tomb_git_{tomb_counter:03d}",
                        artifact_type="DELETED_FILE",
                        name=os.path.basename(file_path),
                        path=file_path,
                        death_commit=current_meta["sha"],
                        author=current_meta["author"],
                        death_date=current_meta["date"],
                        cause_of_death=f"Commit: {current_meta['subject']}",
                        content_snippet=snippet,
                        resurrectable=True,
                        metadata={"raw_commit": current_meta["sha"]}
                    ))
                    tomb_counter += 1

        if not tombstones:
            return self._get_fallback_tombstones()

        return tombstones

    def excavate_abandoned_branches(self) -> List[Tombstone]:
        """Detects stale or dead feature branches unmerged for prolonged periods."""
        branches = []
        if not self.is_git_repo:
            return []

        raw_branches = self._run_git([
            "for-each-ref",
            "--sort=-committerdate",
            "--format=%(refname:short)|%(committerdate:relative)|%(authorname)|%(subject)",
            "refs/heads/"
        ])

        idx = 1
        for line in raw_branches.splitlines():
            parts = line.strip().split("|")
            if len(parts) >= 4:
                b_name, b_date, b_author, b_subj = parts[0], parts[1], parts[2], parts[3]
                # Filter out main / master / trunk
                if b_name not in ["main", "master", "trunk", "development", "dev"]:
                    branches.append(Tombstone(
                        id=f"tomb_branch_{idx:03d}",
                        artifact_type="ABANDONED_BRANCH",
                        name=f"branch/{b_name}",
                        path=f"refs/heads/{b_name}",
                        death_commit="HEAD",
                        author=b_author,
                        death_date=b_date,
                        cause_of_death=f"Abandoned branch: {b_subj}",
                        content_snippet=f"# Branch '{b_name}' last active {b_date} by {b_author}",
                        resurrectable=True
                    ))
                    idx += 1
        return branches

    def _get_fallback_tombstones(self) -> List[Tombstone]:
        """Provides realistic demonstration artifacts when initializing fresh repos."""
        return [
            Tombstone(
                id="tomb_mock_001",
                artifact_type="DELETED_FILE",
                name="legacy_audio_dsp.py",
                path="src/dsp/legacy_audio_dsp.py",
                death_commit="e4b89fa",
                author="Dr. Victor Frankenstein <victor@necro.dev>",
                death_date="Fri Oct 13 23:59:00 2026",
                cause_of_death="Refactored audio pipeline into web-audio bridge",
                content_snippet=(
                    "def compute_fast_fourier_coefficients(signal_buffer):\n"
                    "    '''High performance FFT calculation for retro spectrum visualizer.'''\n"
                    "    import math\n"
                    "    # Real-time DSP frequency binning..."
                ),
                resurrectable=True
            ),
            Tombstone(
                id="tomb_mock_002",
                artifact_type="DELETED_FILE",
                name="retro_skin_loader.py",
                path="plugins/themes/retro_skin_loader.py",
                death_commit="7c19ad4",
                author="Igor <assistant@laboratory.org>",
                death_date="Tue Oct 28 03:14:00 2026",
                cause_of_death="Deprecated WSZ skin format support in favor of modern CSS",
                content_snippet=(
                    "class WinampSkinParser:\n"
                    "    def extract_bitmaps_from_wsz(self, archive_stream):\n"
                    "        '''Extracts main.bmp, cbuttons.bmp, and pledit.bmp...'''"
                ),
                resurrectable=True
            )
        ]
