"""Behavioral checks for Stage 1; run with unittest discovery from tests/."""

import unittest
from dataclasses import (
    FrozenInstanceError,
    replace
)
from datetime import (
    date,
    datetime,
    timedelta
)
from pathlib import Path
from zoneinfo import ZoneInfo

from conftest import (
    make_period,
    make_source
)

from aegean.config import (
    ProjectPaths,
    TimePolicy
)
from aegean.data.schema import (
    DataKind,
    DeliveryPeriod,
    ForecastStage,
    ImbalancePrice,
    Market,
    MarketPrice,
    RESForecast,
    Side,
    TradeVolume,
    Unit
)


class ContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.period = make_period()
        self.source = make_source()
        self.price = MarketPrice(
            source=self.source,
            period=self.period,
            value=-0.10,
            unit=Unit.EUR_PER_MWH,
            market=Market.DAM,
            bidding_zone="Mainland Greece"
        )

    def test_negative_prices_and_zero_are_valid(self) -> None:
        self.assertEqual(
            first=self.price.value,
            second=-0.10
        )
        zero = replace(
            self.price,
            value=0
        )
        self.assertEqual(
            first=zero.decision_issues(decision_at=self.period.start),
            second=()
        )
        settlement = ImbalancePrice(
            source=self.source,
            period=self.period,
            value=-30,
            unit=Unit.EUR_PER_MWH,
            bidding_zone="Mainland Greece"
        )
        self.assertEqual(
            first=settlement.value,
            second=-30
        )

    def test_missing_value_is_not_zero(self) -> None:
        missing = replace(
            self.price,
            value=None
        )
        self.assertIn(
            member="missing_value",
            container=missing.decision_issues(decision_at=self.period.start)
        )

    def test_nonfinite_and_boolean_values_are_rejected(self) -> None:
        for value in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=value):
                with self.assertRaises(expected_exception=ValueError):
                    replace(
                        self.price,
                        value=value
                    )
        with self.assertRaises(expected_exception=TypeError):
            replace(
                self.price,
                value=True
            )

    def test_invalid_delivery_periods_are_rejected(self) -> None:
        for minutes in (0, -15):
            with self.subTest(minutes=minutes):
                with self.assertRaises(expected_exception=ValueError):
                    make_period(minutes=minutes)

    def test_naive_and_non_utc_record_times_are_rejected(self) -> None:
        naive = self.period.start.replace(tzinfo=None)
        with self.assertRaises(expected_exception=ValueError):
            DeliveryPeriod(
                start=naive,
                end=self.period.end
            )
        local = self.period.start.astimezone(tz=ZoneInfo(key="Europe/Athens"))
        with self.assertRaises(expected_exception=ValueError):
            replace(
                self.source,
                published_at=local
            )

    def test_unresolved_forecast_is_retained_but_not_ready(self) -> None:
        forecast = RESForecast(
            source=make_source(available=False),
            period=None,
            value=7113,
            unit=None,
            stage=ForecastStage.ISP1,
            delivery_date=date(
                year=2025,
                month=10,
                day=12
            ),
            period_index=53,
            scope="aggregate RES; source coverage pending verification"
        )
        self.assertEqual(
            first=forecast.decision_issues(decision_at=self.period.start),
            second=("unknown_available_at", "unknown_delivery_period", "unknown_unit")
        )
        self.assertEqual(
            first=forecast.kind,
            second=DataKind.RES_FORECAST
        )
        self.assertNotIsInstance(
            obj=forecast,
            cls=TradeVolume
        )
        with self.assertRaises(expected_exception=TypeError):
            replace(
                forecast,
                kind="actual"
            )

    def test_revisions_coexist_without_overwriting(self) -> None:
        later_source = make_source(revision="02")
        revised = replace(
            self.price,
            source=later_source,
            value=146.42
        )
        original = replace(
            self.price,
            value=146.33
        )
        records = {original, revised}
        self.assertEqual(
            first=len(records),
            second=2
        )
        self.assertEqual(
            first=original.value,
            second=146.33
        )
        self.assertEqual(
            first=revised.source.revision,
            second="02"
        )

    def test_availability_boundary_and_future_revision(self) -> None:
        published = self.source.published_at
        self.assertEqual(
            first=self.price.decision_issues(decision_at=published),
            second=()
        )
        self.assertIn(
            member="not_yet_available",
            container=self.price.decision_issues(
                decision_at=published - timedelta(seconds=1)
            )
        )
        revised_source = replace(
            self.source,
            revision="02",
            published_at=published + timedelta(days=1),
            available_at=published + timedelta(days=1)
        )
        revised = replace(
            self.price,
            source=revised_source
        )
        self.assertIn(
            member="not_yet_available",
            container=revised.decision_issues(decision_at=published)
        )

    def test_availability_needs_evidence_and_valid_order(self) -> None:
        with self.assertRaises(expected_exception=ValueError):
            replace(
                self.source,
                availability_evidence=None
            )
        with self.assertRaises(expected_exception=ValueError):
            replace(
                self.source,
                available_at=self.source.published_at - timedelta(seconds=1)
            )

    def test_retrieval_time_does_not_invent_availability(self) -> None:
        source = replace(
            make_source(available=False),
            retrieved_at=self.period.start
        )
        self.assertIn(
            member="unknown_available_at",
            container=source.decision_issues(decision_at=self.period.end)
        )

    def test_unknown_revision_is_explicit(self) -> None:
        source = replace(
            self.source,
            revision=None
        )
        self.assertIn(
            member="unknown_revision",
            container=source.decision_issues(decision_at=self.period.start)
        )

    def test_prices_cannot_be_labelled_as_power(self) -> None:
        with self.assertRaises(expected_exception=ValueError):
            replace(
                self.price,
                unit=Unit.MW
            )

    def test_volume_energy_uses_actual_duration(self) -> None:
        for minutes, expected in ((15, 25), (60, 100)):
            with self.subTest(minutes=minutes):
                volume = TradeVolume(
                    source=self.source,
                    period=make_period(minutes=minutes),
                    value=100,
                    unit=Unit.MW,
                    market=Market.DAM,
                    bidding_zone="Mainland Greece",
                    side=Side.SELL,
                    asset="SUPPLY",
                    classification="RES"
                )
                self.assertEqual(
                    first=volume.energy_mwh(),
                    second=expected
                )
                energy = replace(
                    volume,
                    value=expected,
                    unit=Unit.MWH
                )
                self.assertEqual(
                    first=energy.energy_mwh(),
                    second=expected
                )
                with self.assertRaises(expected_exception=ValueError):
                    replace(
                        volume,
                        period=None
                    ).energy_mwh()
                with self.assertRaises(expected_exception=ValueError):
                    replace(
                        volume,
                        unit=None
                    ).energy_mwh()
                with self.assertRaises(expected_exception=ValueError):
                    replace(
                        volume,
                        value=-1
                    )

    def test_records_are_immutable(self) -> None:
        with self.assertRaises(expected_exception=FrozenInstanceError):
            self.price.value = 500


class ConfigurationTests(unittest.TestCase):
    def test_explicit_root_produces_paths_without_creation(self) -> None:
        root = Path.cwd() / "stage1-nonexistent-test-root"
        self.assertFalse(expr=root.exists())
        paths = ProjectPaths(root=root)
        self.assertEqual(
            first=paths.raw,
            second=root / "data" / "raw"
        )
        self.assertEqual(
            first=paths.processed,
            second=root / "data" / "processed"
        )
        self.assertEqual(
            first=paths.outputs,
            second=root / "outputs"
        )
        self.assertFalse(expr=root.exists())
        with self.assertRaises(expected_exception=ValueError):
            ProjectPaths(root=Path("relative"))

    def test_display_timezone_does_not_verify_source(self) -> None:
        policy = TimePolicy()
        self.assertEqual(
            first=policy.internal_timezone,
            second="UTC"
        )
        self.assertEqual(
            first=policy.display_timezone,
            second="Europe/Athens"
        )
        self.assertIsNone(obj=policy.source_timezone)
        with self.assertRaises(expected_exception=ValueError):
            policy.require_source_timezone()
        with self.assertRaises(expected_exception=ValueError):
            TimePolicy(source_timezone="Europe/Athens")

    def test_aware_conversion_preserves_distinct_dst_instants(self) -> None:
        zone = ZoneInfo(key="Europe/Athens")
        first = datetime(
            year=2025, month=10, day=26, hour=3, minute=30, tzinfo=zone, fold=0
        )
        second = first.replace(fold=1)
        first_utc = TimePolicy.to_utc(timestamp=first)
        second_utc = TimePolicy.to_utc(timestamp=second)
        self.assertEqual(
            first=second_utc - first_utc,
            second=timedelta(hours=1)
        )
        with self.assertRaises(expected_exception=ValueError):
            TimePolicy.to_utc(timestamp=first.replace(tzinfo=None))


if __name__ == "__main__":
    unittest.main()
