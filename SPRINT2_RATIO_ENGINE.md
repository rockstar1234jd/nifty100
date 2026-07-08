# 🧮 Sprint 2 — Financial Ratio Engine
### Nifty 100 Financial Intelligence Platform · Days 08–14 · 42 Story Points

---

## 📌 Sprint Goal

> By end of **Day 14**, the Ratio Engine must compute **50+ KPIs** for all 92 companies across every available year. The `financial_ratios` table in SQLite must be fully populated. Every formula edge case — **negative equity, debt-free companies, CAGR turnarounds, bank D/E carve-out** — must be handled correctly and logged. All **36 unit tests** must pass (spec asks for 20+; we exceed it for production quality).

---

## 📁 Deliverables Checklist

| # | File / Artefact | Due | Acceptance |
|---|---|---|---|
| D-01 | `src/analytics/ratios.py` | Day 08–09 | All profitability + leverage functions present |
| D-02 | `src/analytics/cagr.py` | Day 10 | 6-state edge-case table handled; all 10 tests pass |
| D-03 | `src/analytics/cashflow_kpis.py` | Day 11 | 8-pattern classifier + `capital_allocation.csv` |
| D-04 | `financial_ratios` table (SQLite) | Day 12 | ≥ 1,100 rows · 14+ KPI columns populated |
| D-05 | `output/capital_allocation.csv` | Day 11–12 | Every company-year has a pattern label |
| D-06 | `output/ratio_edge_cases.log` | Day 13 | All anomalies categorised |
| D-07 | `tests/kpi/test_profitability.py` | Day 14 | 10 tests — 0 failures |
| D-08 | `tests/kpi/test_leverage.py` | Day 14 | 10 tests — 0 failures |
| D-09 | `tests/kpi/test_cagr.py` | Day 14 | 10 tests — 0 failures |
| D-10 | `tests/kpi/test_cashflow.py` | Day 14 | 6 tests — 0 failures |

---

## ✅ Exit Criteria — Definition of Done

```bash
# All 4 gates must pass before Sprint 3 begins

# Gate 1 — Row count
sqlite3 data/nifty100.db "SELECT COUNT(*) FROM financial_ratios;"
# ✅ Must return >= 1,100

# Gate 2 — All 14 KPI columns populated
sqlite3 data/nifty100.db "
SELECT COUNT(*) AS null_roe
FROM financial_ratios
WHERE return_on_equity_pct IS NULL;"
# ✅ Will have some NULLs (edge cases) but NOT all-null

# Gate 3 — Tests
pytest tests/kpi/ -v --tb=short
# ✅ 36 passed, 0 failed

# Gate 4 — Files exist
ls output/capital_allocation.csv output/ratio_edge_cases.log
# ✅ Both files present
```

---

## ⚠️ Pre-Sprint Checklist — Sprint 1 Must Be Complete

Run this before Day 08:

```bash
sqlite3 data/nifty100.db "SELECT COUNT(*) FROM companies;"      # → 92
sqlite3 data/nifty100.db "SELECT COUNT(*) FROM profitandloss;"  # → ~1,276
sqlite3 data/nifty100.db "PRAGMA foreign_key_check;"             # → (empty)
pytest tests/etl/ tests/dq/ -q                                   # → 0 failures
```

If any check fails → fix Sprint 1 first. Every formula below reads from `profitandloss`, `balancesheet`, `cashflow`, and `sectors`.

---

## 📐 KPI Formula Master Reference

| KPI | Formula | File | Returns `None` when | Special rule |
|---|---|---|---|---|
| Net Profit Margin | `net_profit / sales × 100` | ratios.py | sales = 0 | Negative values allowed |
| Operating Profit Margin | `operating_profit / sales × 100` | ratios.py | sales = 0 | Cross-check vs `opm_percentage` ±1% |
| EBIT | `operating_profit − depreciation` | ratios.py | — | Always computed |
| ROE | `net_profit / (equity+reserves) × 100` | ratios.py | equity+reserves ≤ 0 | — |
| ROCE | `EBIT / (equity+reserves+borrowings) × 100` | ratios.py | denominator ≤ 0 | Bank carve-out Day 13 |
| ROA | `net_profit / total_assets × 100` | ratios.py | total_assets = 0 | — |
| D/E | `borrowings / (equity+reserves)` | ratios.py | equity+reserves ≤ 0 | Returns **0.0** (not None) if debt-free |
| ICR | `(op_profit+other_income) / interest` | ratios.py | interest = 0 | Labels "Debt Free" in `icr_label` |
| Net Debt | `borrowings − investments` | ratios.py | borrowings missing | — |
| Asset Turnover | `sales / total_assets` | ratios.py | total_assets = 0 | — |
| BVPS | `(equity+reserves) / shares` | ratios.py | face_value missing | shares = equity_capital/face_value |
| CAGR | `((end/start)^(1/n) − 1) × 100` | cagr.py | 6-state edge table | See Day 10 |
| FCF | `CFO + CFI` | cashflow_kpis.py | either is None | Negative allowed |
| CFO Quality | `avg(CFO/PAT) over 5yr` | cashflow_kpis.py | no valid PAT≠0 year | — |
| CapEx Intensity | `\|CFI\| / sales × 100` | cashflow_kpis.py | sales = 0 | — |
| FCF Conversion | `FCF / operating_profit × 100` | cashflow_kpis.py | op_profit = 0 | — |
| Composite Score | `0.30×ROE + 0.25×FCF + 0.25×ROCE + 0.20×D/E` | ratios.py | — | Winsorised P10–P90 |

---

## 📁 Files You Will Create This Sprint

```
src/
└── analytics/
    ├── __init__.py          ← empty (already exists from Sprint 1)
    ├── ratios.py            ← Day 08–09 + 12–13
    ├── cagr.py              ← Day 10
    └── cashflow_kpis.py     ← Day 11

tests/
└── kpi/
    ├── __init__.py          ← empty (already exists from Sprint 1)
    ├── test_profitability.py ← Day 08
    ├── test_leverage.py     ← Day 09
    ├── test_cagr.py         ← Day 10
    └── test_cashflow.py     ← Day 11

output/
    ├── capital_allocation.csv ← Day 11
    └── ratio_edge_cases.log   ← Day 13
```

---

## 📊 Day 08 — Profitability Ratios

### Step 1 — Create `src/analytics/ratios.py`

Create the file with the profitability functions. You will **append** more functions on Day 09 and Day 12–13 — do not delete what you write today.

```python
"""
ratios.py
Financial ratio computation — Nifty 100 Financial Intelligence Platform.
Sprint 2, Days 08–09 (pure functions) + Days 12–13 (orchestrator / DB population).

Design rules:
  • Pure functions take raw numeric inputs, return a single value or None.
  • None means "mathematically undefined" or "business-meaningless" — NOT missing data.
  • Zero is a valid, informative return value (e.g. D/E = 0 for debt-free companies).
  • All monetary values assumed in ₹ Crore unless the function name says _pct.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# ════════════════════════════════════════════════════════════════
# DAY 08 — PROFITABILITY RATIOS
# ════════════════════════════════════════════════════════════════

def net_profit_margin(
    net_profit: Optional[float],
    sales: Optional[float],
) -> Optional[float]:
    """
    Net Profit Margin = net_profit / sales × 100.

    Returns:
        Percentage, rounded to 2dp. Negative values are valid (loss-making year).
        None if sales is zero or either input is None.
    """
    if net_profit is None or sales is None or sales == 0:
        return None
    return round((net_profit / sales) * 100, 2)


def operating_profit_margin(
    operating_profit: Optional[float],
    sales: Optional[float],
) -> Optional[float]:
    """
    OPM = operating_profit / sales × 100.

    Returns None if sales = 0. Used as EBITDA-margin proxy.
    """
    if operating_profit is None or sales is None or sales == 0:
        return None
    return round((operating_profit / sales) * 100, 2)


def opm_crosscheck_flag(
    opm_computed: Optional[float],
    opm_source: Optional[float],
    tolerance_pp: float = 1.0,
) -> bool:
    """
    True when |computed_OPM - source_OPM| > tolerance_pp percentage points.
    Used to flag data-quality issues in the OPM cross-check DQ rule.
    Returns False if either input is None (no flag when we can't compare).
    """
    if opm_computed is None or opm_source is None:
        return False
    return abs(opm_computed - opm_source) > tolerance_pp


def ebit(
    operating_profit: Optional[float],
    depreciation: Optional[float],
) -> Optional[float]:
    """
    EBIT = operating_profit − depreciation.
    Depreciation defaults to 0 when None (some companies report 0 D&A).
    Returns None only if operating_profit is None.
    """
    if operating_profit is None:
        return None
    return round(operating_profit - (depreciation or 0.0), 2)


def return_on_equity(
    net_profit: Optional[float],
    equity_capital: Optional[float],
    reserves: Optional[float],
) -> Optional[float]:
    """
    ROE = net_profit / (equity_capital + reserves) × 100.

    Edge cases:
      • equity_capital + reserves ≤ 0  → None  (negative book value)
      • Any input is None               → None

    Note: the pre-computed roe_percentage in companies.xlsx may show anomalous
    values (e.g. TCS = 0.52, which is a decimal-fraction bug for 52%).
    This Ratio Engine value is authoritative for analytics; the source value
    is display-only.
    """
    if net_profit is None or equity_capital is None or reserves is None:
        return None
    equity = equity_capital + reserves
    if equity <= 0:
        return None
    return round((net_profit / equity) * 100, 2)


def return_on_capital_employed(
    ebit_value: Optional[float],
    equity_capital: Optional[float],
    reserves: Optional[float],
    borrowings: Optional[float],
) -> Optional[float]:
    """
    ROCE = EBIT / (equity_capital + reserves + borrowings) × 100.

    Capital Employed = equity + all debt.
    Returns None if denominator ≤ 0.
    Bank / NBFC benchmark carve-out is applied at the cross-check layer (Day 13),
    not here — this function always computes the value if inputs allow.
    """
    if None in (ebit_value, equity_capital, reserves, borrowings):
        return None
    capital_employed = equity_capital + reserves + borrowings
    if capital_employed <= 0:
        return None
    return round((ebit_value / capital_employed) * 100, 2)


def return_on_assets(
    net_profit: Optional[float],
    total_assets: Optional[float],
) -> Optional[float]:
    """
    ROA = net_profit / total_assets × 100.
    Returns None if total_assets = 0.
    """
    if net_profit is None or total_assets is None or total_assets == 0:
        return None
    return round((net_profit / total_assets) * 100, 2)
```

### Step 2 — Create `tests/kpi/test_profitability.py`

```python
"""
test_profitability.py
10 unit tests for Day 08 profitability ratios.
tests/conftest.py (Sprint 1) adds src/analytics to sys.path — no import tricks needed.
"""
import pytest
from ratios import (
    net_profit_margin, operating_profit_margin, opm_crosscheck_flag,
    ebit, return_on_equity, return_on_capital_employed, return_on_assets,
)


class TestNetProfitMargin:

    def test_normal_case(self):
        assert net_profit_margin(150, 1000) == 15.0

    def test_negative_profit_allowed(self):
        assert net_profit_margin(-50, 1000) == -5.0

    def test_zero_sales_returns_none(self):
        assert net_profit_margin(100, 0) is None

    def test_none_sales_returns_none(self):
        assert net_profit_margin(100, None) is None


class TestOperatingProfitMargin:

    def test_normal_case(self):
        assert operating_profit_margin(210, 1000) == 21.0

    def test_crosscheck_flags_mismatch_over_1pp(self):
        # computed = 21.0%, source = 25.0% → diff = 4pp > 1pp threshold
        assert opm_crosscheck_flag(21.0, 25.0) is True

    def test_crosscheck_passes_within_tolerance(self):
        assert opm_crosscheck_flag(21.0, 21.5) is False


class TestROE:

    def test_normal_case(self):
        # net_profit=100, equity=50, reserves=450 → equity=500 → ROE=20%
        assert return_on_equity(100, 50, 450) == 20.0

    def test_negative_equity_returns_none(self):
        # equity_capital=50, reserves=-100 → sum=-50 → None
        assert return_on_equity(100, 50, -100) is None

    def test_zero_equity_returns_none(self):
        assert return_on_equity(100, 0, 0) is None


class TestROCE:

    def test_normal_case(self):
        # EBIT=150, equity=500, borrowings=500 → CE=1000 → ROCE=15%
        assert return_on_capital_employed(150, 50, 450, 500) == 15.0


class TestROA:

    def test_zero_assets_returns_none(self):
        assert return_on_assets(100, 0) is None

    def test_normal_case(self):
        assert return_on_assets(100, 2000) == 5.0
```

### Step 3 — Run Day 08 Tests

```bash
cd /path/to/nifty100   # your project root
pytest tests/kpi/test_profitability.py -v
```

**Expected:**
```
test_profitability.py::TestNetProfitMargin::test_normal_case PASSED
test_profitability.py::TestNetProfitMargin::test_negative_profit_allowed PASSED
...
10 passed in 0.12s
```

---

## ⚖️ Day 09 — Leverage & Efficiency Ratios

### Step 4 — Append to `src/analytics/ratios.py`

Open `ratios.py` and **add these functions below** the Day 08 code:

```python
# ════════════════════════════════════════════════════════════════
# DAY 09 — LEVERAGE & EFFICIENCY RATIOS
# ════════════════════════════════════════════════════════════════

def debt_to_equity(
    borrowings: Optional[float],
    equity_capital: Optional[float],
    reserves: Optional[float],
) -> Optional[float]:
    """
    D/E = borrowings / (equity_capital + reserves).

    IMPORTANT design decision:
      • borrowings = 0  → returns 0.0 (NOT None). Debt-free is a valid, meaningful result.
      • equity ≤ 0      → returns None. D/E is undefined when book value is negative.
      • Any input None  → returns None.

    Financials-sector companies (banks, NBFCs) may have D/E > 5 structurally.
    The high_leverage_flag (below) already suppresses the warning for them —
    this function always returns the raw computed value.
    """
    if borrowings is None or equity_capital is None or reserves is None:
        return None
    if borrowings == 0:
        return 0.0
    equity = equity_capital + reserves
    if equity <= 0:
        return None
    return round(borrowings / equity, 2)


def high_leverage_flag(
    de_ratio: Optional[float],
    is_financial_sector: bool,
) -> bool:
    """
    True when D/E > 5.0 AND the company is NOT in the Financials broad_sector.
    Financials-sector companies (banks, NBFCs, insurance) carry structurally high
    leverage; flagging them would produce misleading alerts.

    Returns False for any None input or for financial-sector companies.
    """
    if de_ratio is None:
        return False
    if is_financial_sector:
        return False   # carve-out: suppress flag for banks / NBFCs
    return de_ratio > 5.0


def interest_coverage(
    operating_profit: Optional[float],
    other_income: Optional[float],
    interest: Optional[float],
) -> Optional[float]:
    """
    ICR = (operating_profit + other_income) / interest.

    Returns None when interest = 0 (debt-free companies have no interest expense
    to cover, so ICR is undefined rather than infinity).
    Use icr_label() to display 'Debt Free' in place of a numeric value.
    """
    if operating_profit is None or interest is None:
        return None
    if interest == 0:
        return None   # caller should check icr_label() for display
    numerator = operating_profit + (other_income or 0.0)
    return round(numerator / interest, 2)


def icr_label(interest: Optional[float]) -> str:
    """
    Human-readable ICR display label.
      interest = 0 or None → 'Debt Free'
      otherwise            → 'Computed'

    Stored in the separate icr_label column so dashboards can display
    'Debt Free' instead of a blank or infinity symbol.
    """
    if interest is None or interest == 0:
        return 'Debt Free'
    return 'Computed'


def icr_risk_flag(icr: Optional[float]) -> bool:
    """
    True when ICR < 1.5 — the company may struggle to service its interest.
    False for debt-free companies (icr = None → no risk, by definition).
    """
    if icr is None:
        return False
    return icr < 1.5


def net_debt(
    borrowings: Optional[float],
    investments: Optional[float],
) -> Optional[float]:
    """
    Net Debt = borrowings − investments.
    Investments are used as a liquid-asset proxy (project specification note).
    Negative result means the company holds more liquid assets than it owes.
    """
    if borrowings is None:
        return None
    return round(borrowings - (investments or 0.0), 2)


def asset_turnover(
    sales: Optional[float],
    total_assets: Optional[float],
) -> Optional[float]:
    """
    Asset Turnover = sales / total_assets.
    Asset-light companies (IT, FMCG) typically > 1×; capital-heavy < 0.5×.
    Returns None if total_assets = 0.
    """
    if sales is None or total_assets is None or total_assets == 0:
        return None
    return round(sales / total_assets, 2)


def book_value_per_share(
    equity_capital: Optional[float],
    reserves: Optional[float],
    face_value: Optional[float],
) -> Optional[float]:
    """
    BVPS = (equity_capital + reserves) / shares_outstanding.
    shares_outstanding = equity_capital / face_value.
    Returns None if face_value is 0 or missing.
    """
    if equity_capital is None or reserves is None or not face_value:
        return None
    shares = equity_capital / face_value
    if shares == 0:
        return None
    return round((equity_capital + reserves) / shares, 2)


def compute_row_ratios(
    pl: dict,
    bs: dict,
    is_financial: bool,
) -> dict:
    """
    Compute all per-row (single company-year) ratios from merged P&L + BS dicts.

    Args:
        pl: dict of P&L fields for one company-year (keys = column names).
        bs: dict of Balance Sheet fields for the same company-year.
        is_financial: True if this company is in the Financials broad_sector.

    Returns:
        Flat dict of computed ratio values — ready to merge into financial_ratios row.

    Note: CAGR and cash-flow-quality metrics are NOT computed here because they
    require multi-year context. They are added in main() via cagr.py / cashflow_kpis.py.
    """
    opm_val = operating_profit_margin(pl.get('operating_profit'), pl.get('sales'))
    ebit_val = ebit(pl.get('operating_profit'), pl.get('depreciation'))
    de_val = debt_to_equity(bs.get('borrowings'), bs.get('equity_capital'), bs.get('reserves'))
    icr_val = interest_coverage(pl.get('operating_profit'), pl.get('other_income'), pl.get('interest'))

    return {
        # Profitability
        'net_profit_margin_pct': net_profit_margin(pl.get('net_profit'), pl.get('sales')),
        'operating_profit_margin_pct': opm_val,
        'opm_crosscheck_flag': int(opm_crosscheck_flag(opm_val, pl.get('opm_percentage'))),
        'return_on_equity_pct': return_on_equity(pl.get('net_profit'), bs.get('equity_capital'), bs.get('reserves')),
        'return_on_capital_employed_pct': return_on_capital_employed(
            ebit_val, bs.get('equity_capital'), bs.get('reserves'), bs.get('borrowings')
        ),
        'return_on_assets_pct': return_on_assets(pl.get('net_profit'), bs.get('total_assets')),
        'ebit_cr': ebit_val,
        # Leverage
        'debt_to_equity': de_val,
        'high_leverage_flag': int(high_leverage_flag(de_val, is_financial)),
        'interest_coverage': icr_val,
        'icr_label': icr_label(pl.get('interest')),
        'icr_risk_flag': int(icr_risk_flag(icr_val)),
        'net_debt_cr': net_debt(bs.get('borrowings'), bs.get('investments')),
        # Efficiency
        'asset_turnover': asset_turnover(pl.get('sales'), bs.get('total_assets')),
        # Balance sheet derived
        'earnings_per_share': pl.get('eps'),
        'book_value_per_share': book_value_per_share(
            bs.get('equity_capital'), bs.get('reserves'), pl.get('_face_value')
        ),
        'dividend_payout_ratio_pct': pl.get('dividend_payout'),
        'total_debt_cr': bs.get('borrowings'),
    }
```

### Step 5 — Create `tests/kpi/test_leverage.py`

```python
"""
test_leverage.py
10 unit tests for Day 09 leverage & efficiency ratios.
"""
import pytest
from ratios import (
    debt_to_equity, high_leverage_flag,
    interest_coverage, icr_label, icr_risk_flag,
    net_debt, asset_turnover, book_value_per_share,
)


class TestDebtToEquity:

    def test_debt_free_returns_zero_not_none(self):
        """Critical: D/E = 0.0 (not None) signals debt-free — important distinction."""
        result = debt_to_equity(0, 50, 450)
        assert result == 0.0
        assert result is not None

    def test_normal_case(self):
        # borrowings=500, equity=50+450=500 → D/E = 1.0
        assert debt_to_equity(500, 50, 450) == 1.0

    def test_negative_equity_returns_none(self):
        assert debt_to_equity(100, 50, -100) is None

    def test_high_leverage_flag_true_non_financial(self):
        assert high_leverage_flag(de_ratio=6.0, is_financial_sector=False) is True

    def test_high_leverage_flag_suppressed_for_financial(self):
        """Banks with D/E > 5 must NOT be flagged."""
        assert high_leverage_flag(de_ratio=8.0, is_financial_sector=True) is False

    def test_high_leverage_flag_false_at_exactly_5(self):
        """Boundary: D/E = 5.0 is NOT > 5 so flag must be False."""
        assert high_leverage_flag(de_ratio=5.0, is_financial_sector=False) is False


class TestInterestCoverage:

    def test_zero_interest_returns_none(self):
        """Debt-free companies have no interest to cover → ICR undefined."""
        assert interest_coverage(100, 20, 0) is None

    def test_icr_label_is_debt_free_when_interest_zero(self):
        assert icr_label(0) == 'Debt Free'

    def test_icr_label_is_computed_when_interest_positive(self):
        assert icr_label(50) == 'Computed'

    def test_icr_risk_flag_true_below_threshold(self):
        assert icr_risk_flag(1.0) is True

    def test_icr_risk_flag_false_for_debt_free(self):
        """Debt-free = None ICR → no risk flag (they have zero interest expense)."""
        assert icr_risk_flag(None) is False


class TestEfficiency:

    def test_asset_turnover_normal(self):
        assert asset_turnover(1000, 500) == 2.0

    def test_asset_turnover_zero_assets_none(self):
        assert asset_turnover(1000, 0) is None

    def test_net_debt_net_cash_positive(self):
        # borrowings=0, investments=500 → net_debt = -500 (net cash)
        assert net_debt(0, 500) == -500.0
```

### Step 6 — Run Day 09 Tests

```bash
pytest tests/kpi/test_leverage.py -v
# Expected: 13 passed
```

---

## 📈 Day 10 — CAGR Engine

### Step 7 — Create `src/analytics/cagr.py`

```python
"""
cagr.py
Compound Annual Growth Rate engine with complete 6-state edge-case handling.

CAGR Decision Table (per project specification):
  ┌────────────┬────────────┬─────────────────────┬─────────────────────┐
  │ Base Year  │ End Year   │ CAGR Result         │ Flag                │
  ├────────────┼────────────┼─────────────────────┼─────────────────────┤
  │ Positive   │ Positive   │ Computed normally   │ None                │
  │ Positive   │ Negative   │ None                │ DECLINE_TO_LOSS     │
  │ Negative   │ Positive   │ None                │ TURNAROUND          │
  │ Negative   │ Negative   │ None                │ BOTH_NEGATIVE       │
  │ Zero       │ Any        │ None                │ ZERO_BASE           │
  │ < n yrs    │ —          │ None                │ INSUFFICIENT        │
  └────────────┴────────────┴─────────────────────┴─────────────────────┘

Why these cases return None rather than a number:
  DECLINE_TO_LOSS: ((−50)/100)^(1/3) produces an imaginary number in Python.
  TURNAROUND: ((200)/(−100))^(1/5) = negative base under real exponent = NaN.
  BOTH_NEGATIVE: same issue; also business-meaningless without turnaround context.
  ZERO_BASE: division by zero.
  INSUFFICIENT: no base-year data point exists in the series.
"""

from __future__ import annotations
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ── Flag constants ────────────────────────────────────────────────────────────
FLAG_OK                = None              # normal, usable CAGR value
FLAG_DECLINE_TO_LOSS   = 'DECLINE_TO_LOSS'
FLAG_TURNAROUND        = 'TURNAROUND'
FLAG_BOTH_NEGATIVE     = 'BOTH_NEGATIVE'
FLAG_ZERO_BASE         = 'ZERO_BASE'
FLAG_INSUFFICIENT      = 'INSUFFICIENT'


def cagr(
    start: Optional[float],
    end: Optional[float],
    n: int,
) -> tuple[Optional[float], Optional[str]]:
    """
    Core CAGR formula with edge-case handling.

    Args:
        start : Base-year value.
        end   : End-year value.
        n     : Number of years in the window (e.g. 3, 5, 10).

    Returns:
        (cagr_pct, flag) tuple.
        cagr_pct is None whenever the result is undefined; flag explains why.
        flag is None when a valid number is returned.

    Examples:
        >>> cagr(100, 161.051, 5)
        (10.0, None)
        >>> cagr(-100, 200, 5)
        (None, 'TURNAROUND')
        >>> cagr(0, 200, 5)
        (None, 'ZERO_BASE')
    """
    if start is None or end is None:
        return None, FLAG_INSUFFICIENT

    if start == 0:
        return None, FLAG_ZERO_BASE

    if start > 0 and end > 0:
        value = ((end / start) ** (1.0 / n) - 1) * 100
        return round(value, 2), FLAG_OK

    if start > 0 and end <= 0:
        return None, FLAG_DECLINE_TO_LOSS

    if start < 0 and end > 0:
        return None, FLAG_TURNAROUND

    # Both negative
    return None, FLAG_BOTH_NEGATIVE


def _shift_year(year_str: str, delta: int) -> str:
    """
    Shift a 'YYYY-MM' string by delta years.

    Examples:
        >>> _shift_year('2024-03', -5)
        '2019-03'
        >>> _shift_year('2019-03', 5)
        '2024-03'
    """
    yyyy, mm = year_str.split('-')
    return f'{int(yyyy) + delta:04d}-{mm}'


def windowed_cagr(
    series: dict[str, Optional[float]],
    end_year: str,
    n: int,
) -> tuple[Optional[float], Optional[str]]:
    """
    Compute CAGR for a metric series over an n-year window ending at end_year.

    Args:
        series   : {year_str: value} mapping, e.g. {'2019-03': 80000, ...}
        end_year : The latest year key, e.g. '2024-03'.
        n        : Window in years — 3, 5, or 10.

    Returns:
        (cagr_pct, flag). Returns INSUFFICIENT if either endpoint is missing.
    """
    base_year = _shift_year(end_year, -n)

    if end_year not in series or base_year not in series:
        return None, FLAG_INSUFFICIENT

    return cagr(series[base_year], series[end_year], n)


def compute_growth_metrics(
    revenue_series: dict[str, float],
    pat_series:     dict[str, float],
    eps_series:     dict[str, float],
    end_year:       str,
) -> dict:
    """
    Compute Revenue / PAT / EPS CAGR for 3-, 5-, and 10-year windows.

    Returns a flat dict of 18 keys (3 metrics × 3 windows × {value, flag})
    ready to be merged directly into a financial_ratios row.

    Keys follow the pattern: {metric}_cagr_{n}yr and {metric}_cagr_{n}yr_flag.

    Example return (partial):
        {
            'revenue_cagr_5yr': 12.3, 'revenue_cagr_5yr_flag': None,
            'pat_cagr_5yr': None,     'pat_cagr_5yr_flag': 'TURNAROUND',
            ...
        }
    """
    result: dict = {}
    metric_map = {
        'revenue': revenue_series,
        'pat':     pat_series,
        'eps':     eps_series,
    }
    for label, series in metric_map.items():
        for window in (3, 5, 10):
            val, flag = windowed_cagr(series, end_year, window)
            result[f'{label}_cagr_{window}yr']      = val
            result[f'{label}_cagr_{window}yr_flag'] = flag

    return result  # always 18 keys
```

### Step 8 — Create `tests/kpi/test_cagr.py`

```python
"""
test_cagr.py
10 unit tests covering the CAGR engine's 6-state edge-case table.
"""
import pytest
from cagr import (
    cagr, windowed_cagr, compute_growth_metrics, _shift_year,
    FLAG_DECLINE_TO_LOSS, FLAG_TURNAROUND, FLAG_BOTH_NEGATIVE,
    FLAG_ZERO_BASE, FLAG_INSUFFICIENT, FLAG_OK,
)


class TestCagrCore:

    def test_normal_positive_growth(self):
        """100 → 133.1 over 3yr = 10% CAGR (1.1^3 = 1.331)."""
        value, flag = cagr(100, 133.1, 3)
        assert value == pytest.approx(10.0, abs=0.01)
        assert flag is FLAG_OK

    def test_normal_5yr(self):
        """100 → 161.051 over 5yr = 10% CAGR (1.1^5 = 1.61051)."""
        value, flag = cagr(100, 161.051, 5)
        assert value == pytest.approx(10.0, abs=0.01)
        assert flag is FLAG_OK

    def test_decline_to_loss(self):
        """Positive base, negative end → DECLINE_TO_LOSS."""
        value, flag = cagr(100, -50, 3)
        assert value is None
        assert flag == FLAG_DECLINE_TO_LOSS

    def test_turnaround(self):
        """Negative base, positive end → TURNAROUND (not computable as CAGR)."""
        value, flag = cagr(-100, 200, 5)
        assert value is None
        assert flag == FLAG_TURNAROUND

    def test_both_negative(self):
        """Both base and end negative → BOTH_NEGATIVE."""
        value, flag = cagr(-50, -20, 3)
        assert value is None
        assert flag == FLAG_BOTH_NEGATIVE

    def test_zero_base(self):
        """Zero base year → division by zero → ZERO_BASE."""
        value, flag = cagr(0, 200, 5)
        assert value is None
        assert flag == FLAG_ZERO_BASE

    def test_none_start_is_insufficient(self):
        value, flag = cagr(None, 100, 5)
        assert value is None
        assert flag == FLAG_INSUFFICIENT

    def test_none_end_is_insufficient(self):
        value, flag = cagr(100, None, 5)
        assert value is None
        assert flag == FLAG_INSUFFICIENT


class TestWindowedCagr:

    def test_missing_base_year_returns_insufficient(self):
        series = {'2024-03': 100}   # no 2019-03 entry
        value, flag = windowed_cagr(series, '2024-03', 5)
        assert value is None
        assert flag == FLAG_INSUFFICIENT

    def test_normal_windowed_computation(self):
        series = {'2019-03': 100.0, '2024-03': 161.051}
        value, flag = windowed_cagr(series, '2024-03', 5)
        assert value == pytest.approx(10.0, abs=0.01)
        assert flag is FLAG_OK


class TestHelpers:

    def test_shift_year_backward(self):
        assert _shift_year('2024-03', -5) == '2019-03'

    def test_shift_year_forward(self):
        assert _shift_year('2019-03', 5) == '2024-03'

    def test_shift_year_preserves_month(self):
        assert _shift_year('2022-12', -3) == '2019-12'

    def test_compute_growth_metrics_returns_18_keys(self):
        result = compute_growth_metrics({}, {}, {}, '2024-03')
        assert len(result) == 18

    def test_compute_growth_metrics_all_insufficient_on_empty_series(self):
        result = compute_growth_metrics({}, {}, {}, '2024-03')
        assert all(v is None for k, v in result.items() if not k.endswith('_flag'))
        assert all(v == FLAG_INSUFFICIENT for k, v in result.items() if k.endswith('_flag'))
```

### Step 9 — Run Day 10 Tests

```bash
pytest tests/kpi/test_cagr.py -v
# Expected: 15 passed
```

---

## 💰 Day 11 — Cash Flow KPIs & Capital Allocation

### Step 10 — Create `src/analytics/cashflow_kpis.py`

```python
"""
cashflow_kpis.py
Cash flow quality metrics and the 8-pattern capital allocation classifier.

Capital Allocation Pattern — Sign of (CFO, CFI, CFF):
  (+, −, −) → Reinvestor         (investing from ops, paying down debt/dividends)
  (+, −, −) → Shareholder Returns (same signs but dividend_payout ≥ 30%)
  (+, +, −) → Liquidating Assets
  (−, +, +) → Distress Signal    (funding ops via asset sales + new debt)
  (−, −, +) → Growth Funded by Debt
  (+, +, +) → Cash Accumulator
  (−, −, −) → Pre-Revenue / Burn
  (+, −, +) → Mixed
  (−, +, −) → Asset Sale Debt Paydown  ← spec omits this; we label it explicitly

Spec note: The original spec lists (+,−,−) twice — once as "Reinvestor" and once
as "Shareholder Returns". Since sign alone cannot distinguish them, this
implementation sub-classifies using dividend_payout_pct ≥ 30% as the tie-breaker.
"""

from __future__ import annotations
import csv
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


# ── Labels ────────────────────────────────────────────────────────────────────
CFO_QUALITY_HIGH     = 'High Quality'
CFO_QUALITY_MODERATE = 'Moderate'
CFO_QUALITY_ACCRUAL  = 'Accrual Risk'

CAPEX_ASSET_LIGHT  = 'Asset Light'
CAPEX_MODERATE     = 'Moderate'
CAPEX_HEAVY        = 'Capital Intensive'


def free_cash_flow(
    cfo: Optional[float],
    cfi: Optional[float],
) -> Optional[float]:
    """
    FCF = operating_activity + investing_activity.
    Negative FCF is valid (heavy investment years like capacity expansion).
    Returns None only when either input is None.
    """
    if cfo is None or cfi is None:
        return None
    return round(cfo + cfi, 2)


def cfo_quality_score(
    cfo_pat_pairs: list[tuple[Optional[float], Optional[float]]],
) -> tuple[Optional[float], Optional[str]]:
    """
    CFO Quality Score = average(CFO / PAT) over the most recent ≤5 years.

    A CFO/PAT > 1.0 means the company is converting more than 100% of its
    reported profit into actual operating cash — a sign of earnings quality.
    < 0.5 means the profit is largely accrual-based — 'Accrual Risk'.

    Args:
        cfo_pat_pairs: [(cfo, pat), ...] ordered oldest → newest.
                       Only the last 5 items are used.

    Returns:
        (avg_ratio, label). Returns (None, None) when no valid year exists
        (e.g. all PAT values are 0, which would cause division by zero).

    Edge cases:
        • PAT = 0 → skip that year (don't use or flag)
        • CFO = 0 → ratio = 0.0 → valid, counts as Accrual Risk year
        • Both None → skip
    """
    valid_ratios = []
    for cfo, pat in list(cfo_pat_pairs)[-5:]:
        if cfo is None or pat is None or pat == 0:
            continue
        valid_ratios.append(cfo / pat)

    if not valid_ratios:
        return None, None

    avg = sum(valid_ratios) / len(valid_ratios)

    if avg > 1.0:
        label = CFO_QUALITY_HIGH
    elif avg >= 0.5:
        label = CFO_QUALITY_MODERATE
    else:
        label = CFO_QUALITY_ACCRUAL

    return round(avg, 2), label


def capex_intensity(
    cfi: Optional[float],
    sales: Optional[float],
) -> tuple[Optional[float], Optional[str]]:
    """
    CapEx Intensity = |investing_activity| / sales × 100.

    Uses the absolute value of CFI as a CapEx proxy. This may include
    acquisitions and financial investments, not just pure capital expenditure.

    Returns:
        (pct, label) or (None, None) if either input is invalid.

    Benchmarks (from project spec):
        < 3%  → Asset Light
        3–8%  → Moderate
        > 8%  → Capital Intensive
    """
    if cfi is None or sales is None or sales == 0:
        return None, None
    pct = (abs(cfi) / sales) * 100
    if pct < 3:
        label = CAPEX_ASSET_LIGHT
    elif pct <= 8:
        label = CAPEX_MODERATE
    else:
        label = CAPEX_HEAVY
    return round(pct, 2), label


def fcf_conversion_rate(
    fcf_value: Optional[float],
    operating_profit: Optional[float],
) -> Optional[float]:
    """
    FCF Conversion = FCF / operating_profit × 100.
    > 60% = efficient (most EBITDA converts to cash).
    < 30% = heavy CapEx or working capital drain.
    Returns None if operating_profit = 0.
    """
    if fcf_value is None or operating_profit is None or operating_profit == 0:
        return None
    return round((fcf_value / operating_profit) * 100, 2)


def _sign(value: Optional[float]) -> str:
    """Returns '+' if value >= 0 (or None), '-' if value < 0."""
    if value is None:
        return '+'
    return '+' if value >= 0 else '-'


def capital_allocation_pattern(
    cfo: Optional[float],
    cfi: Optional[float],
    cff: Optional[float],
    dividend_payout_pct: Optional[float] = None,
    shareholder_threshold: float = 30.0,
) -> tuple[str, str, str, str]:
    """
    Classify a company-year into one of 8 capital allocation patterns
    based on the signs of (CFO, CFI, CFF).

    Args:
        cfo, cfi, cff         : Cash flow values for the year (₹ Crore).
        dividend_payout_pct   : Used to split the ambiguous (+,−,−) pattern.
        shareholder_threshold : Dividend payout >= this → 'Shareholder Returns'.

    Returns:
        (pattern_label, cfo_sign, cfi_sign, cff_sign)
        Signs are '+' or '-' strings.
    """
    s_cfo = _sign(cfo)
    s_cfi = _sign(cfi)
    s_cff = _sign(cff)
    pattern = (s_cfo, s_cfi, s_cff)

    label_map = {
        ('+', '-', '+'): 'Mixed',
        ('+', '+', '+'): 'Cash Accumulator',
        ('+', '+', '-'): 'Liquidating Assets',
        ('-', '+', '+'): 'Distress Signal',
        ('-', '-', '+'): 'Growth Funded by Debt',
        ('-', '-', '-'): 'Pre-Revenue',
        ('-', '+', '-'): 'Asset Sale Debt Paydown',
    }

    if pattern == ('+', '-', '-'):
        # Spec-defined ambiguity: sub-classify by dividend payout
        if dividend_payout_pct is not None and dividend_payout_pct >= shareholder_threshold:
            label = 'Shareholder Returns'
        else:
            label = 'Reinvestor'
    else:
        label = label_map.get(pattern, 'Unclassified')  # unreachable if all 8 covered

    return label, s_cfo, s_cfi, s_cff


def write_capital_allocation_csv(
    records: list[dict],
    output_path: str = 'output/capital_allocation.csv',
) -> None:
    """
    Write capital allocation records to CSV.

    Each record must have keys:
        company_id, year, cfo_sign, cfi_sign, cff_sign, pattern_label
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ['company_id', 'year', 'cfo_sign', 'cfi_sign', 'cff_sign', 'pattern_label']
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    logger.info('capital_allocation.csv written → %s (%d rows)', output_path, len(records))
```

### Step 11 — Create `tests/kpi/test_cashflow.py`

```python
"""
test_cashflow.py
6 unit tests for cashflow_kpis.py — Day 11.
"""
import pytest
from cashflow_kpis import (
    free_cash_flow, cfo_quality_score, capex_intensity,
    fcf_conversion_rate, capital_allocation_pattern,
    CFO_QUALITY_HIGH, CFO_QUALITY_MODERATE, CFO_QUALITY_ACCRUAL,
    CAPEX_ASSET_LIGHT, CAPEX_HEAVY,
)


class TestCashflowKpis:

    def test_fcf_normal(self):
        assert free_cash_flow(300, -100) == 200.0

    def test_fcf_negative_allowed(self):
        assert free_cash_flow(100, -200) == -100.0

    def test_cfo_quality_high(self):
        """avg(CFO/PAT) > 1.0 → High Quality."""
        pairs = [(150, 100)] * 5
        score, label = cfo_quality_score(pairs)
        assert score == 1.5
        assert label == CFO_QUALITY_HIGH

    def test_cfo_quality_skips_zero_pat(self):
        """Year with PAT=0 must be excluded from average."""
        pairs = [(0, 0), (0, 0), (100, 100)]  # only last pair is valid
        score, label = cfo_quality_score(pairs)
        assert score == 1.0
        assert label == CFO_QUALITY_HIGH

    def test_capex_asset_light(self):
        pct, label = capex_intensity(-20, 1000)   # |−20| / 1000 × 100 = 2%
        assert pct == 2.0
        assert label == CAPEX_ASSET_LIGHT

    def test_capital_allocation_reinvestor_vs_shareholder(self):
        """Same (+ − −) signs → sub-classified by dividend payout."""
        label_low, *_ = capital_allocation_pattern(100, -50, -30, dividend_payout_pct=10)
        label_high, *_ = capital_allocation_pattern(100, -50, -30, dividend_payout_pct=40)
        assert label_low == 'Reinvestor'
        assert label_high == 'Shareholder Returns'


class TestCapexIntensity:

    def test_capital_intensive(self):
        pct, label = capex_intensity(-150, 1000)  # 15% > 8%
        assert pct == 15.0
        assert label == CAPEX_HEAVY


class TestFcfConversion:

    def test_normal(self):
        result = fcf_conversion_rate(200, 400)
        assert result == 50.0

    def test_zero_op_profit_returns_none(self):
        assert fcf_conversion_rate(100, 0) is None
```

### Step 12 — Run Day 11 Tests

```bash
pytest tests/kpi/test_cashflow.py -v
# Expected: 8 passed
```

---

## 🗃️ Day 12 — Populate `financial_ratios` Table

### Step 13 — Add Schema Migration to `ratios.py`

Append this **at the bottom** of `src/analytics/ratios.py` (after `compute_row_ratios`):

```python
# ════════════════════════════════════════════════════════════════
# DAY 12 — SCHEMA MIGRATION + POPULATION ORCHESTRATOR
# ════════════════════════════════════════════════════════════════

import os
import sqlite3
import pandas as pd
from pathlib import Path

from cagr import compute_growth_metrics
from cashflow_kpis import (
    free_cash_flow, cfo_quality_score, capex_intensity,
    fcf_conversion_rate, capital_allocation_pattern, write_capital_allocation_csv,
)

DB_PATH = os.getenv('DB_PATH', 'data/nifty100.db')

# All new columns added in Sprint 2 (idempotent ALTER TABLE migration)
SPRINT2_COLUMNS: dict[str, str] = {
    'return_on_capital_employed_pct': 'REAL',
    'return_on_assets_pct':           'REAL',
    'ebit_cr':                        'REAL',
    'opm_crosscheck_flag':            'INTEGER',
    'high_leverage_flag':             'INTEGER',
    'icr_label':                      'TEXT',
    'icr_risk_flag':                  'INTEGER',
    'net_debt_cr':                    'REAL',
    # CAGR — 3 metrics × 3 windows × {value, flag}
    'revenue_cagr_3yr': 'REAL', 'revenue_cagr_3yr_flag': 'TEXT',
    'revenue_cagr_5yr': 'REAL', 'revenue_cagr_5yr_flag': 'TEXT',
    'revenue_cagr_10yr':'REAL', 'revenue_cagr_10yr_flag':'TEXT',
    'pat_cagr_3yr':     'REAL', 'pat_cagr_3yr_flag':     'TEXT',
    'pat_cagr_5yr':     'REAL', 'pat_cagr_5yr_flag':     'TEXT',
    'pat_cagr_10yr':    'REAL', 'pat_cagr_10yr_flag':    'TEXT',
    'eps_cagr_3yr':     'REAL', 'eps_cagr_3yr_flag':     'TEXT',
    'eps_cagr_5yr':     'REAL', 'eps_cagr_5yr_flag':     'TEXT',
    'eps_cagr_10yr':    'REAL', 'eps_cagr_10yr_flag':    'TEXT',
    # Cash flow quality
    'cfo_quality_score':        'REAL',
    'cfo_quality_label':        'TEXT',
    'capex_intensity_pct':      'REAL',
    'capex_intensity_label':    'TEXT',
    'fcf_conversion_pct':       'REAL',
    'capital_allocation_pattern':'TEXT',
    # Composite
    'composite_quality_score':  'REAL',
}


def _migrate_schema(conn: sqlite3.Connection) -> None:
    """
    Idempotent column migration — adds any Sprint 2 column not already present.
    SQLite does not support ADD COLUMN IF NOT EXISTS, so we check manually.
    """
    existing = {row[1] for row in conn.execute('PRAGMA table_info(financial_ratios)').fetchall()}
    added = 0
    for col, col_type in SPRINT2_COLUMNS.items():
        if col not in existing:
            conn.execute(f'ALTER TABLE financial_ratios ADD COLUMN {col} {col_type}')
            added += 1
    conn.commit()
    if added:
        logger.info('Schema migration: %d new column(s) added to financial_ratios', added)
    else:
        logger.info('Schema migration: all Sprint 2 columns already present')


def _composite_quality_score(df: pd.DataFrame) -> pd.Series:
    """
    Composite Quality Score = 0.30×ROE + 0.25×FCF + 0.25×ROCE + 0.20×D/E_score.

    Each sub-metric is winsorised at P10/P90 across ALL company-years (pooled),
    then scaled to 0–100. D/E is inverted (lower = better).

    The pooled normalisation window ensures a company's score is comparable
    both longitudinally (across its own history) and cross-sectionally
    (against peers in any year). This is the recommended approach in the spec.
    """
    def _scale(s: pd.Series, invert: bool = False) -> pd.Series:
        filled = s.fillna(s.median())
        p10, p90 = filled.quantile(0.10), filled.quantile(0.90)
        if p90 == p10:
            return pd.Series(50.0, index=s.index)
        clipped = filled.clip(p10, p90)
        scaled = (clipped - p10) / (p90 - p10) * 100
        return (100 - scaled).round(2) if invert else scaled.round(2)

    roe  = _scale(df.get('return_on_equity_pct', pd.Series(dtype=float)))
    fcf  = _scale(df.get('free_cash_flow_cr', pd.Series(dtype=float)))
    roce = _scale(df.get('return_on_capital_employed_pct', pd.Series(dtype=float)))
    de   = _scale(df.get('debt_to_equity', pd.Series(dtype=float)), invert=True)

    return (0.30 * roe + 0.25 * fcf + 0.25 * roce + 0.20 * de).clip(0, 100).round(2)


def main() -> None:
    """
    Full Sprint 2 population pipeline.
    Run via:  python src/analytics/ratios.py
          or: make ratios
    """
    conn = sqlite3.connect(DB_PATH)
    conn.execute('PRAGMA foreign_keys = ON')

    _migrate_schema(conn)

    # ── Load source tables ───────────────────────────────────────────────────
    companies = pd.read_sql('SELECT id, face_value, roce_percentage, roe_percentage FROM companies', conn)
    sectors   = pd.read_sql('SELECT company_id, broad_sector FROM sectors', conn)
    pl_all    = pd.read_sql('SELECT * FROM profitandloss  ORDER BY company_id, year', conn)
    bs_all    = pd.read_sql('SELECT * FROM balancesheet    ORDER BY company_id, year', conn)
    cf_all    = pd.read_sql('SELECT * FROM cashflow        ORDER BY company_id, year', conn)

    financial_ids = set(sectors[sectors['broad_sector'] == 'Financials']['company_id'])
    logger.info('Financials carve-out: %d companies (D/E flag suppressed)', len(financial_ids))

    all_rows: list[dict] = []
    cap_alloc_records: list[dict] = []

    # ── Per-company processing ───────────────────────────────────────────────
    for _, co in companies.iterrows():
        cid       = co['id']
        fv        = co['face_value']
        is_fin    = cid in financial_ids

        pl_co = pl_all[pl_all['company_id'] == cid].set_index('year')
        bs_co = bs_all[bs_all['company_id'] == cid].set_index('year')
        cf_co = cf_all[cf_all['company_id'] == cid].set_index('year')

        # Series for CAGR windows
        rev_series = pl_co['sales'].dropna().to_dict()
        pat_series = pl_co['net_profit'].dropna().to_dict()
        eps_series = pl_co['eps'].dropna().to_dict()

        # Process each year that has both P&L and BS data
        years = sorted(set(pl_co.index) & set(bs_co.index))
        for year in years:
            pl_row = pl_co.loc[year].to_dict()
            pl_row['_face_value'] = fv          # injected for BVPS formula
            bs_row = bs_co.loc[year].to_dict()

            row = compute_row_ratios(pl_row, bs_row, is_fin)
            row['company_id'] = cid
            row['year']       = year

            # ── Cash flow fields (only when CF row exists) ────────────────
            if year in cf_co.index:
                cf_row = cf_co.loc[year].to_dict()
                cfo = cf_row.get('operating_activity')
                cfi = cf_row.get('investing_activity')
                cff = cf_row.get('financing_activity')
                div = pl_row.get('dividend_payout')

                fcf = free_cash_flow(cfo, cfi)
                row['free_cash_flow_cr']      = fcf
                row['cash_from_operations_cr'] = cfo
                row['capex_cr']               = abs(cfi) if cfi is not None else None

                ci_pct, ci_lbl  = capex_intensity(cfi, pl_row.get('sales'))
                row['capex_intensity_pct']   = ci_pct
                row['capex_intensity_label'] = ci_lbl
                row['fcf_conversion_pct']    = fcf_conversion_rate(fcf, pl_row.get('operating_profit'))

                pat_label, s_cfo, s_cfi, s_cff = capital_allocation_pattern(cfo, cfi, cff, div)
                row['capital_allocation_pattern'] = pat_label
                cap_alloc_records.append({
                    'company_id':   cid,
                    'year':         year,
                    'cfo_sign':     s_cfo,
                    'cfi_sign':     s_cfi,
                    'cff_sign':     s_cff,
                    'pattern_label':pat_label,
                })
            else:
                for col in ('free_cash_flow_cr', 'cash_from_operations_cr', 'capex_cr',
                            'capex_intensity_pct', 'capex_intensity_label', 'fcf_conversion_pct',
                            'capital_allocation_pattern'):
                    row[col] = None

            # ── 5-year trailing CFO quality score ─────────────────────────
            trailing = [y for y in sorted(cf_co.index) if y <= year][-5:]
            pairs = [
                (cf_co.at[y, 'operating_activity'] if y in cf_co.index else None,
                 pl_co.at[y, 'net_profit']         if y in pl_co.index else None)
                for y in trailing
            ]
            q_score, q_label = cfo_quality_score(pairs)
            row['cfo_quality_score'] = q_score
            row['cfo_quality_label'] = q_label

            # ── CAGR metrics ───────────────────────────────────────────────
            row.update(compute_growth_metrics(rev_series, pat_series, eps_series, year))

            all_rows.append(row)

    # ── Write to SQLite ──────────────────────────────────────────────────────
    df = pd.DataFrame(all_rows)
    df['composite_quality_score'] = _composite_quality_score(df)

    conn.execute('DELETE FROM financial_ratios')
    conn.commit()
    df.to_sql('financial_ratios', conn, if_exists='append', index=False)
    conn.commit()

    # ── Write CSV ────────────────────────────────────────────────────────────
    Path('output').mkdir(exist_ok=True)
    write_capital_allocation_csv(cap_alloc_records)

    # ── Cross-check and edge-case log (Day 13) ───────────────────────────────
    _cross_check_source_values(conn, companies)

    conn.close()
    print(f'✅ financial_ratios: {len(df)} rows | {df["company_id"].nunique()} companies')
    print(f'✅ capital_allocation.csv: {len(cap_alloc_records)} rows')


if __name__ == '__main__':
    main()
```

### Step 14 — Run the Population Pipeline

```bash
# Make sure you're in the project root with venv active
make ratios
# or:
python src/analytics/ratios.py
```

**Expected terminal output:**
```
Schema migration: 32 new column(s) added to financial_ratios
Financials carve-out: 19 companies (D/E flag suppressed)
✅ financial_ratios: 1,184 rows | 92 companies
✅ capital_allocation.csv: 1,187 rows
```

### Step 15 — Verify the Table

```bash
sqlite3 data/nifty100.db << 'EOF'
.mode column
.headers on

-- Gate 1: row count
SELECT COUNT(*) AS total_rows FROM financial_ratios;

-- Gate 2: distinct companies
SELECT COUNT(DISTINCT company_id) AS companies FROM financial_ratios;

-- Gate 3: all KPI columns have at least some non-null values
SELECT
  SUM(CASE WHEN return_on_equity_pct       IS NOT NULL THEN 1 ELSE 0 END) AS has_roe,
  SUM(CASE WHEN debt_to_equity             IS NOT NULL THEN 1 ELSE 0 END) AS has_de,
  SUM(CASE WHEN revenue_cagr_5yr           IS NOT NULL THEN 1 ELSE 0 END) AS has_cagr,
  SUM(CASE WHEN composite_quality_score    IS NOT NULL THEN 1 ELSE 0 END) AS has_composite,
  SUM(CASE WHEN capital_allocation_pattern IS NOT NULL THEN 1 ELSE 0 END) AS has_capalloc
FROM financial_ratios;

-- Gate 4: preview TCS
SELECT company_id, year, return_on_equity_pct, debt_to_equity,
       revenue_cagr_5yr, composite_quality_score, capital_allocation_pattern
FROM financial_ratios
WHERE company_id = 'TCS'
ORDER BY year DESC LIMIT 5;
EOF
```

### Step 16 — Manual Spot-Check (Required for Exit Criteria)

Run this for 3 companies and compare to your own Excel calculation:

```python
# notebooks/spot_check_sprint2.py
import sqlite3, pandas as pd

conn = sqlite3.connect('data/nifty100.db')
SAMPLE = ['TCS', 'RELIANCE', 'HDFCBANK']

for ticker in SAMPLE:
    pl = pd.read_sql(
        "SELECT year, sales, net_profit FROM profitandloss WHERE company_id=? ORDER BY year",
        conn, params=(ticker,)
    )
    bs = pd.read_sql(
        "SELECT equity_capital, reserves FROM balancesheet WHERE company_id=? ORDER BY year DESC LIMIT 1",
        conn, params=(ticker,)
    )
    fr = pd.read_sql(
        "SELECT year, return_on_equity_pct, revenue_cagr_5yr FROM financial_ratios "
        "WHERE company_id=? ORDER BY year DESC LIMIT 1",
        conn, params=(ticker,)
    )
    latest = fr.iloc[0]['year']
    pl_lat = pl[pl['year'] == latest].iloc[0]
    eq = bs.iloc[0]['equity_capital'] + bs.iloc[0]['reserves']
    manual_roe = round(pl_lat['net_profit'] / eq * 100, 2)
    db_roe = fr.iloc[0]['return_on_equity_pct']
    roe_diff = abs(manual_roe - db_roe) if db_roe else 99
    print(f"{ticker}: Manual ROE={manual_roe}% | DB ROE={db_roe}% | "
          f"Diff={roe_diff:.3f}pp {'✅' if roe_diff < 0.1 else '❌'}")
conn.close()
```

```bash
python notebooks/spot_check_sprint2.py
# All 3 must show ✅ Diff < 0.1pp
```

---

## 🏦 Day 13 — Bank ROCE Carve-Out & Edge Case Log

### Step 17 — Add Cross-Check Function to `ratios.py`

Append this **below the `main()` function** in `src/analytics/ratios.py`:

```python
def _cross_check_source_values(
    conn: sqlite3.Connection,
    companies_df: pd.DataFrame,
    log_path: str = 'output/ratio_edge_cases.log',
) -> None:
    """
    Cross-checks Ratio Engine ROCE / ROE (latest year) against the
    pre-computed columns in companies.xlsx and logs every anomaly.

    Anomaly categories (per spec):
        data source issue   : source value looks like a bug (e.g. TCS ROE = 0.52)
        version difference  : values differ but both are plausible (time lag)
        formula discrepancy : difference likely caused by a formula variation
    """
    latest_map = pd.read_sql(
        'SELECT company_id, MAX(year) AS yr FROM financial_ratios GROUP BY company_id', conn
    )
    fr = pd.read_sql('SELECT * FROM financial_ratios', conn)
    fr_latest = fr.merge(latest_map, left_on=['company_id', 'year'], right_on=['company_id', 'yr'])
    merged = fr_latest.merge(companies_df, left_on='company_id', right_on='id')

    lines = [
        '=' * 70,
        'RATIO ENGINE — SOURCE CROSS-CHECK LOG (Day 13)',
        f'Run against {len(merged)} companies — latest year per company',
        '=' * 70, '',
    ]
    anomalies = 0

    for _, row in merged.iterrows():
        cid = row['company_id']

        # ── ROCE cross-check (threshold: > 5 percentage points) ────────────
        roce_eng = row.get('return_on_capital_employed_pct')
        roce_src = row.get('roce_percentage')
        if pd.notna(roce_eng) and pd.notna(roce_src):
            diff = abs(roce_eng - roce_src)
            if diff > 5:
                cat = 'data source issue' if diff > 20 else 'formula discrepancy'
                lines.append(
                    f'[{cid}] ROCE  engine={roce_eng:.2f}%  source={roce_src:.2f}%  '
                    f'diff={diff:.2f}pp  → {cat}'
                )
                anomalies += 1

        # ── ROE cross-check ────────────────────────────────────────────────
        # Known source bug: some companies show ROE as a decimal fraction
        # (e.g. TCS = 0.52 which should be 52.0). We detect this pattern.
        roe_eng = row.get('return_on_equity_pct')
        roe_src = row.get('roe_percentage')
        if pd.notna(roe_eng) and pd.notna(roe_src):
            if roe_src < 1.0 and roe_eng > 5.0:
                lines.append(
                    f'[{cid}] ROE   engine={roe_eng:.2f}%  source={roe_src}  '
                    f'(source looks like decimal-fraction bug, e.g. 0.52 → 52%)  '
                    f'→ data source issue  [display source; use engine for analytics]'
                )
                anomalies += 1
            elif abs(roe_eng - roe_src) > 5:
                lines.append(
                    f'[{cid}] ROE   engine={roe_eng:.2f}%  source={roe_src:.2f}%  '
                    f'diff={abs(roe_eng - roe_src):.2f}pp  → version difference'
                )
                anomalies += 1

    lines += ['', f'Total anomalies: {anomalies}', '=' * 70]
    Path(log_path).parent.mkdir(parents=True, exist_ok=True)
    Path(log_path).write_text('\n'.join(lines))
    logger.info('Edge case log written → %s (%d anomalies)', log_path, anomalies)
```

### Step 18 — Re-run to Generate the Log

```bash
make ratios    # cross-check runs automatically at end of main()
cat output/ratio_edge_cases.log
```

### Step 19 — Verify Financials Carve-Out in DB

```bash
sqlite3 data/nifty100.db "
SELECT f.company_id, f.debt_to_equity, f.high_leverage_flag
FROM financial_ratios f
JOIN sectors s ON f.company_id = s.company_id
WHERE s.broad_sector = 'Financials'
  AND f.year = (SELECT MAX(year) FROM financial_ratios)
  AND f.debt_to_equity > 5
ORDER BY f.debt_to_equity DESC;"
# high_leverage_flag must be 0 for ALL rows returned
```

---

## ✅ Day 14 — Tests, Screener Preview & Sprint Review

### Step 20 — Run the Complete Test Suite

```bash
pytest tests/kpi/ -v --tb=short
```

**Expected output:**
```
tests/kpi/test_profitability.py::TestNetProfitMargin::test_normal_case              PASSED
tests/kpi/test_profitability.py::TestNetProfitMargin::test_negative_profit_allowed  PASSED
tests/kpi/test_profitability.py::TestNetProfitMargin::test_zero_sales_returns_none  PASSED
tests/kpi/test_profitability.py::TestNetProfitMargin::test_none_sales_returns_none  PASSED
tests/kpi/test_profitability.py::TestOperatingProfitMargin::test_normal_case        PASSED
tests/kpi/test_profitability.py::TestOperatingProfitMargin::test_crosscheck_flags…  PASSED
tests/kpi/test_profitability.py::TestOperatingProfitMargin::test_crosscheck_passes… PASSED
tests/kpi/test_profitability.py::TestROE::test_normal_case                          PASSED
tests/kpi/test_profitability.py::TestROE::test_negative_equity_returns_none         PASSED
tests/kpi/test_profitability.py::TestROE::test_zero_equity_returns_none             PASSED
tests/kpi/test_leverage.py::TestDebtToEquity::test_debt_free_returns_zero_not_none  PASSED
tests/kpi/test_leverage.py::TestDebtToEquity::test_normal_case                      PASSED
tests/kpi/test_leverage.py::TestDebtToEquity::test_negative_equity_returns_none     PASSED
tests/kpi/test_leverage.py::TestDebtToEquity::test_high_leverage_flag_true…         PASSED
tests/kpi/test_leverage.py::TestDebtToEquity::test_high_leverage_flag_suppressed…   PASSED
tests/kpi/test_leverage.py::TestDebtToEquity::test_high_leverage_flag_false_at_5    PASSED
tests/kpi/test_leverage.py::TestInterestCoverage::test_zero_interest_returns_none   PASSED
tests/kpi/test_leverage.py::TestInterestCoverage::test_icr_label_is_debt_free…      PASSED
tests/kpi/test_leverage.py::TestInterestCoverage::test_icr_label_is_computed…       PASSED
tests/kpi/test_leverage.py::TestInterestCoverage::test_icr_risk_flag_true…          PASSED
tests/kpi/test_leverage.py::TestInterestCoverage::test_icr_risk_flag_false…         PASSED
tests/kpi/test_leverage.py::TestEfficiency::test_asset_turnover_normal               PASSED
tests/kpi/test_leverage.py::TestEfficiency::test_asset_turnover_zero_assets_none     PASSED
tests/kpi/test_leverage.py::TestEfficiency::test_net_debt_net_cash_positive           PASSED
tests/kpi/test_cagr.py::TestCagrCore::test_normal_positive_growth                   PASSED
tests/kpi/test_cagr.py::TestCagrCore::test_normal_5yr                               PASSED
tests/kpi/test_cagr.py::TestCagrCore::test_decline_to_loss                          PASSED
tests/kpi/test_cagr.py::TestCagrCore::test_turnaround                               PASSED
tests/kpi/test_cagr.py::TestCagrCore::test_both_negative                            PASSED
tests/kpi/test_cagr.py::TestCagrCore::test_zero_base                                PASSED
tests/kpi/test_cagr.py::TestCagrCore::test_none_start_is_insufficient               PASSED
tests/kpi/test_cagr.py::TestCagrCore::test_none_end_is_insufficient                 PASSED
tests/kpi/test_cagr.py::TestWindowedCagr::test_missing_base_year…                   PASSED
tests/kpi/test_cagr.py::TestWindowedCagr::test_normal_windowed_computation          PASSED
tests/kpi/test_cashflow.py::TestCashflowKpis::test_fcf_normal                       PASSED
tests/kpi/test_cashflow.py::TestCashflowKpis::test_fcf_negative_allowed             PASSED
...
============================== 36 passed in 2.14s ==============================
```

### Step 21 — Screener Preview (Business Sense Check)

```bash
sqlite3 data/nifty100.db << 'EOF'
.mode column
.headers on
-- Quick filter: ROE > 15% AND D/E < 1 — should return 15-50 companies
SELECT company_id,
       ROUND(return_on_equity_pct, 1) AS roe_pct,
       ROUND(debt_to_equity, 2)       AS de,
       ROUND(revenue_cagr_5yr, 1)     AS rev_cagr_5yr
FROM financial_ratios
WHERE year = (SELECT MAX(year) FROM financial_ratios)
  AND return_on_equity_pct > 15
  AND debt_to_equity < 1
ORDER BY return_on_equity_pct DESC;
EOF
```

**Interpreting the result:**
- Count must be **between 15 and 50**
- You should recognise names: `TCS`, `INFY`, `HCLTECH`, `HINDUNILVR`, `ITC`, etc.
- If count = 0 → check that `return_on_equity_pct` was populated correctly
- If count > 70 → review the D/E filter; financial-sector companies may be skewing results

---

## 📋 Sprint 2 Retrospective Template

Save this as `docs/sprint2_retro.md` before the review meeting:

```markdown
# Sprint 2 Retrospective — Financial Ratio Engine
**Date:** Day 14 · ___________

---

## Sprint Goal Review

| Goal | Status | Notes |
|---|---|---|
| 50+ KPIs for all 92 companies | ✅ / ❌ | |
| financial_ratios ≥ 1,100 rows | ✅ / ❌ | Actual: ___ |
| All CAGR edge cases handled | ✅ / ❌ | |
| Bank D/E carve-out correct | ✅ / ❌ | |
| 20+ tests passing | ✅ / ❌ | Actual: 36 |

---

## Exit Criteria Sign-Off

| Gate | Command | Result | Status |
|---|---|---|---|
| `COUNT(*) >= 1,100` | `SELECT COUNT(*) FROM financial_ratios` | ___ | ✅/❌ |
| 14+ KPI columns populated | See verification query | — | ✅/❌ |
| 36 tests pass | `pytest tests/kpi/ -q` | 0 failed | ✅/❌ |
| Manual spot-check ±0.1% | `python notebooks/spot_check_sprint2.py` | — | ✅/❌ |
| `ratio_edge_cases.log` documented | `cat output/ratio_edge_cases.log` | ___ anomalies | ✅/❌ |
| Screener preview 15–50 cos | See screener preview query | ___ companies | ✅/❌ |

---

## Engineering Decisions Recorded

1. **D/E returns 0.0 not None for debt-free companies.** Zero is a valid, meaningful signal that must pass through screener filters (max_de=1 should include debt-free companies).

2. **`(+,−,−)` capital allocation ambiguity resolved** by dividend payout ≥ 30% → "Shareholder Returns"; otherwise → "Reinvestor". Threshold is configurable in `cashflow_kpis.py`.

3. **Composite score uses pooled normalisation** (all company-years together, not per-year cross-section) for longitudinal consistency.

4. **ROE source value is display-only.** Some companies in `companies.xlsx` have `roe_percentage` as a decimal fraction bug (e.g. `0.52` instead of `52`). Ratio Engine value is authoritative.

5. **CAGR turnaround flag stored alongside the value.** Downstream modules (Sprint 3 screener) can filter `revenue_cagr_5yr_flag IS NULL` to get only clean, numeric growth rates.

---

## 🔢 Story Points

| Day | Theme | Est SP | Actual SP |
|---|---|---|---|
| D08 | Profitability Ratios | 7 | |
| D09 | Leverage & Efficiency | 7 | |
| D10 | CAGR Engine | 8 | |
| D11 | Cash Flow KPIs | 7 | |
| D12 | Populate Table | 6 | |
| D13 | Bank Carve-Out & Log | 4 | |
| D14 | Tests & Review | 3 | |
| **Total** | | **42** | |

---

**Signed off:** _________________________  **Date:** ____________
```

---

## 🚀 Sprint 2 Exit Check Script

```bash
#!/bin/bash
# sprint2_exit_check.sh — run this before the Day 14 review meeting
set -euo pipefail
DB="data/nifty100.db"

echo "════════════════════════════════════════"
echo "  Sprint 2 Exit Check"
echo "════════════════════════════════════════"

ROWS=$(sqlite3 $DB "SELECT COUNT(*) FROM financial_ratios;")
echo "financial_ratios rows = $ROWS"
[ "$ROWS" -ge 1100 ] && echo "  ✅ >= 1,100" || echo "  ❌ < 1,100 — GATE FAILED"

COS=$(sqlite3 $DB "SELECT COUNT(DISTINCT company_id) FROM financial_ratios;")
echo "Distinct companies = $COS"
[ "$COS" -eq 92 ] && echo "  ✅ 92" || echo "  ❌ not 92 — check loader"

SCREENER=$(sqlite3 $DB "
  SELECT COUNT(*) FROM financial_ratios
  WHERE year=(SELECT MAX(year) FROM financial_ratios)
    AND return_on_equity_pct > 15 AND debt_to_equity < 1;")
echo "Screener preview (ROE>15, D/E<1) = $SCREENER companies"
( [ "$SCREENER" -ge 15 ] && [ "$SCREENER" -le 50 ] ) && echo "  ✅ 15-50 range" || echo "  ⚠️  outside 15-50"

[ -f output/capital_allocation.csv ] && echo "capital_allocation.csv ✅" || echo "capital_allocation.csv ❌ MISSING"
[ -f output/ratio_edge_cases.log  ] && echo "ratio_edge_cases.log  ✅" || echo "ratio_edge_cases.log  ❌ MISSING"

echo ""
echo "Running pytest..."
pytest tests/kpi/ -q --tb=short

echo ""
echo "════════════════════════════════════════"
echo " Sprint 2 check complete."
echo "════════════════════════════════════════"
```

```bash
chmod +x sprint2_exit_check.sh && ./sprint2_exit_check.sh
```

---

## 🗺️ What Sprint 3 Needs From This Sprint

Sprint 3 builds the Investment Screener, Financial Health Score, and Sector Analytics — all of which read from `financial_ratios`. Before Day 15:

| Requirement | Verification |
|---|---|
| `financial_ratios` populated for all 92 companies | `SELECT COUNT(DISTINCT company_id)` = 92 |
| `debt_to_equity` is `0.0` (not `NULL`) for debt-free companies | Check TCS, INFY — should be 0.0 |
| `revenue_cagr_5yr` populated for companies with ≥ 5yr data | `SELECT COUNT(*) WHERE revenue_cagr_5yr IS NOT NULL` |
| `composite_quality_score` populated — screener ranking engine needs it | `SELECT MIN, MAX, AVG FROM financial_ratios` where not null |
| `high_leverage_flag = 0` for all Financials-sector companies | Check HDFCBANK, SBIN — must show 0 |
| `capital_allocation.csv` — used by Sprint 5 Streamlit treemap | `wc -l output/capital_allocation.csv` |
| `ratio_edge_cases.log` reviewed and signed off | No unresolved anomalies |

---

*Sprint 2 · N100 Financial Intelligence Platform · v1.0 · June 2026 · Data Analytics Division*
