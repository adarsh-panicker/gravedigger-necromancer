from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any

@dataclass
class Tombstone:
    """Represents a dead entity in the repository graveyard."""
    id: str
    artifact_type: str  # 'DELETED_FILE', 'DELETED_FUNCTION', 'ZOMBIE_CODE', 'ABANDONED_BRANCH'
    name: str
    path: str
    death_commit: str
    author: str
    death_date: str
    cause_of_death: str
    content_snippet: str
    line_number: Optional[int] = None
    resurrectable: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ExcavationReport:
    """Consolidated summary of the repository graveyard."""
    repo_path: str
    total_tombstones: int
    deleted_files_count: int
    zombie_functions_count: int
    abandoned_branches_count: int
    dead_loc: int
    tombstones: List[Tombstone] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "repo_path": self.repo_path,
            "total_tombstones": self.total_tombstones,
            "deleted_files_count": self.deleted_files_count,
            "zombie_functions_count": self.zombie_functions_count,
            "abandoned_branches_count": self.abandoned_branches_count,
            "dead_loc": self.dead_loc,
            "tombstones": [t.to_dict() for t in self.tombstones]
        }

@dataclass
class ResurrectionResult:
    """Result of raising a dead artifact back to life."""
    tombstone_id: str
    success: bool
    resurrected_path: str
    patch_path: Optional[str]
    message: str
    diff_preview: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
