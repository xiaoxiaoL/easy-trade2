import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date
from data.snapshot import MarketSnapshot
from rules.value import value_screen


def make_snapshot(**kwargs) -> MarketSnapshot:
    defaults = dict(
        ticker="TEST",
        date=date(2026, 1, 1),
        price=100.0,
        pe_ratio=0.0,
        pb_ratio=0.0,
        week52_low=0.0,
        pfcf_ratio=0.0,
        debt_equity=0.0,
        roe=0.0,
    )
    defaults.update(kwargs)
    return MarketSnapshot(**defaults)


def test_all_filters_pass():
    snap = make_snapshot(pe_ratio=10.0, pb_ratio=1.0, pfcf_ratio=12.0, debt_equity=0.3, roe=0.15)
    score, filters = value_screen(snap)
    assert score == 5
    assert len(filters) == 5


def test_no_filters_pass():
    snap = make_snapshot(pe_ratio=30.0, pb_ratio=5.0, pfcf_ratio=25.0, debt_equity=2.0, roe=0.05)
    score, filters = value_screen(snap)
    assert score == 0
    assert filters == []


def test_pe_boundary():
    # Exactly at threshold — should pass
    snap = make_snapshot(pe_ratio=15.0)
    score, _ = value_screen(snap)
    assert score == 1

    # Just over — should fail
    snap = make_snapshot(pe_ratio=15.1)
    score, _ = value_screen(snap)
    assert score == 0


def test_pe_zero_excluded():
    # P/E of 0 means not available — should not count as cheap
    snap = make_snapshot(pe_ratio=0.0)
    score, _ = value_screen(snap)
    assert score == 0


def test_pb_boundary():
    snap = make_snapshot(pb_ratio=1.5)
    score, _ = value_screen(snap)
    assert score == 1

    snap = make_snapshot(pb_ratio=1.51)
    score, _ = value_screen(snap)
    assert score == 0


def test_pfcf_boundary():
    snap = make_snapshot(pfcf_ratio=15.0)
    score, _ = value_screen(snap)
    assert score == 1

    snap = make_snapshot(pfcf_ratio=0.0)  # not available
    score, _ = value_screen(snap)
    assert score == 0


def test_debt_equity_boundary():
    snap = make_snapshot(debt_equity=0.5)
    score, _ = value_screen(snap)
    assert score == 1

    snap = make_snapshot(debt_equity=0.51)
    score, _ = value_screen(snap)
    assert score == 0


def test_roe_boundary():
    snap = make_snapshot(roe=0.10)
    score, _ = value_screen(snap)
    assert score == 1

    snap = make_snapshot(roe=0.09)
    score, _ = value_screen(snap)
    assert score == 0


def test_filter_descriptions_contain_values():
    snap = make_snapshot(pe_ratio=10.0, roe=0.20)
    _, filters = value_screen(snap)
    assert any("P/E=10.0" in f for f in filters)
    assert any("ROE=20.0%" in f for f in filters)


if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    passed = failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL  {t.__name__} — {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
