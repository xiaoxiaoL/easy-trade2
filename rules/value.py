import config
from data.snapshot import MarketSnapshot


def value_screen(snapshot: MarketSnapshot) -> tuple[int, list[str]]:
    """
    Score a stock against the 5 Graham-style value filters.
    Returns (score, list of passed filter descriptions).
    Score 5/5 = ideal candidate, 3+/5 = worth considering.
    """
    passed = []

    if 0 < snapshot.pe_ratio <= config.VALUE_PE_MAX:
        passed.append(f"P/E={snapshot.pe_ratio:.1f} (target <{config.VALUE_PE_MAX})")

    if 0 < snapshot.pb_ratio <= config.VALUE_PB_MAX:
        passed.append(f"P/B={snapshot.pb_ratio:.2f} (target <{config.VALUE_PB_MAX})")

    if 0 < snapshot.pfcf_ratio <= config.VALUE_PFCF_MAX:
        passed.append(f"P/FCF={snapshot.pfcf_ratio:.1f} (target <{config.VALUE_PFCF_MAX})")

    if 0 < snapshot.debt_equity <= config.VALUE_DE_MAX:
        passed.append(f"D/E={snapshot.debt_equity:.2f} (target <{config.VALUE_DE_MAX})")

    if snapshot.roe >= config.VALUE_ROE_MIN:
        passed.append(f"ROE={snapshot.roe * 100:.1f}% (target >{config.VALUE_ROE_MIN * 100:.0f}%)")

    return len(passed), passed
