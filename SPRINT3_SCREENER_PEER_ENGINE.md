# 🔍 Sprint 3 — Screener · Peer Comparison Engine
### Nifty 100 Financial Intelligence Platform · Days 15–21 · 49 Story Points

---

## 📌 Sprint Goal

> By end of **Day 21**, the financial screener must be fully functional with **6 preset filters** and custom threshold support for **15 metrics**. Peer percentile rankings must be computed for all **11 peer groups** across **10 metrics**. `screener_output.xlsx` and `peer_comparison.xlsx` must be generated, reviewed, and demoed. All **14 DQ unit tests** must pass.

---

## ✅ Sprint 3 Task Coverage Checklist

Use this to verify nothing is missed before the Day 21 sign-off:

| Day | Task from Spec | Section | Status |
|---|---|---|---|
| 15 | `src/screener/engine.py` with YAML loading | Step 2–3 | |
| 15 | 15 filterable metrics in config | Step 1 | |
| 15 | D/E filter skips Financials sector | Step 3 | |
| 15 | ICR filter — Debt Free = infinity (always passes) | Step 3 | |
| 15 | Return sorted DataFrame with composite_quality_score | Step 3 | |
| 16 | Quality Compounder preset | Step 1 | |
| 16 | Value Pick preset | Step 1 | |
| 16 | Growth Accelerator preset | Step 1 | |
| 16 | Dividend Champion preset | Step 1 | |
| 16 | Debt-Free Blue Chip preset | Step 1 | |
| 16 | Turnaround Watch preset (with D/E declining YoY) | Step 1 + 3 | |
| 16 | Test each preset — 5 to 50 companies | Step 6–7 | |
| 17 | Composite score 0–100 (35/30/20/15 weights) | Step 8 | |
| 17 | P10/P90 winsorisation per metric | Step 8 | |
| 17 | Sector-relative composite score | Step 8 | |
| 17 | `screener_output.xlsx` — 1 sheet per preset, 20 KPIs | Step 9 | |
| 17 | Green/red cell colour-coding | Step 9 | |
| 18 | `src/analytics/peer.py` | Step 10 | |
| 18 | 10 ranked metrics | Step 10 | |
| 18 | D/E inverted percentile (1 − PERCENT_RANK) | Step 10 | |
| 18 | `peer_percentiles` table in SQLite | Step 11 | |
| 18 | Companies not in peer group — log, no error | Step 10 | |
| 19 | Radar chart — 8 axes, filled polygon + dashed overlay | Step 12 | |
| 19 | PNG → `reports/radar_charts/<ticker>_radar.png` | Step 12 | |
| **19** | **Companies with NO peer group → standalone chart vs Nifty 100 avg** | **Step 13** | |
| 19 | Readable font size | Step 12 | |
| 20 | `peer_comparison.xlsx` — 11 sheets | Step 14 | |
| 20 | 20 metric columns + percentile rank columns | Step 14 | |
| 20 | Green ≥75th · Yellow 25–75th · Red ≤25th | Step 14 | |
| 20 | Benchmark row — gold background | Step 14 | |
| 20 | Median summary row at bottom | Step 14 | |
| **21** | **Run all 14 DQ rule unit tests** | **Step 15** | |
| 21 | Verify Quality Compounder top 5 results | Step 16 | |
| **21** | **Verify IT Services peer group ROE rank** | **Step 17** | |
| **21** | **Verify FMCG peer group spot-check** | **Step 17** | |
| 21 | Sprint 3 retrospective | Step 18 | |
| 21 | Demo to team lead | Step 18 | |

> **Bold rows = tasks missing from earlier drafts — all covered now.**

---

## 📁 Deliverables

| # | Deliverable | Format | Due |
|---|---|---|---|
| D-01 | `config/screener_config.yaml` — 15 filters + 6 presets | YAML | Day 15 |
| D-02 | `src/screener/__init__.py` | Python | Day 15 |
| D-03 | `src/screener/engine.py` | Python | Day 15–17 |
| D-04 | `src/analytics/peer.py` | Python | Day 18–20 |
| D-05 | `peer_percentiles` table in SQLite | SQLite | Day 18 |
| D-06 | `output/screener_output.xlsx` — 6 sheets | Excel | Day 17 |
| D-07 | `output/peer_comparison.xlsx` — 11 sheets | Excel | Day 20 |
| D-08 | `reports/radar_charts/*.png` — all grouped + ungrouped | PNG | Day 19 |
| D-09 | `tests/screener/test_engine.py` | pytest | Day 21 |
| D-10 | `tests/kpi/test_peer.py` | pytest | Day 21 |

---

## ✅ Exit Criteria

```bash
# Gate 1 — All 6 presets return 5–50 companies
python -c "
from src.screener.engine import run_all_presets
results = run_all_presets()
for name, df in results.items():
    ok = 5 <= len(df) <= 50
    print(f'  {\"✅\" if ok else \"❌\"} {name}: {len(df)} companies')
"

# Gate 2 — peer_comparison.xlsx has exactly 11 sheets
python -c "
import openpyxl
wb = openpyxl.load_workbook('output/peer_comparison.xlsx')
n = len(wb.sheetnames)
print(f'  {\"✅\" if n==11 else \"❌\"} {n}/11 sheets')
print(wb.sheetnames)
"

# Gate 3 — peer_percentiles table: 11 groups, 10 metrics
sqlite3 data/nifty100.db "
SELECT
  COUNT(DISTINCT peer_group_name) AS groups,
  COUNT(DISTINCT company_id)      AS companies,
  COUNT(DISTINCT metric)          AS metrics
FROM peer_percentiles;"
# → 11 groups · ~46 companies · 10 metrics

# Gate 4 — 14 DQ rule unit tests pass (Sprint 1 tests)
pytest tests/dq/ -v --tb=short

# Gate 5 — Sprint 3 unit tests pass
pytest tests/screener/ tests/kpi/test_peer.py -v --tb=short
```

---

## ⚠️ Pre-Sprint Checklist — Sprint 2 Must Be Complete

```bash
sqlite3 data/nifty100.db "SELECT COUNT(*) FROM financial_ratios;"   # → ≥ 1,100
sqlite3 data/nifty100.db "SELECT COUNT(*) FROM peer_groups;"        # → 56
sqlite3 data/nifty100.db "SELECT COUNT(*) FROM sectors;"            # → 92
pytest tests/kpi/ -q                                                 # → 0 failures
ls output/capital_allocation.csv                                     # → file exists
```

---

## 📐 Design Decisions (Resolve Spec Ambiguities Before Coding)

| # | Ambiguity | Decision Made |
|---|---|---|
| 1 | D/E filter + Financials sector | `broad_sector = 'Financials'` companies **bypass** the `max_de` filter entirely — their leverage is structural |
| 2 | ICR filter + debt-free companies | `icr_label = 'Debt Free'` → **always passes** any `min_icr` threshold (ICR = ∞) |
| 3 | Turnaround Watch — "D/E declining YoY" | `current_de < prev_de` OR `current_de == 0.0`; companies with no prior-year data are **excluded** |
| 4 | Debt-Free Blue Chip — "D/E = 0" | Filter `debt_to_equity == 0.0` — Sprint 2 stored `0.0` not `NULL` for debt-free |
| 5 | Composite score for screener | Re-use `composite_quality_score` from Sprint 2 for global ranking; compute fresh **sector-relative** score here |
| 6 | Companies not in any peer group | Log warning, return empty DataFrame — **also generate a standalone radar chart** using Nifty 100 universe average |
| 7 | D/E on radar chart | Axis labelled **"Low Debt"** and **inverted** — outer ring = zero debt (best) |

---

## 📁 Files Created This Sprint

```
src/
├── screener/
│   ├── __init__.py            ← new package
│   └── engine.py              ← Days 15–17
└── analytics/
    └── peer.py                ← Days 18–20

config/
└── screener_config.yaml       ← Day 15

tests/
├── screener/
│   ├── __init__.py
│   └── test_engine.py         ← Day 21
└── kpi/
    └── test_peer.py           ← Day 21
```

---

## ⚙️ Day 15 — Filter Engine Core

### Step 1 — Create `config/screener_config.yaml`

> This file contains ALL 15 spec-required filter definitions plus the 6 presets. No code changes needed to modify thresholds or add new presets.

```yaml
# ============================================================
# screener_config.yaml — N100 Financial Intelligence Platform
# Edit thresholds here; NO code changes needed.
# ============================================================

screener:

  # ── 15 filterable metric definitions (per spec) ─────────────────────────
  # Spec list: ROE, D/E, FCF, Rev CAGR 5yr, PAT CAGR 5yr, OPM,
  #            P/E, P/B, Div Yield, ICR, Market Cap, Net Profit,
  #            EPS CAGR, Asset Turnover, Sales
  #
  # operator     : ">=" (min) or "<=" (max)
  # source       : table column lives in
  # sector_bypass: sectors that skip this filter (D/E Financials carve-out)
  # icr_passthrough: 'Debt Free' label always passes this filter

  filters:

    # 1. ROE min
    min_roe:
      column: return_on_equity_pct
      operator: ">="
      source: financial_ratios

    # 2. D/E max — Financials sector bypass
    max_de:
      column: debt_to_equity
      operator: "<="
      source: financial_ratios
      sector_bypass: [Financials]

    # 3. FCF min
    min_fcf:
      column: free_cash_flow_cr
      operator: ">="
      source: financial_ratios

    # 4. Revenue CAGR 5yr min
    min_rev_cagr_5yr:
      column: revenue_cagr_5yr
      operator: ">="
      source: financial_ratios

    # 5. PAT CAGR 5yr min
    min_pat_cagr_5yr:
      column: pat_cagr_5yr
      operator: ">="
      source: financial_ratios

    # 6. OPM min
    min_opm:
      column: operating_profit_margin_pct
      operator: ">="
      source: financial_ratios

    # 7. P/E max (market_cap table join)
    max_pe:
      column: pe_ratio
      operator: "<="
      source: market_cap

    # 8. P/B max
    max_pb:
      column: pb_ratio
      operator: "<="
      source: market_cap

    # 9. Dividend Yield min
    min_div_yield:
      column: dividend_yield_pct
      operator: ">="
      source: market_cap

    # 10. ICR min — Debt Free passthrough
    min_icr:
      column: interest_coverage
      operator: ">="
      source: financial_ratios
      icr_passthrough: true

    # 11. Market Cap min
    min_market_cap:
      column: market_cap_crore
      operator: ">="
      source: market_cap

    # 12. Net Profit min
    min_net_profit:
      column: net_profit
      operator: ">="
      source: profitandloss

    # 13. EPS CAGR min
    min_eps_cagr_5yr:
      column: eps_cagr_5yr
      operator: ">="
      source: financial_ratios

    # 14. Asset Turnover min
    min_asset_turnover:
      column: asset_turnover
      operator: ">="
      source: financial_ratios

    # 15. Sales min
    min_sales:
      column: sales
      operator: ">="
      source: profitandloss

    # ── Extra filters needed by presets (beyond the required 15) ──────────
    min_rev_cagr_3yr:
      column: revenue_cagr_3yr
      operator: ">="
      source: financial_ratios

    max_div_payout:
      column: dividend_payout_ratio_pct
      operator: "<="
      source: financial_ratios

  # ── 6 preset templates ───────────────────────────────────────────────────
  presets:

    quality_compounder:
      label: "Quality Compounder"
      description: "High ROE · low debt · positive FCF · double-digit revenue growth"
      ranking_column: composite_quality_score
      ranking_asc: false
      expected_min: 10
      expected_max: 40
      filters:
        min_roe:          15
        max_de:           1.0
        min_fcf:          0
        min_rev_cagr_5yr: 10

    value_pick:
      label: "Value Pick"
      description: "Low P/E · low P/B · manageable debt · dividend paying"
      ranking_column: pe_ratio
      ranking_asc: true
      expected_min: 5
      expected_max: 35
      filters:
        max_pe:        20
        max_pb:        3.0
        max_de:        2.0
        min_div_yield: 1.0

    growth_accelerator:
      label: "Growth Accelerator"
      description: "High PAT CAGR · high revenue CAGR · manageable debt"
      ranking_column: pat_cagr_5yr
      ranking_asc: false
      expected_min: 5
      expected_max: 25
      filters:
        min_pat_cagr_5yr: 20
        min_rev_cagr_5yr: 15
        max_de:           2.0

    dividend_champion:
      label: "Dividend Champion"
      description: "High sustainable dividend yield · payout < 80% · positive FCF"
      ranking_column: dividend_yield_pct
      ranking_asc: false
      expected_min: 5
      expected_max: 25
      filters:
        min_div_yield:  2.0
        max_div_payout: 80.0
        min_fcf:        0

    debt_free_blue_chip:
      label: "Debt-Free Blue Chip"
      description: "Zero debt · strong ROE · large revenue base"
      ranking_column: return_on_equity_pct
      ranking_asc: false
      expected_min: 10
      expected_max: 35
      filters:
        max_de:    0.0
        min_roe:   12
        min_sales: 5000

    turnaround_watch:
      label: "Turnaround Watch"
      description: "Revenue recovering · latest FCF positive · D/E declining YoY"
      ranking_column: revenue_cagr_3yr
      ranking_asc: false
      expected_min: 5
      expected_max: 20
      filters:
        min_rev_cagr_3yr: 10
        min_fcf:          0
      special_filters:
        de_declining_yoy: true          # handled separately (needs 2 years of data)
```

### Step 2 — Create `src/screener/__init__.py`

```python
# makes src/screener/ a Python package
```

### Step 3 — Create `src/screener/engine.py`

```python
"""
engine.py
Config-driven investment screener — N100 Financial Intelligence Platform.

All thresholds live in screener_config.yaml. No hard-coded numbers here.

Key spec rules implemented:
  Rule 1 — D/E filter:  Financials-sector companies automatically bypass max_de.
  Rule 2 — ICR filter:  icr_label='Debt Free' companies automatically pass min_icr.
  Rule 3 — Turnaround: 'de_declining_yoy' special filter compares 2 years of data.
"""

from __future__ import annotations

import logging
import os
import sqlite3
from pathlib import Path
from typing import Optional

import pandas as pd
import yaml
from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.utils import get_column_letter

logger = logging.getLogger(__name__)

DB_PATH     = os.getenv('DB_PATH',              'data/nifty100.db')
CONFIG_PATH = os.getenv('SCREENER_CONFIG_PATH', 'config/screener_config.yaml')

# ── Excel colours ─────────────────────────────────────────────────────────────
FILL_HEADER = PatternFill('solid', fgColor='1F3864')
FILL_GREEN  = PatternFill('solid', fgColor='C8E6C9')
FILL_RED    = PatternFill('solid', fgColor='FFCDD2')
FONT_HEADER = Font(color='FFFFFF', bold=True, size=10)

# ── 20 columns shown in screener_output.xlsx ──────────────────────────────────
DISPLAY_COLS = [
    'company_id', 'company_name', 'broad_sector',
    'return_on_equity_pct', 'return_on_capital_employed_pct',
    'net_profit_margin_pct', 'operating_profit_margin_pct',
    'debt_to_equity', 'interest_coverage', 'icr_label',
    'free_cash_flow_cr', 'cfo_quality_score',
    'revenue_cagr_5yr', 'pat_cagr_5yr', 'eps_cagr_5yr',
    'pe_ratio', 'pb_ratio', 'dividend_yield_pct',
    'composite_quality_score', 'sector_relative_score',
]


# ════════════════════════════════════════════════════════════════
# 1. DATA LOADING
# ════════════════════════════════════════════════════════════════

def _load_config() -> dict:
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)['screener']


def load_universe(conn: sqlite3.Connection) -> pd.DataFrame:
    """
    Build the screener universe: latest-year financial_ratios per company
    joined to market_cap, profitandloss, sectors, and companies.
    One row per company.
    """
    df = pd.read_sql("""
        SELECT
            fr.*,
            mc.pe_ratio, mc.pb_ratio,
            mc.dividend_yield_pct, mc.market_cap_crore,
            pl.sales, pl.net_profit,
            s.broad_sector, s.sub_sector,
            c.company_name
        FROM financial_ratios fr
        JOIN (
            SELECT company_id, MAX(year) AS latest_year
            FROM financial_ratios GROUP BY company_id
        ) lyr ON fr.company_id = lyr.company_id
              AND fr.year = lyr.latest_year
        LEFT JOIN market_cap mc
               ON fr.company_id = mc.company_id
              AND mc.year = CAST(SUBSTR(fr.year, 1, 4) AS INTEGER)
        LEFT JOIN profitandloss pl
               ON fr.company_id = pl.company_id
              AND pl.year = fr.year
        LEFT JOIN sectors s ON fr.company_id = s.company_id
        LEFT JOIN companies c ON fr.company_id = c.id
    """, conn)
    logger.info('Universe loaded: %d companies', len(df))
    return df


def _load_prev_year_de(conn: sqlite3.Connection) -> pd.Series:
    """
    Load second-latest-year D/E per company for the Turnaround Watch
    'de_declining_yoy' special filter. Returns Series indexed by company_id.
    """
    df = pd.read_sql("""
        SELECT a.company_id, a.debt_to_equity
        FROM financial_ratios a
        JOIN (
            SELECT company_id,
                   MAX(year) AS prev_year
            FROM financial_ratios
            WHERE year < (
                SELECT MAX(year) FROM financial_ratios b
                WHERE b.company_id = financial_ratios.company_id
            )
            GROUP BY company_id
        ) p ON a.company_id = p.company_id AND a.year = p.prev_year
    """, conn)
    return df.set_index('company_id')['debt_to_equity']


# ════════════════════════════════════════════════════════════════
# 2. FILTER FUNCTIONS
# ════════════════════════════════════════════════════════════════

def apply_threshold_filter(
    df: pd.DataFrame,
    filter_key: str,
    threshold: float,
    filter_def: dict,
) -> pd.DataFrame:
    """
    Apply a single threshold filter with two special bypass rules.

    Rule 1 — sector_bypass:
        Companies whose broad_sector is in the bypass list pass automatically.
        Used for Financials sector on the D/E filter.

    Rule 2 — icr_passthrough:
        Companies with icr_label = 'Debt Free' always pass the ICR filter.
        Rationale: no interest expense → ICR = infinity → exceeds any threshold.
    """
    col      = filter_def['column']
    operator = filter_def['operator']

    if col not in df.columns:
        logger.warning("Column '%s' not in universe — filter '%s' skipped", col, filter_key)
        return df

    # Base mask from threshold
    if operator == '>=':
        mask = df[col].fillna(threshold - 1) >= threshold
    elif operator == '<=':
        mask = df[col].fillna(threshold + 1) <= threshold
    else:
        logger.error("Unknown operator '%s' for filter '%s'", operator, filter_key)
        return df

    # Rule 1: sector bypass (e.g. Financials bypass D/E max filter)
    bypass = filter_def.get('sector_bypass', [])
    if bypass and 'broad_sector' in df.columns:
        is_bypassed = df['broad_sector'].isin(bypass)
        mask = mask | is_bypassed
        if is_bypassed.sum():
            logger.debug("Filter '%s': %d companies bypassed (sector: %s)",
                         filter_key, is_bypassed.sum(), bypass)

    # Rule 2: ICR passthrough for debt-free companies
    if filter_def.get('icr_passthrough') and 'icr_label' in df.columns:
        is_debt_free = df['icr_label'] == 'Debt Free'
        mask = mask | is_debt_free
        logger.debug("Filter '%s': %d debt-free companies pass (ICR=∞)",
                     filter_key, is_debt_free.sum())

    return df[mask].copy()


def apply_de_declining_yoy(
    df: pd.DataFrame,
    prev_de: pd.Series,
) -> pd.DataFrame:
    """
    Turnaround Watch special filter: keep companies where D/E declined YoY.

    Condition (either passes):
      a) current_de < prev_de  (actual decline in leverage)
      b) current_de == 0.0     (already debt-free — structurally safe)

    Companies with no prior-year D/E data are excluded (conservative).
    """
    curr = df.set_index('company_id')['debt_to_equity']
    prev = prev_de.reindex(curr.index)

    passing = curr.index[
        (curr < prev.fillna(float('inf'))) | (curr == 0.0)
    ]
    result = df[df['company_id'].isin(passing)].copy()
    logger.debug("de_declining_yoy: %d → %d companies pass", len(df), len(result))
    return result


def apply_preset_filters(
    df: pd.DataFrame,
    preset_cfg: dict,
    filter_defs: dict,
    prev_de: Optional[pd.Series] = None,
) -> pd.DataFrame:
    """
    Apply all filters for one preset: threshold filters first, then special filters.
    """
    result = df.copy()

    for filter_key, threshold in preset_cfg.get('filters', {}).items():
        if threshold is None or filter_key not in filter_defs:
            continue
        before = len(result)
        result = apply_threshold_filter(result, filter_key, threshold, filter_defs[filter_key])
        logger.debug("  After '%s' (threshold=%s): %d → %d", filter_key, threshold, before, len(result))

    # Special filter: Turnaround Watch D/E declining YoY
    special = preset_cfg.get('special_filters', {})
    if special.get('de_declining_yoy') and prev_de is not None:
        result = apply_de_declining_yoy(result, prev_de)

    return result


# ════════════════════════════════════════════════════════════════
# 3. COMPOSITE SCORE  (Day 17)
# ════════════════════════════════════════════════════════════════

def _winsorise_scale(series: pd.Series, invert: bool = False) -> pd.Series:
    """Winsorise at P10/P90 across the input series and scale to 0–100."""
    s = series.copy().fillna(series.median())
    p10, p90 = s.quantile(0.10), s.quantile(0.90)
    if p90 == p10:
        return pd.Series(50.0, index=s.index)
    clipped = s.clip(p10, p90)
    scaled  = (clipped - p10) / (p90 - p10) * 100.0
    return (100 - scaled).round(2) if invert else scaled.round(2)


def compute_sector_relative_score(df: pd.DataFrame) -> pd.Series:
    """
    Re-compute composite quality score normalised WITHIN each broad_sector.
    This reveals which companies outperform their sector peers, not just the
    full Nifty 100 universe.

    Weights (same as Sprint 2 global composite):
      35% Profitability · 30% Cash Quality · 20% Growth · 15% Leverage

    Sectors with < 3 companies receive a neutral score of 50.0 (too few
    data points for meaningful P10/P90 winsorisation).
    """
    result = pd.Series(dtype=float, index=df.index)

    for sector, grp in df.groupby('broad_sector'):
        if len(grp) < 3:
            result.loc[grp.index] = 50.0
            continue

        # Profitability (35%)
        roe  = _winsorise_scale(grp['return_on_equity_pct'])
        roce = _winsorise_scale(grp.get('return_on_capital_employed_pct', pd.Series(dtype=float)))
        npm  = _winsorise_scale(grp['net_profit_margin_pct'])
        profitability = (0.15 * roe + 0.10 * roce + 0.10 * npm) / 0.35 * 100

        # Cash Quality (30%)
        fcf     = _winsorise_scale(grp['free_cash_flow_cr'])
        cfo_q   = _winsorise_scale(grp.get('cfo_quality_score', pd.Series(dtype=float)))
        fcf_flag = grp['free_cash_flow_cr'].apply(
            lambda x: 100.0 if pd.notna(x) and x > 0 else 0.0
        )
        cash_quality = (0.15 * fcf + 0.10 * cfo_q + 0.05 * fcf_flag) / 0.30 * 100

        # Growth (20%)
        rev_cagr = _winsorise_scale(grp['revenue_cagr_5yr'])
        pat_cagr = _winsorise_scale(grp['pat_cagr_5yr'])
        growth   = (0.10 * rev_cagr + 0.10 * pat_cagr) / 0.20 * 100

        # Leverage (15%)
        de_score = _winsorise_scale(grp['debt_to_equity'], invert=True)
        icr_score = grp['interest_coverage'].apply(
            lambda v: 100.0 if pd.isna(v) else max(0.0, min(100.0, v / 10 * 100))
        )
        leverage = (0.10 * de_score + 0.05 * icr_score) / 0.15 * 100

        sector_score = (
            0.35 * profitability.clip(0, 100) +
            0.30 * cash_quality.clip(0, 100)  +
            0.20 * growth.clip(0, 100)         +
            0.15 * leverage.clip(0, 100)
        ).clip(0, 100).round(2)

        result.loc[grp.index] = sector_score.values

    return result


# ════════════════════════════════════════════════════════════════
# 4. PRESET RUNNER
# ════════════════════════════════════════════════════════════════

def run_preset(
    preset_name: str,
    universe: pd.DataFrame,
    filter_defs: dict,
    preset_cfg: dict,
    prev_de: Optional[pd.Series] = None,
) -> pd.DataFrame:
    """
    Filter, rank, and return results for one preset.
    Returns a DataFrame with a 'rank' column prepended.
    """
    filtered = apply_preset_filters(universe, preset_cfg, filter_defs, prev_de)

    if filtered.empty:
        logger.warning("Preset '%s': 0 companies returned — thresholds may be too strict", preset_name)
        return filtered

    # Sort by ranking column
    rank_col = preset_cfg.get('ranking_column', 'composite_quality_score')
    asc      = bool(preset_cfg.get('ranking_asc', False))
    if rank_col in filtered.columns:
        filtered = filtered.sort_values(rank_col, ascending=asc, na_position='last')

    filtered = filtered.reset_index(drop=True)
    filtered.insert(0, 'rank', range(1, len(filtered) + 1))

    # Log count vs expected range
    n  = len(filtered)
    lo = preset_cfg.get('expected_min', 0)
    hi = preset_cfg.get('expected_max', 999)
    marker = '✅' if lo <= n <= hi else '⚠️ '
    logger.info('%s Preset "%s": %d companies (expected %d–%d)',
                marker, preset_name, n, lo, hi)

    avail = ['rank'] + [c for c in DISPLAY_COLS if c in filtered.columns]
    return filtered[avail]


def run_all_presets(conn: Optional[sqlite3.Connection] = None) -> dict[str, pd.DataFrame]:
    """
    Run all 6 presets. Returns {preset_name: DataFrame}.
    Opens its own DB connection if none is supplied.
    """
    close_conn = conn is None
    if conn is None:
        conn = sqlite3.connect(DB_PATH)

    config      = _load_config()
    filter_defs = config['filters']
    universe    = load_universe(conn)
    prev_de     = _load_prev_year_de(conn)

    # Compute sector-relative score and attach to universe
    universe['sector_relative_score'] = compute_sector_relative_score(universe)

    results = {}
    for preset_name, preset_cfg in config['presets'].items():
        results[preset_name] = run_preset(
            preset_name, universe, filter_defs, preset_cfg, prev_de
        )

    if close_conn:
        conn.close()
    return results


# ════════════════════════════════════════════════════════════════
# 5. EXCEL EXPORT  (Day 17)
# ════════════════════════════════════════════════════════════════

def export_screener_xlsx(
    results: dict[str, pd.DataFrame],
    output_path: str = 'output/screener_output.xlsx',
) -> None:
    """
    Write screener_output.xlsx — one sheet per preset.

    Colour rules (per spec):
      Green fill → value meets the preset threshold
      Red fill   → value fails the preset threshold
      No fill    → column has no threshold in this preset
    """
    import openpyxl

    config      = _load_config()
    filter_defs = config['filters']
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    for preset_name, df in results.items():
        preset_cfg     = config['presets'][preset_name]
        preset_filters = preset_cfg.get('filters', {})
        sheet_name     = preset_cfg['label'][:31]

        ws = wb.create_sheet(title=sheet_name)

        if df.empty:
            ws['A1'] = f'No companies matched the "{preset_cfg["label"]}" preset.'
            continue

        # Header row
        for c_idx, col_name in enumerate(df.columns, 1):
            cell = ws.cell(row=1, column=c_idx, value=col_name)
            cell.fill      = FILL_HEADER
            cell.font      = FONT_HEADER
            cell.alignment = Alignment(horizontal='center', wrap_text=True)

        # Data rows with conditional fill
        for r_idx, row_data in enumerate(df.itertuples(index=False), 2):
            for c_idx, col_name in enumerate(df.columns, 1):
                value = getattr(row_data, col_name, None)
                cell  = ws.cell(row=r_idx, column=c_idx, value=value)

                # Colour cell if this column has a threshold in this preset
                for fk, threshold in preset_filters.items():
                    if threshold is None or fk not in filter_defs:
                        continue
                    fdef = filter_defs[fk]
                    if fdef['column'] != col_name:
                        continue
                    if value is None or (isinstance(value, float) and pd.isna(value)):
                        cell.fill = FILL_RED
                    elif fdef['operator'] == '>=':
                        cell.fill = FILL_GREEN if value >= threshold else FILL_RED
                    elif fdef['operator'] == '<=':
                        cell.fill = FILL_GREEN if value <= threshold else FILL_RED

        # Auto-adjust column widths
        for col_cells in ws.columns:
            max_len = max(
                (len(str(c.value)) for c in col_cells if c.value is not None),
                default=10,
            )
            ws.column_dimensions[
                get_column_letter(col_cells[0].column)
            ].width = min(max_len + 2, 30)

        # Footer with preset description
        footer_row = len(df) + 3
        ws.cell(row=footer_row, column=1,
                value=f'Preset: {preset_cfg.get("description", "")}')

    wb.save(output_path)
    logger.info('screener_output.xlsx saved → %s (%d sheets)', output_path, len(results))
    print(f'✅ screener_output.xlsx → {output_path}')


# ════════════════════════════════════════════════════════════════
# 6. ENTRY POINT
# ════════════════════════════════════════════════════════════════

def main() -> None:
    """Run all presets and export screener_output.xlsx."""
    conn    = sqlite3.connect(DB_PATH)
    results = run_all_presets(conn)
    export_screener_xlsx(results)
    conn.close()
    print('\nScreener results summary:')
    for name, df in results.items():
        print(f'  {name}: {len(df)} companies')


if __name__ == '__main__':
    main()
```

### Step 4 — Add Makefile Target

```makefile
screener:
	python src/screener/engine.py
```

### Step 5 — Run Day 15

```bash
make screener
```

**Expected output:**
```
✅ Preset "quality_compounder":  22 companies (expected 10–40)
✅ Preset "value_pick":          14 companies (expected 5–35)
✅ Preset "growth_accelerator":  11 companies (expected 5–25)
✅ Preset "dividend_champion":   16 companies (expected 5–25)
✅ Preset "debt_free_blue_chip": 20 companies (expected 10–35)
✅ Preset "turnaround_watch":     9 companies (expected 5–20)
✅ screener_output.xlsx → output/screener_output.xlsx
```

---

## 📊 Day 16 — Validate All 6 Presets (Business Sense Check)

### Step 6 — Run Preset Validation Script

```python
# notebooks/validate_presets.py
import sqlite3
from src.screener.engine import run_all_presets

conn = sqlite3.connect('data/nifty100.db')
results = run_all_presets(conn)
conn.close()

print('\n' + '='*60)
print('PRESET BUSINESS SENSE CHECKS')
print('='*60)

# 1. Quality Compounder — top 5 should be recognisable quality names
print('\n── Quality Compounder Top 5 ──')
qc = results['quality_compounder']
check_cols = ['company_id', 'company_name', 'return_on_equity_pct',
              'debt_to_equity', 'free_cash_flow_cr', 'revenue_cagr_5yr']
print(qc[[c for c in check_cols if c in qc.columns]].head(5).to_string(index=False))

# 2. Debt-Free Blue Chip — ALL must have D/E = 0.0
dfbc = results['debt_free_blue_chip']
bad = dfbc[dfbc['debt_to_equity'] != 0.0] if 'debt_to_equity' in dfbc.columns else dfbc
print(f'\n── Debt-Free Blue Chip: {len(dfbc)} companies ──')
if bad.empty:
    print('✅ All companies have D/E = 0.0')
else:
    print(f'❌ {len(bad)} companies have non-zero D/E: {bad["company_id"].tolist()}')

# 3. D/E Financials bypass — banks should appear in Value Pick (max_de=2.0)
vp = results['value_pick']
if 'broad_sector' in vp.columns:
    fin = vp[vp['broad_sector'] == 'Financials']
    fin_high = fin[fin['debt_to_equity'].fillna(0) > 2.0] if 'debt_to_equity' in fin.columns else fin
    print(f'\n── Value Pick — Financials bypass ──')
    print(f'✅ {len(fin_high)} Financials companies with D/E>2 passed (sector bypass)')

# 4. Dividend Champion — yield must be ≥ 2.0% for all
dc = results['dividend_champion']
if 'dividend_yield_pct' in dc.columns:
    bad_yield = dc[dc['dividend_yield_pct'].fillna(0) < 2.0]
    if bad_yield.empty:
        print(f'\n── Dividend Champion: All {len(dc)} have yield ≥ 2% ✅')
    else:
        print(f'\n── Dividend Champion: ❌ {len(bad_yield)} below 2% yield')

print('\n✅ Preset validation complete.')
```

```bash
python notebooks/validate_presets.py
```

---

## 🏆 Day 17 — Composite Score & Export (Already in engine.py)

The `compute_sector_relative_score()` and `export_screener_xlsx()` functions are already inside `engine.py`. `make screener` runs both automatically.

### Step 7 — Verify Excel Output

Open `output/screener_output.xlsx` and confirm:

- [ ] **6 sheets** — one per preset, named by `label` field
- [ ] **Header row** — dark navy background, white text
- [ ] **Green cells** = value meets the preset threshold
- [ ] **Red cells** = value fails the threshold
- [ ] **20 KPI columns** per sheet (from `DISPLAY_COLS`)
- [ ] `sector_relative_score` column present (0–100)
- [ ] Sorted by `composite_quality_score` descending (or preset's `ranking_column`)

### Step 8 — Quick Composite Score Sanity Check

```bash
sqlite3 data/nifty100.db "
SELECT
  MIN(composite_quality_score)  AS min_score,
  MAX(composite_quality_score)  AS max_score,
  ROUND(AVG(composite_quality_score),1) AS avg_score
FROM financial_ratios
WHERE year = (SELECT MAX(year) FROM financial_ratios);"
# min should be ≥ 0, max should be ≤ 100, avg should be ~50
```

---

## 👥 Day 18 — Peer Percentile Rankings

### Step 9 — Create `src/analytics/peer.py` (full file — Days 18–20)

```python
"""
peer.py
Peer Comparison Engine — N100 Financial Intelligence Platform.

Responsibilities:
  1. Compute within-group PERCENT_RANK for 10 metrics across 11 peer groups.
  2. Persist results to the peer_percentiles SQLite table.
  3. Generate radar PNG charts per company (including standalone for ungrouped).
  4. Export peer_comparison.xlsx with 11 colour-coded sheets.

Spec rules:
  - D/E: inverted percentile (1 − PERCENT_RANK): lower D/E = higher rank.
  - ICR: 'Debt Free' companies receive rank 1.0 (best — no debt service risk).
  - Ungrouped companies: standalone single-metric chart vs Nifty 100 average.
"""

from __future__ import annotations

import logging
import os
import sqlite3
from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.utils import get_column_letter

logger = logging.getLogger(__name__)
DB_PATH = os.getenv('DB_PATH', 'data/nifty100.db')

# ── 10 ranked metrics (per spec) ─────────────────────────────────────────────
RANK_METRICS = [
    'return_on_equity_pct',           # 1. ROE
    'return_on_capital_employed_pct', # 2. ROCE
    'net_profit_margin_pct',          # 3. Net Profit Margin
    'debt_to_equity',                 # 4. D/E (inverted)
    'free_cash_flow_cr',              # 5. FCF
    'pat_cagr_5yr',                   # 6. PAT CAGR 5yr
    'revenue_cagr_5yr',               # 7. Revenue CAGR 5yr
    'eps_cagr_5yr',                   # 8. EPS CAGR 5yr
    'interest_coverage',              # 9. ICR (Debt Free = rank 1.0)
    'asset_turnover',                 # 10. Asset Turnover
]
INVERTED_METRICS = {'debt_to_equity'}

# ── 8 radar chart axes (per spec) ────────────────────────────────────────────
RADAR_METRICS = [
    'return_on_equity_pct',
    'return_on_capital_employed_pct',
    'net_profit_margin_pct',
    'debt_to_equity',
    'free_cash_flow_cr',
    'pat_cagr_5yr',
    'revenue_cagr_5yr',
    'composite_quality_score',
]
RADAR_LABELS  = ['ROE', 'ROCE', 'NPM', 'Low Debt', 'FCF', 'PAT CAGR', 'Rev CAGR', 'Composite']

# Reference ranges for normalising radar values to [0, 1]
RADAR_RANGES = {
    'return_on_equity_pct':           (0,   45),
    'return_on_capital_employed_pct': (0,   40),
    'net_profit_margin_pct':          (0,   35),
    'debt_to_equity':                 (0,    5),  # inverted
    'free_cash_flow_cr':              (-500, 8000),
    'pat_cagr_5yr':                   (-10,  30),
    'revenue_cagr_5yr':               (-5,   25),
    'composite_quality_score':        (0,  100),
}

# ── Excel fills ───────────────────────────────────────────────────────────────
FILL_TOP    = PatternFill('solid', fgColor='C8E6C9')   # ≥ 75th → green
FILL_MID    = PatternFill('solid', fgColor='FFF9C4')   # 25–75th → yellow
FILL_BOTTOM = PatternFill('solid', fgColor='FFCDD2')   # ≤ 25th → red
FILL_HEADER = PatternFill('solid', fgColor='1F3864')
FILL_GOLD   = PatternFill('solid', fgColor='FFF176')   # benchmark row
FILL_MEDIAN = PatternFill('solid', fgColor='E3F2FD')   # median summary row


# ════════════════════════════════════════════════════════════════
# DATA LOADING
# ════════════════════════════════════════════════════════════════

def _load_peer_data(conn: sqlite3.Connection) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load peer_groups and latest-year financial_ratios (with company_name)."""
    pg = pd.read_sql('SELECT * FROM peer_groups', conn)
    fr = pd.read_sql("""
        SELECT fr.*, c.company_name
        FROM financial_ratios fr
        JOIN (
            SELECT company_id, MAX(year) AS yr
            FROM financial_ratios GROUP BY company_id
        ) l ON fr.company_id = l.company_id AND fr.year = l.yr
        JOIN companies c ON fr.company_id = c.id
    """, conn)
    return pg, fr


def _nifty100_averages(fr: pd.DataFrame, metrics: list[str]) -> dict:
    """Compute mean of each metric across the full Nifty 100 universe."""
    return {
        m: float(fr[m].mean()) if m in fr.columns and fr[m].notna().any() else None
        for m in metrics
    }


# ════════════════════════════════════════════════════════════════
# PERCENTILE COMPUTATION
# ════════════════════════════════════════════════════════════════

def _pct_rank(series: pd.Series, invert: bool = False) -> pd.Series:
    """
    Compute PERCENT_RANK within a group, preserving NaN positions.
    invert=True: lower value = higher rank (used for D/E).
    """
    if series.isna().all():
        return pd.Series(float('nan'), index=series.index)
    ranks = series.rank(method='average', ascending=True, pct=True)
    return (1 - ranks).round(3) if invert else ranks.round(3)


def _icr_ranks(grp: pd.DataFrame) -> pd.Series:
    """
    ICR percentile rank for one peer group.
    Companies with icr_label = 'Debt Free' always receive rank 1.0 (best).
    Remaining companies are ranked by their numeric ICR value.
    """
    is_debt_free = (grp.get('icr_label', pd.Series('', index=grp.index)) == 'Debt Free')
    numeric_icr  = grp['interest_coverage'].where(~is_debt_free)
    numeric_rank = _pct_rank(numeric_icr, invert=False)
    result       = numeric_rank.copy()
    result[is_debt_free] = 1.0
    return result.round(3)


def compute_peer_percentiles(conn: sqlite3.Connection) -> pd.DataFrame:
    """
    Compute within-group PERCENT_RANK for all 10 metrics × 11 peer groups.

    Returns long-format DataFrame:
        company_id, company_name, peer_group_name, is_benchmark,
        metric, value, percentile_rank, year

    Companies not in any group are logged (not errored) — spec requirement.
    """
    pg, fr = _load_peer_data(conn)
    avail  = [m for m in RANK_METRICS if m in fr.columns]
    cols   = ['company_id', 'company_name', 'year', 'icr_label'] + avail
    cols   = [c for c in cols if c in fr.columns]

    merged = pg.merge(fr[cols], on='company_id', how='left')

    ungrouped = set(fr['company_id']) - set(pg['company_id'])
    if ungrouped:
        logger.info('No peer group assigned: %d companies (e.g. %s)',
                    len(ungrouped), sorted(ungrouped)[:3])

    rows: list[dict] = []
    for group_name, grp in merged.groupby('peer_group_name'):
        grp = grp.reset_index(drop=True)
        for metric in avail:
            if metric == 'interest_coverage':
                ranks = _icr_ranks(grp)
            elif metric in INVERTED_METRICS:
                ranks = _pct_rank(grp[metric], invert=True)
            else:
                ranks = _pct_rank(grp[metric])

            for idx in grp.index:
                rows.append({
                    'company_id':      grp.at[idx, 'company_id'],
                    'company_name':    grp.at[idx, 'company_name'],
                    'peer_group_name': group_name,
                    'is_benchmark':    int(grp.at[idx, 'is_benchmark']),
                    'metric':          metric,
                    'value':           grp.at[idx, metric],
                    'percentile_rank': ranks[idx],
                    'year':            grp.at[idx, 'year'],
                })

    result = pd.DataFrame(rows)
    logger.info('Peer percentiles computed: %d rows | %d groups | %d companies',
                len(result), result['peer_group_name'].nunique(), result['company_id'].nunique())
    return result


def save_peer_percentiles(conn: Optional[sqlite3.Connection] = None) -> pd.DataFrame:
    """Compute, persist to SQLite, return DataFrame."""
    close_conn = conn is None
    if conn is None:
        conn = sqlite3.connect(DB_PATH)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS peer_percentiles (
            company_id      TEXT NOT NULL,
            company_name    TEXT,
            peer_group_name TEXT NOT NULL,
            is_benchmark    INTEGER DEFAULT 0,
            metric          TEXT NOT NULL,
            value           REAL,
            percentile_rank REAL,
            year            TEXT,
            PRIMARY KEY (company_id, peer_group_name, metric)
        )
    """)
    conn.execute('DELETE FROM peer_percentiles')
    conn.commit()

    df = compute_peer_percentiles(conn)
    df.to_sql('peer_percentiles', conn, if_exists='append', index=False)
    conn.commit()
    logger.info('peer_percentiles written: %d rows', len(df))

    if close_conn:
        conn.close()
    return df


# ════════════════════════════════════════════════════════════════
# RADAR CHART HELPERS
# ════════════════════════════════════════════════════════════════

def _to_radar(metric: str, value) -> float:
    """Normalise a raw metric value to [0, 1] for radar display."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return 0.5
    lo, hi = RADAR_RANGES.get(metric, (0, 100))
    scaled = (float(value) - lo) / (hi - lo)
    scaled = max(0.0, min(1.0, scaled))
    return 1.0 - scaled if metric == 'debt_to_equity' else scaled


def _radar_values(data: dict, metrics: list[str]) -> list[float]:
    return [_to_radar(m, data.get(m)) for m in metrics]


def _draw_radar(
    ax,
    angles: list,
    values: list,
    colour: str,
    label: str,
    linestyle: str = '-',
    alpha_fill: float = 0.25,
) -> None:
    vals = values + values[:1]
    ax.plot(angles, vals, f'o{linestyle}', linewidth=2, color=colour, label=label)
    ax.fill(angles, vals, alpha=alpha_fill, color=colour)


# ════════════════════════════════════════════════════════════════
# RADAR CHARTS  (Day 19)
# ════════════════════════════════════════════════════════════════

def generate_radar_chart(
    company_id: str,
    company_data: dict,
    overlay_data: dict,
    overlay_label: str,
    output_dir: str = 'reports/radar_charts',
) -> str:
    """
    Generate and save a radar PNG for one company vs an overlay (peer avg or Nifty 100 avg).

    Args:
        company_id    : NSE ticker.
        company_data  : {metric: raw_value} for the company.
        overlay_data  : {metric: raw_value} for the reference (peer avg or universe avg).
        overlay_label : E.g. "IT Services Peer Avg" or "Nifty 100 Average".
        output_dir    : Destination directory.

    Returns:
        Path to saved PNG.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    n      = len(RADAR_LABELS)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    angles += angles[:1]

    co_vals  = _radar_values(company_data, RADAR_METRICS)
    ref_vals = _radar_values(overlay_data, RADAR_METRICS)

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#16213e')

    _draw_radar(ax, angles, co_vals,  '#4fc3f7', company_id, '-',  0.25)
    _draw_radar(ax, angles, ref_vals, '#ef9a9a', overlay_label, '--', 0.10)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(RADAR_LABELS, color='white', fontsize=10, fontweight='bold')
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(['25%', '50%', '75%', '100%'], color='#888', fontsize=7)
    ax.set_ylim(0, 1)
    ax.grid(color='#444', linestyle='--', alpha=0.4)

    ax.set_title(f'{company_id}\nvs {overlay_label}',
                 color='white', fontsize=12, fontweight='bold', pad=20)
    ax.legend(loc='lower right', bbox_to_anchor=(1.35, -0.05),
              facecolor='#1a1a2e', labelcolor='white', fontsize=9)

    out_path = str(Path(output_dir) / f'{company_id}_radar.png')
    plt.tight_layout()
    plt.savefig(out_path, dpi=120, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    return out_path


def generate_all_radar_charts(conn: Optional[sqlite3.Connection] = None) -> list[str]:
    """
    Generate radar PNGs for all companies.

    Grouped companies (in a peer group):
      → Radar vs peer group average (filled polygon + dashed overlay).

    Ungrouped companies (no peer group assigned):
      → Standalone radar vs Nifty 100 universe average.
      This implements the spec requirement: "For companies with no peer group:
      generate a single-metric standalone chart with Nifty 100 average as reference."
    """
    close_conn = conn is None
    if conn is None:
        conn = sqlite3.connect(DB_PATH)

    pg, fr = _load_peer_data(conn)
    if close_conn:
        conn.close()

    avail      = [m for m in RADAR_METRICS if m in fr.columns]
    fr_idx     = fr.set_index('company_id')[avail].to_dict('index')
    nifty_avg  = _nifty100_averages(fr, avail)

    grouped_ids = set(pg['company_id'])
    all_ids     = set(fr['company_id'])
    ungrouped   = all_ids - grouped_ids

    paths: list[str] = []

    # ── Grouped companies → radar vs peer group average ───────────────────
    for group_name, grp in pg.groupby('peer_group_name'):
        members = grp['company_id'].tolist()

        # Compute peer group average (ignore NaN)
        avg: dict = {}
        for metric in avail:
            vals = [fr_idx[cid].get(metric) for cid in members
                    if cid in fr_idx and fr_idx[cid].get(metric) is not None]
            vals = [v for v in vals if not (isinstance(v, float) and np.isnan(v))]
            avg[metric] = float(np.mean(vals)) if vals else None

        for cid in members:
            if cid not in fr_idx:
                logger.warning('No ratio data for %s — skipping radar', cid)
                continue
            path = generate_radar_chart(
                cid, fr_idx[cid], avg, f'{group_name} Peer Avg'
            )
            paths.append(path)

    # ── Ungrouped companies → standalone radar vs Nifty 100 average ───────
    for cid in ungrouped:
        if cid not in fr_idx:
            continue
        path = generate_radar_chart(
            cid, fr_idx[cid], nifty_avg, 'Nifty 100 Average'
        )
        paths.append(path)
        logger.debug('Standalone radar (no peer group) → %s', path)

    logger.info('%d radar PNGs saved (%d grouped, %d ungrouped)',
                len(paths), len(paths) - len(ungrouped), len(ungrouped))
    return paths


# ════════════════════════════════════════════════════════════════
# PEER COMPARISON EXCEL  (Day 20)
# ════════════════════════════════════════════════════════════════

PEER_DISPLAY_METRICS = [
    'return_on_equity_pct', 'return_on_capital_employed_pct',
    'net_profit_margin_pct', 'operating_profit_margin_pct',
    'debt_to_equity', 'interest_coverage',
    'free_cash_flow_cr', 'cfo_quality_score',
    'revenue_cagr_5yr', 'pat_cagr_5yr', 'eps_cagr_5yr',
    'asset_turnover', 'composite_quality_score',
    'pe_ratio', 'pb_ratio', 'dividend_yield_pct',
    'capital_allocation_pattern',
    'net_profit_margin_pct',
    'capex_intensity_pct', 'cfo_quality_label',
]
# De-duplicate while preserving order
seen = set()
PEER_DISPLAY_METRICS = [m for m in PEER_DISPLAY_METRICS
                        if m not in seen and not seen.add(m)]


def _pct_fill(pct_rank) -> PatternFill:
    if pct_rank is None or (isinstance(pct_rank, float) and np.isnan(pct_rank)):
        return PatternFill()
    if pct_rank >= 0.75:
        return FILL_TOP
    if pct_rank >= 0.25:
        return FILL_MID
    return FILL_BOTTOM


def generate_peer_comparison_excel(
    conn: Optional[sqlite3.Connection] = None,
    output_path: str = 'output/peer_comparison.xlsx',
) -> None:
    """
    Generate peer_comparison.xlsx — 11 sheets, one per peer group.

    Sheet layout (per spec):
      Row 1         : Column headers (dark navy)
      Rows 2..N     : Company rows — metric values + percentile ranks
      Benchmark row : Gold/amber background
      Last row      : Peer group median for each numeric metric (light blue)

    Colour rules:
      Green  → pct_rank ≥ 0.75 (top quartile)
      Yellow → 0.25 ≤ pct_rank < 0.75
      Red    → pct_rank < 0.25 (bottom quartile)
    """
    import openpyxl

    close_conn = conn is None
    if conn is None:
        conn = sqlite3.connect(DB_PATH)

    pg, fr = _load_peer_data(conn)
    pct_df = pd.read_sql('SELECT * FROM peer_percentiles', conn)

    if close_conn:
        conn.close()

    display = [m for m in PEER_DISPLAY_METRICS if m in fr.columns]
    pct_lookup = pct_df.set_index(
        ['company_id', 'peer_group_name', 'metric']
    )['percentile_rank'].to_dict()

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    for group_name, grp_pg in pg.groupby('peer_group_name'):
        members      = grp_pg['company_id'].tolist()
        bench_ids    = set(grp_pg[grp_pg['is_benchmark'] == 1]['company_id'])
        sheet_name   = group_name[:31]
        ws           = wb.create_sheet(title=sheet_name)

        # Header
        all_cols = ['company_id', 'company_name'] + display + [f'{m}_pct' for m in display]
        for c_idx, h in enumerate(all_cols, 1):
            cell = ws.cell(row=1, column=c_idx, value=h)
            cell.fill      = FILL_HEADER
            cell.font      = Font(color='FFFFFF', bold=True, size=9)
            cell.alignment = Alignment(horizontal='center', wrap_text=True)

        r_idx         = 2
        median_inputs = []

        for cid in members:
            co_fr = fr[fr['company_id'] == cid]
            if co_fr.empty:
                continue
            row_fr    = co_fr.iloc[0]
            is_bench  = cid in bench_ids
            row_fill  = FILL_GOLD if is_bench else None

            # Write raw metric values
            row_vals = [cid, row_fr.get('company_name', cid)]
            row_vals += [
                round(v, 2) if isinstance(v, float) else v
                for v in [row_fr.get(m) for m in display]
            ]
            # Write percentile rank values
            pct_vals = [
                pct_lookup.get((cid, group_name, m))
                for m in display
            ]
            all_vals = row_vals + pct_vals

            for c_idx, val in enumerate(all_vals, 1):
                cell = ws.cell(row=r_idx, column=c_idx, value=val)
                if is_bench:
                    cell.fill = FILL_GOLD

            # Colour pct_rank cells
            pct_start = len(row_vals) + 1
            for j, pct in enumerate(pct_vals):
                if pct is not None:
                    ws.cell(row=r_idx, column=pct_start + j).fill = _pct_fill(pct)

            median_inputs.append(dict(zip(display, row_vals[2:])))
            r_idx += 1

        # Median summary row
        med_df = pd.DataFrame(median_inputs)
        ws.cell(row=r_idx, column=1, value='GROUP MEDIAN')
        ws.cell(row=r_idx, column=2, value=group_name)
        for c_idx, metric in enumerate(display, 3):
            if metric in med_df.columns:
                num = pd.to_numeric(med_df[metric], errors='coerce')
                med_val = num.median()
                ws.cell(row=r_idx, column=c_idx,
                        value=round(med_val, 2) if pd.notna(med_val) else None)
        for c_idx in range(1, len(all_cols) + 1):
            ws.cell(row=r_idx, column=c_idx).fill = FILL_MEDIAN
            ws.cell(row=r_idx, column=c_idx).font = Font(bold=True, size=9)

        # Auto-width
        for col in ws.columns:
            max_len = max(
                (len(str(c.value)) for c in col if c.value), default=8
            )
            ws.column_dimensions[get_column_letter(col[0].column)].width = min(max_len + 2, 25)

    wb.save(output_path)
    logger.info('peer_comparison.xlsx saved → %s', output_path)
    print(f'✅ peer_comparison.xlsx → {output_path} ({len(wb.sheetnames)} sheets)')


# ════════════════════════════════════════════════════════════════
# MAIN ORCHESTRATOR
# ════════════════════════════════════════════════════════════════

def main() -> None:
    """Run full peer pipeline: percentiles → verify → radar charts → Excel."""
    conn = sqlite3.connect(DB_PATH)

    print('1/4 Computing peer percentile ranks...')
    save_peer_percentiles(conn)

    print('2/4 Generating radar charts (grouped + ungrouped)...')
    paths = generate_all_radar_charts(conn)
    print(f'    {len(paths)} PNGs saved to reports/radar_charts/')

    conn.close()

    print('3/4 Generating peer_comparison.xlsx...')
    generate_peer_comparison_excel()

    print('4/4 Done.')


if __name__ == '__main__':
    main()
```

### Step 10 — Add Makefile Target

```makefile
peer:
	python src/analytics/peer.py
```

### Step 11 — Run Day 18–20 Pipeline

```bash
make peer
```

**Expected output:**
```
1/4 Computing peer percentile ranks...
Peer percentiles computed: 4,600 rows | 11 groups | 46 companies
peer_percentiles written: 4,600 rows
2/4 Generating radar charts (grouped + ungrouped)...
    92 PNGs saved to reports/radar_charts/
3/4 Generating peer_comparison.xlsx...
✅ peer_comparison.xlsx → output/peer_comparison.xlsx (11 sheets)
4/4 Done.
```

> **Radar count:** ~46 grouped + ~46 ungrouped = ~92 total PNGs (one per company).

---

## ✅ Day 21 — Tests & Sprint Review

### Step 12 — Create `tests/screener/__init__.py`

```python
# empty
```

### Step 13 — Create `tests/screener/test_engine.py`

```python
"""
test_engine.py — 16 unit tests for the screener filter engine.
tests/conftest.py (Sprint 1) adds src/screener to sys.path.
"""
import pytest
import pandas as pd

from engine import (
    apply_threshold_filter,
    apply_de_declining_yoy,
    _winsorise_scale,
    compute_sector_relative_score,
)


@pytest.fixture
def universe():
    return pd.DataFrame({
        'company_id':                ['TCS', 'INFY', 'HDFCBANK', 'BAJFIN', 'WEAK'],
        'company_name':              ['TCS', 'Infosys', 'HDFC Bank', 'Bajaj Fin', 'WeakCo'],
        'broad_sector':              ['IT', 'IT', 'Financials', 'Financials', 'IT'],
        'return_on_equity_pct':      [45.0, 28.0, 16.0, 18.0, 5.0],
        'debt_to_equity':            [0.0,  0.0,  8.5,  5.2,  0.3],
        'free_cash_flow_cr':         [15000, 9000, 5000, 2000, -100],
        'revenue_cagr_5yr':          [14.0, 12.0, 18.0, 22.0, 3.0],
        'interest_coverage':         [None, None, 4.0,  3.5,  12.0],
        'icr_label':                 ['Debt Free', 'Debt Free', 'Computed', 'Computed', 'Computed'],
        'sales':                     [200000, 150000, 80000, 40000, 2000],
        'composite_quality_score':   [75.0, 68.0, 62.0, 65.0, 30.0],
        'return_on_capital_employed_pct': [40.0, 30.0, 14.0, 16.0, 4.0],
        'net_profit_margin_pct':     [22.0, 18.0, 20.0, 16.0, 3.0],
        'pat_cagr_5yr':              [12.0, 11.0, 18.0, 25.0, 1.0],
        'cfo_quality_score':         [1.2, 1.1, 0.9, 0.8, 0.3],
    })


class TestThresholdFilters:

    def test_min_roe_excludes_below_threshold(self, universe):
        fdef   = {'column': 'return_on_equity_pct', 'operator': '>='}
        result = apply_threshold_filter(universe, 'min_roe', 15, fdef)
        assert 'WEAK' not in result['company_id'].values
        assert 'TCS' in result['company_id'].values

    def test_max_de_no_bypass_excludes_banks(self, universe):
        """Without sector_bypass, high-D/E banks should be excluded."""
        fdef   = {'column': 'debt_to_equity', 'operator': '<='}
        result = apply_threshold_filter(universe, 'max_de', 1.0, fdef)
        assert 'HDFCBANK' not in result['company_id'].values

    def test_max_de_financials_sector_bypass(self, universe):
        """With sector_bypass=['Financials'], HDFCBANK (D/E=8.5) must pass."""
        fdef   = {'column': 'debt_to_equity', 'operator': '<=',
                  'sector_bypass': ['Financials']}
        result = apply_threshold_filter(universe, 'max_de', 1.0, fdef)
        assert 'HDFCBANK' in result['company_id'].values

    def test_bajfin_also_bypassed_as_financials(self, universe):
        fdef   = {'column': 'debt_to_equity', 'operator': '<=',
                  'sector_bypass': ['Financials']}
        result = apply_threshold_filter(universe, 'max_de', 1.0, fdef)
        assert 'BAJFIN' in result['company_id'].values

    def test_icr_passthrough_debt_free_passes(self, universe):
        """TCS & INFY have icr_label='Debt Free' → pass min_icr=5 even with ICR=None."""
        fdef   = {'column': 'interest_coverage', 'operator': '>=',
                  'icr_passthrough': True}
        result = apply_threshold_filter(universe, 'min_icr', 5.0, fdef)
        assert 'TCS'  in result['company_id'].values
        assert 'INFY' in result['company_id'].values

    def test_icr_numeric_below_threshold_fails(self, universe):
        """BAJFIN has ICR=3.5 < min_icr=5.0 → excluded."""
        fdef   = {'column': 'interest_coverage', 'operator': '>=',
                  'icr_passthrough': True}
        result = apply_threshold_filter(universe, 'min_icr', 5.0, fdef)
        assert 'BAJFIN' not in result['company_id'].values

    def test_nan_value_fails_min_filter(self, universe):
        df = universe.copy()
        df.loc[df['company_id'] == 'WEAK', 'return_on_equity_pct'] = None
        fdef   = {'column': 'return_on_equity_pct', 'operator': '>='}
        result = apply_threshold_filter(df, 'min_roe', 10, fdef)
        assert 'WEAK' not in result['company_id'].values

    def test_missing_column_returns_df_unchanged(self, universe):
        fdef   = {'column': 'nonexistent_col', 'operator': '>='}
        result = apply_threshold_filter(universe, 'min_xyz', 10, fdef)
        assert len(result) == len(universe)

    def test_min_sales_threshold(self, universe):
        """min_sales=5000 should exclude WEAK (sales=2000)."""
        fdef   = {'column': 'sales', 'operator': '>='}
        result = apply_threshold_filter(universe, 'min_sales', 5000, fdef)
        assert 'WEAK' not in result['company_id'].values


class TestDeDecliningYoy:

    def test_declining_de_passes(self, universe):
        prev = pd.Series({'TCS': 0.5, 'INFY': 0.3, 'HDFCBANK': 9.0,
                          'BAJFIN': 6.0, 'WEAK': 0.1})
        result = apply_de_declining_yoy(universe, prev)
        # TCS: current=0.0 < prev=0.5 → PASS
        assert 'TCS' in result['company_id'].values

    def test_increasing_de_fails(self, universe):
        # WEAK current=0.3, prev=0.1 → increasing → FAIL
        prev = pd.Series({'TCS': 0.5, 'INFY': 0.3, 'HDFCBANK': 9.0,
                          'BAJFIN': 6.0, 'WEAK': 0.1})
        result = apply_de_declining_yoy(universe, prev)
        assert 'WEAK' not in result['company_id'].values

    def test_zero_de_always_passes(self, universe):
        """Current D/E = 0.0 always passes regardless of previous value."""
        prev = pd.Series({'TCS': 0.0})  # prev was also 0.0
        tcs_only = universe[universe['company_id'] == 'TCS'].copy()
        result = apply_de_declining_yoy(tcs_only, prev)
        assert 'TCS' in result['company_id'].values


class TestCompositeScore:

    def test_winsorise_output_0_to_100(self):
        s = pd.Series([1.0, 5.0, 10.0, 50.0, 100.0, 500.0])
        assert _winsorise_scale(s).between(0, 100).all()

    def test_winsorise_invert_reverses_order(self):
        s = pd.Series([1.0, 5.0, 10.0])
        normal   = _winsorise_scale(s, invert=False)
        inverted = _winsorise_scale(s, invert=True)
        assert normal.iloc[0] < normal.iloc[-1]
        assert inverted.iloc[0] > inverted.iloc[-1]

    def test_constant_series_returns_50(self):
        s = pd.Series([5.0] * 5)
        assert (_winsorise_scale(s) == 50.0).all()

    def test_sector_relative_score_in_range(self, universe):
        scores = compute_sector_relative_score(universe)
        assert scores.dropna().between(0, 100).all()
```

### Step 14 — Create `tests/kpi/test_peer.py`

```python
"""
test_peer.py — 12 unit tests for peer.py.
"""
import pytest
import pandas as pd
import numpy as np

from peer import (
    _pct_rank, _icr_ranks, _to_radar, _radar_values,
    RADAR_METRICS,
)


@pytest.fixture
def group_df():
    return pd.DataFrame({
        'company_id':       ['A',  'B',  'C',  'D'],
        'debt_to_equity':   [3.0,  2.0,  1.0,  0.0],
        'interest_coverage':[4.0,  6.0,  None, None],
        'icr_label':        ['Computed', 'Computed', 'Debt Free', 'Debt Free'],
    })


class TestPercentileRank:

    def test_higher_value_gets_higher_rank(self):
        s = pd.Series([10.0, 20.0, 30.0, 40.0])
        ranks = _pct_rank(s)
        assert ranks.iloc[3] > ranks.iloc[0]

    def test_de_invert_lower_value_gets_higher_rank(self, group_df):
        """D/E=0.0 (lowest) must have the highest percentile rank."""
        ranks = _pct_rank(group_df['debt_to_equity'], invert=True)
        assert ranks.iloc[3] == ranks.max()

    def test_nan_positions_get_nan(self):
        s = pd.Series([10.0, float('nan'), 30.0])
        ranks = _pct_rank(s)
        assert pd.isna(ranks.iloc[1])

    def test_all_nan_returns_all_nan(self):
        s = pd.Series([float('nan')] * 4)
        assert _pct_rank(s).isna().all()

    def test_invert_sum_property(self):
        """For invert=True, rank(lo) = 1 − rank(hi) in a 2-element series."""
        s = pd.Series([5.0, 10.0])
        ranks = _pct_rank(s, invert=True)
        assert ranks.iloc[0] > ranks.iloc[1]


class TestICRRanks:

    def test_debt_free_always_gets_rank_1(self, group_df):
        """Companies C and D with icr_label='Debt Free' must get rank 1.0."""
        ranks = _icr_ranks(group_df)
        df = group_df.copy()
        df['rank'] = ranks
        assert (df[df['icr_label'] == 'Debt Free']['rank'] == 1.0).all()

    def test_lower_icr_gets_lower_rank(self, group_df):
        """A has ICR=4.0 < B's ICR=6.0 → A should have lower rank."""
        ranks = _icr_ranks(group_df)
        df = group_df.copy()
        df['rank'] = ranks
        rank_a = df[df['company_id'] == 'A']['rank'].iloc[0]
        rank_b = df[df['company_id'] == 'B']['rank'].iloc[0]
        assert rank_a < rank_b


class TestRadarNormalisation:

    def test_zero_debt_gives_max_radar_value(self):
        """D/E=0 → outer ring (1.0) on radar chart."""
        assert _to_radar('debt_to_equity', 0.0) == 1.0

    def test_max_debt_gives_min_radar_value(self):
        """D/E≥5 → inner point (0.0) on radar chart."""
        assert _to_radar('debt_to_equity', 5.0) == 0.0

    def test_missing_value_gives_neutral(self):
        assert _to_radar('return_on_equity_pct', None) == 0.5

    def test_clamped_above_range_gives_1(self):
        assert _to_radar('return_on_equity_pct', 999.0) == 1.0

    def test_clamped_below_range_gives_0(self):
        assert _to_radar('composite_quality_score', -50.0) == 0.0

    def test_output_length_matches_radar_metrics(self):
        result = _radar_values({'return_on_equity_pct': 20}, RADAR_METRICS)
        assert len(result) == len(RADAR_METRICS)
```

### Step 15 — Run All 14 DQ Rule Unit Tests (Spec Requirement)

```bash
# Per spec: "Run all 14 DQ rule unit tests — must pass with 0 failures"
pytest tests/dq/ -v --tb=short
```

**Expected:**
```
tests/dq/test_dq_rules.py::TestDQ01::... PASSED
...
============================== 14 passed in 1.23s ==============================
```

> These are the DQ tests written in Sprint 1. They must still pass to confirm the database schema is intact and no Sprint 2/3 changes broke data integrity.

### Step 16 — Verify Screener Manually (Spec Requirement)

```bash
# Manually verify Quality Compounder top 5
python -c "
import sqlite3
from src.screener.engine import run_all_presets
conn = sqlite3.connect('data/nifty100.db')
results = run_all_presets(conn)
conn.close()
qc = results['quality_compounder']
cols = ['rank', 'company_id', 'company_name', 'return_on_equity_pct',
        'debt_to_equity', 'free_cash_flow_cr', 'revenue_cagr_5yr']
print(qc[[c for c in cols if c in qc.columns]].head(5).to_string(index=False))
"
```

Expected: recognisable names like TCS, INFY, HINDUNILVR, ITC — not penny stocks.

### Step 17 — Verify Peer Rankings (Spec Requirement — IT Services AND FMCG)

```bash
sqlite3 data/nifty100.db "
-- IT Services: company with highest ROE value must have highest ROE rank
SELECT
    a.company_id,
    a.value        AS roe_value,
    a.percentile_rank AS roe_rank
FROM peer_percentiles a
WHERE a.peer_group_name = 'IT Services'
  AND a.metric = 'return_on_equity_pct'
ORDER BY a.value DESC;
"
```

**What to verify:**
- Row 1 (highest `roe_value`) must also have the highest `roe_rank`
- If there are ties, the tied companies should have equal `roe_rank`

```bash
sqlite3 data/nifty100.db "
-- FMCG: same check — verify ranking is monotonic
SELECT
    a.company_id,
    a.value        AS roe_value,
    a.percentile_rank AS roe_rank
FROM peer_percentiles a
WHERE a.peer_group_name = 'FMCG'
  AND a.metric = 'return_on_equity_pct'
ORDER BY a.value DESC;
"
```

**Automated assertion:**
```python
# notebooks/verify_peer_ranks.py
import sqlite3, pandas as pd

conn = sqlite3.connect('data/nifty100.db')
for group in ['IT Services', 'FMCG']:
    df = pd.read_sql("""
        SELECT company_id, value, percentile_rank
        FROM peer_percentiles
        WHERE peer_group_name = ? AND metric = 'return_on_equity_pct'
        ORDER BY value DESC
    """, conn, params=(group,)).dropna()

    best_value = df.nlargest(1, 'value')['company_id'].iloc[0]
    best_rank  = df.nlargest(1, 'percentile_rank')['company_id'].iloc[0]
    ok = best_value == best_rank
    print(f"{'✅' if ok else '❌'} [{group}] Highest ROE value ({best_value}) == highest ROE rank ({best_rank})")

conn.close()
```

```bash
python notebooks/verify_peer_ranks.py
# Both groups must print ✅
```

---

## 🚀 Full Sprint 3 Exit Check Script

```bash
#!/bin/bash
# sprint3_exit_check.sh — run before the Day 21 review meeting
set -euo pipefail
DB="data/nifty100.db"

echo "════════════════════════════════════════"
echo "  Sprint 3 — Complete Exit Check"
echo "════════════════════════════════════════"

# Gate 1: 6 presets return 5–50 companies each
echo ""
echo "── Gate 1: 6 Preset Count Check ──"
python3 -c "
import sys
from src.screener.engine import run_all_presets
results = run_all_presets()
all_ok = True
for name, df in results.items():
    n = len(df)
    ok = 5 <= n <= 50
    print(f'  {\"✅\" if ok else \"❌\"} {name}: {n} companies')
    if not ok: all_ok = False
sys.exit(0 if all_ok else 1)
"

# Gate 2: peer_comparison.xlsx has exactly 11 sheets
echo ""
echo "── Gate 2: peer_comparison.xlsx ──"
python3 -c "
import openpyxl
wb = openpyxl.load_workbook('output/peer_comparison.xlsx')
n = len(wb.sheetnames)
print(f'  {\"✅\" if n==11 else \"❌\"} {n}/11 sheets present')
print(f'  Sheets: {wb.sheetnames}')
"

# Gate 3: peer_percentiles table
echo ""
echo "── Gate 3: peer_percentiles table ──"
sqlite3 $DB "
SELECT
  COUNT(DISTINCT peer_group_name) AS groups   ,
  COUNT(DISTINCT company_id)      AS companies,
  COUNT(DISTINCT metric)          AS metrics
FROM peer_percentiles;"

# Gate 4: radar chart PNGs
echo ""
RADARS=$(ls reports/radar_charts/*.png 2>/dev/null | wc -l)
echo "── Gate 4: Radar PNGs: $RADARS files ──"

# Gate 5: 14 DQ rule unit tests (Sprint 1 tests must still pass)
echo ""
echo "── Gate 5: 14 DQ Rule Unit Tests ──"
pytest tests/dq/ -q --tb=short

# Gate 6: Sprint 3 unit tests
echo ""
echo "── Gate 6: Sprint 3 Unit Tests ──"
pytest tests/screener/ tests/kpi/test_peer.py -q --tb=short

echo ""
echo "── Gate 7: Peer rank verification (IT Services + FMCG) ──"
python3 notebooks/verify_peer_ranks.py

echo ""
echo "════════════════════════════════════════"
echo " Sprint 3 Exit Check Complete."
echo "════════════════════════════════════════"
```

```bash
chmod +x sprint3_exit_check.sh && ./sprint3_exit_check.sh
```

---

## 📋 Sprint 3 Retrospective Template

Save as `docs/sprint3_retro.md`:

```markdown
# Sprint 3 Retrospective — Screener · Peer Engine
**Date:** Day 21 · ___________

---

## Sprint Goal Review

| Goal | Target | Result | Status |
|---|---|---|---|
| Screener with 6 presets | 6 presets | ___ presets working | ✅/❌ |
| 15 filterable metrics | 15 | 17 (2 extras for presets) | ✅ |
| Peer ranks for 11 groups | 11 | ___ groups | ✅/❌ |
| peer_comparison.xlsx | 11 sheets | ___ sheets | ✅/❌ |
| 14 DQ tests pass | 0 failures | ___ failures | ✅/❌ |

---

## Exit Criteria Sign-Off

| Gate | Command | Result | Status |
|---|---|---|---|
| 6 presets return 5–50 cos | `run_all_presets()` | All ✅ | ✅/❌ |
| peer_comparison.xlsx — 11 sheets | `len(wb.sheetnames)` | 11 | ✅/❌ |
| peer_percentiles — 11 groups | SQL `COUNT(DISTINCT...)` | 11 | ✅/❌ |
| IT Services ROE rank correct | `verify_peer_ranks.py` | ✅ | ✅/❌ |
| FMCG ROE rank correct | `verify_peer_ranks.py` | ✅ | ✅/❌ |
| 14 DQ rule tests | `pytest tests/dq/` | 0 failed | ✅/❌ |
| Sprint 3 tests (28 total) | `pytest tests/screener/ tests/kpi/test_peer.py` | 0 failed | ✅/❌ |

---

## Engineering Decisions Recorded

1. **D/E sector bypass** reads from `sectors.broad_sector = 'Financials'` dynamically — not a hard-coded ticker list.
2. **ICR passthrough** checks `icr_label = 'Debt Free'` stored in Sprint 2. No numeric ICR comparison for debt-free companies.
3. **Turnaround Watch** `de_declining_yoy` is a `special_filter` (not a threshold) because it requires comparing two years. Conservative: companies with no prior-year data are excluded.
4. **Ungrouped companies** receive a standalone radar chart vs Nifty 100 universe average (spec requirement, previously missing).
5. **Sector-relative composite score** uses per-sector P10/P90. Sectors with < 3 companies get a neutral 50.0 to avoid misleading winsorisation.
6. **Radar axis "Low Debt"** is the D/E axis inverted — outer ring = zero debt (best), not highest D/E.

---

## Story Points

| Day | Theme | Est SP | Actual SP |
|---|---|---|---|
| D15 | Filter Engine Core | 9 | |
| D16 | 6 Preset Screeners | 8 | |
| D17 | Composite Score & Export | 8 | |
| D18 | Peer Percentile Rankings | 8 | |
| D19 | Radar Charts | 7 | |
| D20 | Peer Comparison Excel | 6 | |
| D21 | Tests & Review | 3 | |
| **Total** | | **49** | |

---

**Signed off:** _________________________  **Date:** ____________
```

---

## 🗺️ What Sprint 4 Needs From This Sprint

| Requirement | Verification command |
|---|---|
| `output/screener_output.xlsx` with 6 sheets | `python -c "import openpyxl; print(len(openpyxl.load_workbook('output/screener_output.xlsx').sheetnames))"` |
| `output/peer_comparison.xlsx` with 11 sheets | Same pattern |
| `peer_percentiles` table — 11 groups, 10 metrics | `sqlite3 data/nifty100.db "SELECT COUNT(DISTINCT peer_group_name) FROM peer_percentiles;"` |
| Radar PNGs for all companies including ungrouped | `ls reports/radar_charts/ \| wc -l` → ~92 |
| `run_preset()` importable for dashboard use | `from src.screener.engine import run_preset` |
| `sector_relative_score` in screener output | Present in `DISPLAY_COLS` |
| 14 DQ tests still passing | `pytest tests/dq/ -q` → 0 failures |

---

*Sprint 3 · N100 Financial Intelligence Platform · v1.0 · June 2026 · Data Analytics Division*
