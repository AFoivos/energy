"""Explicit local paths and time policy; importing this module performs no I/O."""

from dataclasses import dataclass
from datetime import (
    UTC,
    datetime
)
from pathlib import Path
from zoneinfo import ZoneInfo


@dataclass(
    frozen=True
)
class ProjectPaths:
    """Derive paths from an explicit absolute root without creating directories."""

    root: Path

    def __post_init__(self) -> None:
        root = Path(self.root)
        if not root.is_absolute():
            raise ValueError("project root must be an absolute path")
        if ".." in root.parts:
            raise ValueError("project root must not contain '..'")
        object.__setattr__(self, "root", root)

    @property
    def raw(self) -> Path:
        return self.root / "data" / "raw"

    @property
    def processed(self) -> Path:
        return self.root / "data" / "processed"

    @property
    def outputs(self) -> Path:
        return self.root / "outputs"


@dataclass(
    frozen=True
)
class TimePolicy:
    """Configure each source separately; a display zone does not validate a source zone.

    Naive timestamps are deliberately not localized here. The reader must first
    resolve the source convention and ambiguous/nonexistent local times.
    """

    source_timezone: str | None = None
    source_timezone_evidence: str | None = None
    display_timezone: str = "Europe/Athens"

    def __post_init__(self) -> None:
        ZoneInfo(key=self.display_timezone)
        if self.source_timezone is not None:
            ZoneInfo(key=self.source_timezone)
            if not self.source_timezone_evidence or not self.source_timezone_evidence.strip():
                raise ValueError("a source timezone requires documented evidence")
        elif self.source_timezone_evidence is not None:
            raise ValueError("timezone evidence requires a source timezone")

    @property
    def internal_timezone(self) -> str:
        return "UTC"

    def require_source_timezone(self) -> ZoneInfo:
        if self.source_timezone is None:
            raise ValueError("source timezone is unverified")
        return ZoneInfo(key=self.source_timezone)

    @staticmethod
    def to_utc(
        timestamp: datetime
    ) -> datetime:
        """Convert an already resolved, aware timestamp. Never guess its timezone."""
        if not isinstance(timestamp, datetime):
            raise TypeError("timestamp must be a datetime")
        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            raise ValueError("timestamp must be timezone-aware")
        return timestamp.astimezone(tz=UTC)
