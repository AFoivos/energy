"""Small synthetic factories shared by the Stage 1 contract tests.

No real spreadsheets, filesystem writes or network access are needed. These
factories also work with unittest discovery; pytest is not required to run them.
"""

from datetime import (
    UTC,
    datetime,
    timedelta
)
from pathlib import Path

from aegean.data.schema import (
    DeliveryPeriod,
    SourceMetadata
)


def make_period(
    *,
    minutes: int = 15
) -> DeliveryPeriod:
    start = datetime(
        year=2025,
        month=10,
        day=12,
        hour=10,
        tzinfo=UTC
    )
    return DeliveryPeriod(
        start=start,
        end=start + timedelta(minutes=minutes)
    )


def make_source(
    *,
    revision: str = "01",
    available: bool = True
) -> SourceMetadata:
    published = datetime(
        year=2025,
        month=10,
        day=11,
        hour=12,
        tzinfo=UTC
    )
    return SourceMetadata(
        source_id="synthetic-test",
        source_file=Path("synthetic.xlsx"),
        source_sheet="Data",
        source_row=2,
        revision=revision,
        published_at=published,
        available_at=published if available else None,
        availability_evidence="Synthetic fixture with explicit publication time" if available else None
    )
