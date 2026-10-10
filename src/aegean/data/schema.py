"""Immutable records for market results, forecasts and imbalance prices.

Missing values use None. Unknown metadata can be retained for inspection, but
decision_issues() fails closed. It is an information check, not an execution or
market-gate check, and does not select the latest available revision.
"""

from dataclasses import dataclass
from datetime import (
    date,
    datetime,
    timedelta
)
from enum import StrEnum
from math import isfinite
from numbers import Real
from pathlib import Path
from typing import ClassVar


class Market(StrEnum):
    DAM = "DAM"
    IDA1 = "IDA1"
    IDA2 = "IDA2"
    IDA3 = "IDA3"


class Side(StrEnum):
    BUY = "Buy"
    SELL = "Sell"


class ForecastStage(StrEnum):
    ISP1 = "ISP1"
    ISP2 = "ISP2"
    ISP3 = "ISP3"


class Unit(StrEnum):
    MW = "MW"
    MWH = "MWh"
    EUR_PER_MWH = "EUR/MWh"


class DataKind(StrEnum):
    MARKET_PRICE = "market_price"
    TRADE_VOLUME = "trade_volume"
    RES_FORECAST = "res_forecast"
    IMBALANCE_PRICE = "imbalance_price"


def _text(
    value: str,
    field: str
) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a nonempty string")


def _utc(
    value: datetime,
    field: str
) -> None:
    if not isinstance(value, datetime):
        raise TypeError(f"{field} must be a datetime")
    if value.tzinfo is None or value.utcoffset() != timedelta(seconds=0):
        raise ValueError(f"{field} must be timezone-aware UTC")


@dataclass(
    frozen=True
)
class DeliveryPeriod:
    """Half-open [start, end) interval. Duration follows endpoints, not row count."""

    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        _utc(
            value=self.start,
            field="start"
        )
        _utc(
            value=self.end,
            field="end"
        )
        if self.end <= self.start:
            raise ValueError("delivery end must be later than start")

    @property
    def duration_hours(self) -> float:
        return (self.end - self.start).total_seconds() / 3600


@dataclass(
    frozen=True,
    kw_only=True
)
class SourceMetadata:
    """Provenance for one publication/record; no timestamps are inferred.

    source_row is a one-based Excel row. revision is source-local, not a global
    ordering key. Raw strings retain unresolved source timestamps as evidence.
    """

    source_id: str
    source_file: Path
    source_sheet: str
    revision: str | None = None
    source_row: int | None = None
    checksum_sha256: str | None = None
    published_at: datetime | None = None
    available_at: datetime | None = None
    availability_evidence: str | None = None
    retrieved_at: datetime | None = None
    raw_publication_time: str | None = None
    raw_delivery_time: str | None = None

    def __post_init__(self) -> None:
        _text(
            value=self.source_id,
            field="source_id"
        )
        _text(
            value=self.source_sheet,
            field="source_sheet"
        )
        if not isinstance(self.source_file, Path) or self.source_file == Path("."):
            raise ValueError("source_file must be a nonempty Path")
        if self.revision is not None:
            _text(
                value=self.revision,
                field="revision"
            )
        if self.source_row is not None and (
            type(self.source_row) is not int or self.source_row < 1
        ):
            raise ValueError("source_row must be a positive integer")
        if self.checksum_sha256 is not None:
            digest = self.checksum_sha256
            if not isinstance(digest, str) or len(digest) != 64 or any(
                char not in "0123456789abcdefABCDEF" for char in digest
            ):
                raise ValueError("checksum_sha256 must contain 64 hexadecimal characters")
        for name in ("published_at", "available_at", "retrieved_at"):
            value = getattr(self, name)
            if value is not None:
                _utc(
                    value=value,
                    field=name
                )
        if self.available_at is not None:
            _text(
                value=self.availability_evidence,
                field="availability_evidence"
            )
            if self.published_at is not None and self.available_at < self.published_at:
                raise ValueError("available_at cannot precede published_at")
        elif self.availability_evidence is not None:
            raise ValueError("availability_evidence requires available_at")

    def decision_issues(
        self,
        decision_at: datetime
    ) -> tuple[str, ...]:
        _utc(
            value=decision_at,
            field="decision_at"
        )
        issues = []
        if self.revision is None:
            issues.append("unknown_revision")
        if self.available_at is None:
            issues.append("unknown_available_at")
        elif self.available_at > decision_at:
            issues.append("not_yet_available")
        return tuple(issues)


@dataclass(
    frozen=True,
    kw_only=True
)
class _Record:
    source: SourceMetadata
    period: DeliveryPeriod | None
    value: float | None
    unit: Unit | None

    def __post_init__(self) -> None:
        if not isinstance(self.source, SourceMetadata):
            raise TypeError("source must be SourceMetadata")
        if self.period is not None and not isinstance(self.period, DeliveryPeriod):
            raise TypeError("period must be DeliveryPeriod or None")
        if self.value is not None:
            if isinstance(self.value, bool) or not isinstance(self.value, Real):
                raise TypeError("value must be a real number or None")
            if not isfinite(self.value):
                raise ValueError("value must be finite; use None for missing values")
        if self.unit is not None and not isinstance(self.unit, Unit):
            raise TypeError("unit must be Unit or None")

    def _unit_allowed(
        self,
        *,
        units: tuple[Unit, ...]
    ) -> None:
        if self.unit is not None and self.unit not in units:
            raise ValueError(f"unsupported unit {self.unit}; expected {units}")

    def decision_issues(
        self,
        decision_at: datetime
    ) -> tuple[str, ...]:
        issues = list(
            self.source.decision_issues(
                decision_at=decision_at
            )
        )
        if self.period is None:
            issues.append("unknown_delivery_period")
        if self.value is None:
            issues.append("missing_value")
        if self.unit is None:
            issues.append("unknown_unit")
        return tuple(issues)


@dataclass(
    frozen=True,
    kw_only=True
)
class MarketPrice(_Record):
    market: Market
    bidding_zone: str
    kind: ClassVar[DataKind] = DataKind.MARKET_PRICE

    def __post_init__(self) -> None:
        super().__post_init__()
        if not isinstance(self.market, Market):
            raise TypeError("market must be Market")
        _text(
            value=self.bidding_zone,
            field="bidding_zone"
        )
        self._unit_allowed(
            units=(Unit.EUR_PER_MWH,)
        )


@dataclass(
    frozen=True,
    kw_only=True
)
class TradeVolume(_Record):
    market: Market
    bidding_zone: str
    side: Side
    asset: str
    classification: str
    kind: ClassVar[DataKind] = DataKind.TRADE_VOLUME

    def __post_init__(self) -> None:
        super().__post_init__()
        if not isinstance(self.market, Market) or not isinstance(self.side, Side):
            raise TypeError("market and side must use their enum types")
        for name in ("bidding_zone", "asset", "classification"):
            _text(
                value=getattr(self, name),
                field=name
            )
        self._unit_allowed(
            units=(Unit.MW, Unit.MWH)
        )
        if self.value is not None and self.value < 0:
            raise ValueError("trade volume is nonnegative; direction is stored in side")

    def energy_mwh(self) -> float:
        """Explicit conversion; no relabelling of MW as MWh."""
        if self.value is None:
            raise ValueError("trade volume is missing")
        if self.unit == Unit.MWH:
            return self.value
        if self.unit == Unit.MW and self.period is not None:
            return self.value * self.period.duration_hours
        raise ValueError("energy conversion requires a known unit and duration")


@dataclass(
    frozen=True,
    kw_only=True
)
class RESForecast(_Record):
    stage: ForecastStage
    delivery_date: date
    period_index: int
    scope: str
    kind: ClassVar[DataKind] = DataKind.RES_FORECAST

    def __post_init__(self) -> None:
        super().__post_init__()
        if not isinstance(self.stage, ForecastStage):
            raise TypeError("stage must be ForecastStage")
        if type(self.delivery_date) is not date:
            raise TypeError("delivery_date must be a date")
        if type(self.period_index) is not int or self.period_index < 1:
            raise ValueError("period_index must be a positive integer")
        _text(
            value=self.scope,
            field="scope"
        )
        self._unit_allowed(
            units=(Unit.MW, Unit.MWH)
        )


@dataclass(
    frozen=True,
    kw_only=True
)
class ImbalancePrice(_Record):
    bidding_zone: str
    kind: ClassVar[DataKind] = DataKind.IMBALANCE_PRICE

    def __post_init__(self) -> None:
        super().__post_init__()
        _text(
            value=self.bidding_zone,
            field="bidding_zone"
        )
        self._unit_allowed(
            units=(Unit.EUR_PER_MWH,)
        )
