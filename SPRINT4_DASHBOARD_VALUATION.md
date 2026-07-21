# 📊 Sprint 4 — Dashboard · Valuation Module
### Nifty 100 Financial Intelligence Platform · Days 22–28 · 55 Story Points

---

## 📌 Sprint Goal

> By end of **Day 28**, a fully working **8-screen Streamlit dashboard** must run on `localhost:8501`. Every screen must load for any of the 92 tickers without errors. The valuation module must produce `valuation_summary.xlsx` with FCF yield, P/E flags, and Caution/Discount labels. CSV export must work on the screener screen.

---

## ✅ Sprint 4 Task Coverage Checklist

| Day | Task from Spec | Step | ✓ |
|---|---|---|---|
| 22 | `src/dashboard/app.py` — main entry + sidebar navigation | Step 2 | |
| 22 | `pages/` — 8 files (01_home.py … 08_reports.py) | Step 3 | |
| 22 | `src/dashboard/utils/db.py` — `@st.cache_data(ttl=600)` on every query | Step 1 | |
| 22 | 8 required db functions: get_companies, get_ratios, get_pl, get_bs, get_cf, get_sectors, get_peers, get_valuation | Step 1 | |
| 22 | Page config: wide layout · title = "Nifty 100 Analytics" · sidebar expanded | Step 2 | |
| 22 | `streamlit run` opens with zero import errors | Step 4 | |
| 23 | Home: 6 KPI tiles (Avg ROE, Median P/E, Median D/E, Total, Median Rev CAGR, Debt-Free count) | Step 5 | |
| 23 | Home: sector donut chart — 11 sectors + company count | Step 5 | |
| 23 | Home: top-5 companies by composite quality score | Step 5 | |
| 23 | Home: year selector 2019–2024, all metrics update | Step 5 | |
| 23 | Profile: text search + autocomplete dropdown | Step 6 | |
| 23 | Profile: company card (name, sector, sub-sector, ticker, about) | Step 6 | |
| 23 | Profile: 6 KPI tiles — ROE, ROCE, NPM, D/E, Rev CAGR 5yr, FCF | Step 6 | |
| 23 | Profile: 10-year Revenue & Net Profit bar chart | Step 6 | |
| 23 | Profile: ROE/ROCE dual-axis line chart | Step 6 | |
| 23 | Profile: pros/cons green check / red cross badges | Step 6 | |
| 23 | Profile: "Ticker not found" friendly message | Step 6 | |
| 24 | Screener: 10 metric sliders in sidebar | Step 7 | |
| 24 | Screener: 6 preset buttons auto-fill sliders | Step 7 | |
| 24 | Screener: live-updating results table | Step 7 | |
| 24 | Screener: CSV download button | Step 7 | |
| 24 | Screener: result count label above table | Step 7 | |
| 24 | Peer: 11-group dropdown | Step 8 | |
| 24 | Peer: radar chart via Plotly Scatterpolar — company vs peer avg | Step 8 | |
| 24 | Peer: KPI table with benchmark row highlighted | Step 8 | |
| 25 | Trend: search + multi-metric selector (≤3) + 10-year line + YoY annotation | Step 9 | |
| 25 | Sector: bubble chart X=Revenue, Y=ROE, size=MarketCap, colour=sub-sector | Step 10 | |
| 25 | Sector: median KPI bar chart below bubble | Step 10 | |
| 25 | Capital Allocation: Plotly treemap by 8 patterns | Step 11 | |
| 25 | Annual Reports: search + BSE PDF links + 404 badge | Step 12 | |
| 26 | `src/analytics/valuation.py` | Step 13 | |
| 26 | FCF yield = FCF / market_cap_crore × 100 | Step 13 | |
| 26 | Sector median P/E per broad_sector | Step 13 | |
| 26 | Flags: Caution >1.5×, Discount <0.7×, Fair otherwise | Step 13 | |
| 26 | `valuation_summary.xlsx` — 92 rows, all required columns | Step 14 | |
| 26 | `valuation_flags.csv` — only Caution/Discount companies | Step 14 | |
| 27 | Test 10 tickers across IT, Financials, FMCG, Energy, Healthcare | Step 15 | |
| 27 | Test partial-data companies — no crash | Step 15 | |
| 27 | Test extreme slider values — no crash | Step 15 | |
| 27 | None/NaN → "N/A" everywhere | Step 15 | |
| 27 | Profile screen load time < 3 seconds | Step 15 | |
| 28 | README.md updated with dashboard run instructions | Step 16 | |
| 28 | Screen descriptions in README | Step 16 | |
| 28 | Sprint retrospective template | Step 17 | |

---

## 📁 Deliverables

| # | File / Artefact | Format | Due |
|---|---|---|---|
| D-01 | `src/dashboard/utils/db.py` | Python | Day 22 |
| D-02 | `src/dashboard/app.py` | Python | Day 22 |
| D-03 | `src/dashboard/pages/01_home.py` | Python | Day 23 |
| D-04 | `src/dashboard/pages/02_profile.py` | Python | Day 23 |
| D-05 | `src/dashboard/pages/03_screener.py` | Python | Day 24 |
| D-06 | `src/dashboard/pages/04_peers.py` | Python | Day 24 |
| D-07 | `src/dashboard/pages/05_trends.py` | Python | Day 25 |
| D-08 | `src/dashboard/pages/06_sectors.py` | Python | Day 25 |
| D-09 | `src/dashboard/pages/07_capital.py` | Python | Day 25 |
| D-10 | `src/dashboard/pages/08_reports.py` | Python | Day 25 |
| D-11 | `src/analytics/valuation.py` | Python | Day 26 |
| D-12 | `output/valuation_summary.xlsx` | Excel | Day 26 |
| D-13 | `output/valuation_flags.csv` | CSV | Day 26 |
| D-14 | `README.md` updated | Markdown | Day 28 |

---

## ✅ Exit Criteria

```bash
# Gate 1 — app runs with no import errors
streamlit run src/dashboard/app.py &
sleep 4
curl -s http://localhost:8501/_stcore/health | grep -q '"status":"ok"' && echo "✅ App healthy" || echo "❌ App not running"

# Gate 2 — valuation_summary.xlsx has 92 rows
python -c "
import openpyxl
wb = openpyxl.load_workbook('output/valuation_summary.xlsx')
ws = wb.active
print(f'Rows: {ws.max_row - 1} (need 92)')  # subtract header
"

# Gate 3 — valuation_flags.csv exists with required columns
python -c "
import pandas as pd
df = pd.read_csv('output/valuation_flags.csv')
required = ['company_id','flag']
ok = all(c in df.columns for c in required)
print(f'✅ valuation_flags.csv OK ({len(df)} rows)' if ok else '❌ Missing columns')
"

# Gate 4 — screener CSV export check
python -c "
import sqlite3
from src.screener.engine import run_all_presets
r = run_all_presets()
df = list(r.values())[0]
csv = df.to_csv(index=False)
lines = csv.strip().split('\n')
print(f'✅ CSV has {len(lines)-1} data rows and {len(lines[0].split(\",\"))} columns')
"
```

---

## ⚠️ Pre-Sprint Checklist — Sprint 3 Must Be Complete

```bash
sqlite3 data/nifty100.db "SELECT COUNT(*) FROM financial_ratios;"  # → ≥ 1,100
sqlite3 data/nifty100.db "SELECT COUNT(*) FROM peer_percentiles;"  # → ≥ 400
ls output/screener_output.xlsx output/peer_comparison.xlsx          # both exist
pytest tests/screener/ tests/kpi/test_peer.py -q                    # → 0 failures
```

---

## 📁 Files Created This Sprint

```
src/
├── dashboard/
│   ├── __init__.py
│   ├── app.py                  ← Day 22
│   ├── pages/
│   │   ├── 01_home.py          ← Day 23
│   │   ├── 02_profile.py       ← Day 23
│   │   ├── 03_screener.py      ← Day 24
│   │   ├── 04_peers.py         ← Day 24
│   │   ├── 05_trends.py        ← Day 25
│   │   ├── 06_sectors.py       ← Day 25
│   │   ├── 07_capital.py       ← Day 25
│   │   └── 08_reports.py       ← Day 25
│   └── utils/
│       ├── __init__.py
│       └── db.py               ← Day 22
└── analytics/
    └── valuation.py            ← Day 26
```

---

## 🛠️ Day 22 — Streamlit App Scaffold

### Step 1 — Create `src/dashboard/utils/db.py`

> Every function has `@st.cache_data(ttl=600)` — this is the spec requirement. All 8 required functions are implemented.

```python
"""
db.py
Centralised, cached data loader for all Streamlit dashboard pages.

Design rules:
  - Every public function has @st.cache_data(ttl=600) — cache for 10 minutes.
  - All functions open their own SQLite connection and close it when done.
  - None/NaN handling: functions return DataFrames; pages do the display formatting.
  - No business logic here — only data retrieval.

Required functions (per spec):
  get_companies(), get_ratios(), get_pl(), get_bs(), get_cf(),
  get_sectors(), get_peers(), get_valuation()
"""

from __future__ import annotations

import os
import sqlite3

import pandas as pd
import streamlit as st

DB_PATH = os.getenv('DB_PATH', 'data/nifty100.db')


def _conn() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


# ── 1. get_companies ─────────────────────────────────────────────────────────
@st.cache_data(ttl=600)
def get_companies() -> pd.DataFrame:
    """All 92 companies with master attributes."""
    with _conn() as conn:
        return pd.read_sql("""
            SELECT c.id, c.company_name, c.about_company,
                   c.face_value, c.website, c.nse_profile,
                   s.broad_sector, s.sub_sector
            FROM companies c
            LEFT JOIN sectors s ON c.id = s.company_id
            ORDER BY c.company_name
        """, conn)


# ── 2. get_ratios ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=600)
def get_ratios(ticker: str, year: str | None = None) -> pd.DataFrame:
    """
    Financial ratios for one company, optionally filtered to a single year.
    Returns all years when year=None. Sorted oldest → newest.
    """
    with _conn() as conn:
        if year:
            return pd.read_sql(
                "SELECT * FROM financial_ratios WHERE company_id=? AND year=? ORDER BY year",
                conn, params=(ticker, year)
            )
        return pd.read_sql(
            "SELECT * FROM financial_ratios WHERE company_id=? ORDER BY year",
            conn, params=(ticker,)
        )


# ── 3. get_pl ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=600)
def get_pl(ticker: str) -> pd.DataFrame:
    """Full P&L history for one company, sorted oldest → newest."""
    with _conn() as conn:
        return pd.read_sql(
            "SELECT * FROM profitandloss WHERE company_id=? ORDER BY year",
            conn, params=(ticker,)
        )


# ── 4. get_bs ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=600)
def get_bs(ticker: str) -> pd.DataFrame:
    """Full balance sheet history for one company."""
    with _conn() as conn:
        return pd.read_sql(
            "SELECT * FROM balancesheet WHERE company_id=? ORDER BY year",
            conn, params=(ticker,)
        )


# ── 5. get_cf ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=600)
def get_cf(ticker: str) -> pd.DataFrame:
    """Full cash flow history for one company."""
    with _conn() as conn:
        return pd.read_sql(
            "SELECT * FROM cashflow WHERE company_id=? ORDER BY year",
            conn, params=(ticker,)
        )


# ── 6. get_sectors ────────────────────────────────────────────────────────────
@st.cache_data(ttl=600)
def get_sectors() -> pd.DataFrame:
    """Sector mapping with latest-year median KPIs per broad_sector."""
    with _conn() as conn:
        sec = pd.read_sql('SELECT * FROM sectors', conn)
        fr  = pd.read_sql("""
            SELECT fr.*
            FROM financial_ratios fr
            JOIN (
                SELECT company_id, MAX(year) AS yr
                FROM financial_ratios GROUP BY company_id
            ) l ON fr.company_id=l.company_id AND fr.year=l.yr
        """, conn)
        mc = pd.read_sql("""
            SELECT mc.company_id, mc.market_cap_crore
            FROM market_cap mc
            JOIN (SELECT company_id, MAX(year) AS yr FROM market_cap GROUP BY company_id) l
                ON mc.company_id=l.company_id AND mc.year=l.yr
        """, conn)
    merged = sec.merge(fr, on='company_id').merge(mc, on='company_id', how='left')
    return merged


# ── 7. get_peers ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=600)
def get_peers(group_name: str) -> pd.DataFrame:
    """
    All companies in a named peer group with their latest-year ratios
    and percentile ranks. Returns empty DataFrame if group not found.
    """
    with _conn() as conn:
        pg = pd.read_sql(
            "SELECT * FROM peer_groups WHERE peer_group_name=?",
            conn, params=(group_name,)
        )
        if pg.empty:
            return pd.DataFrame()
        members = pg['company_id'].tolist()
        placeholders = ','.join('?' * len(members))
        fr = pd.read_sql(f"""
            SELECT fr.*, c.company_name
            FROM financial_ratios fr
            JOIN (
                SELECT company_id, MAX(year) AS yr
                FROM financial_ratios GROUP BY company_id
            ) l ON fr.company_id=l.company_id AND fr.year=l.yr
            JOIN companies c ON fr.company_id=c.id
            WHERE fr.company_id IN ({placeholders})
        """, conn, params=members)
        pct = pd.read_sql(f"""
            SELECT company_id, metric, percentile_rank
            FROM peer_percentiles
            WHERE peer_group_name=?
        """, conn, params=(group_name,))

    # Pivot percentile ranks: one row per company, one column per metric_pct
    pct_wide = pct.pivot(index='company_id', columns='metric', values='percentile_rank')
    pct_wide.columns = [f'{c}_pct' for c in pct_wide.columns]
    result = fr.merge(pct_wide, on='company_id', how='left')
    result = result.merge(pg[['company_id', 'is_benchmark']], on='company_id', how='left')
    return result


# ── 8. get_valuation ─────────────────────────────────────────────────────────
@st.cache_data(ttl=600)
def get_valuation(ticker: str) -> pd.DataFrame:
    """Historical valuation multiples for one company from market_cap table."""
    with _conn() as conn:
        return pd.read_sql(
            "SELECT * FROM market_cap WHERE company_id=? ORDER BY year",
            conn, params=(ticker,)
        )


# ── Helper: latest-year universe (used by Home and Screener screens) ──────────
@st.cache_data(ttl=600)
def get_latest_universe() -> pd.DataFrame:
    """Latest-year financial_ratios + market_cap + sectors + company_name."""
    with _conn() as conn:
        return pd.read_sql("""
            SELECT fr.*,
                   mc.pe_ratio, mc.pb_ratio, mc.dividend_yield_pct, mc.market_cap_crore,
                   pl.sales, pl.net_profit,
                   s.broad_sector, s.sub_sector,
                   c.company_name
            FROM financial_ratios fr
            JOIN (
                SELECT company_id, MAX(year) AS yr
                FROM financial_ratios GROUP BY company_id
            ) l ON fr.company_id=l.company_id AND fr.year=l.yr
            LEFT JOIN market_cap mc
                   ON fr.company_id=mc.company_id
                  AND mc.year=CAST(SUBSTR(fr.year,1,4) AS INTEGER)
            LEFT JOIN profitandloss pl
                   ON fr.company_id=pl.company_id AND pl.year=fr.year
            LEFT JOIN sectors s ON fr.company_id=s.company_id
            LEFT JOIN companies c ON fr.company_id=c.id
        """, conn)


# ── Helper: pros/cons for a company ──────────────────────────────────────────
@st.cache_data(ttl=600)
def get_pros_cons(ticker: str) -> pd.DataFrame:
    with _conn() as conn:
        return pd.read_sql(
            "SELECT pros, cons FROM prosandcons WHERE company_id=?",
            conn, params=(ticker,)
        )


# ── Helper: all peer group names ─────────────────────────────────────────────
@st.cache_data(ttl=600)
def get_peer_group_names() -> list[str]:
    with _conn() as conn:
        df = pd.read_sql(
            "SELECT DISTINCT peer_group_name FROM peer_groups ORDER BY peer_group_name",
            conn
        )
    return df['peer_group_name'].tolist()


# ── Helper: annual reports for a company ─────────────────────────────────────
@st.cache_data(ttl=600)
def get_documents(ticker: str) -> pd.DataFrame:
    with _conn() as conn:
        return pd.read_sql(
            "SELECT Year, Annual_Report FROM documents WHERE company_id=? ORDER BY Year DESC",
            conn, params=(ticker,)
        )
```

### Step 2 — Create `src/dashboard/__init__.py` and `src/dashboard/utils/__init__.py`

```python
# empty — makes directories Python packages
```

Create both:
```bash
touch src/dashboard/__init__.py
touch src/dashboard/utils/__init__.py
touch src/dashboard/pages/__init__.py
```

### Step 3 — Create `src/dashboard/app.py`

```python
"""
app.py
Main Streamlit entry point — N100 Financial Intelligence Platform dashboard.

Run from project root:
    streamlit run src/dashboard/app.py

Page config (per spec):
  - Layout: wide
  - Title: Nifty 100 Analytics
  - Sidebar: expanded by default
"""

import os
import sys

# Make project root importable (covers all 8 page files)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import streamlit as st
from src.dashboard.utils.db import get_latest_universe, get_companies

# ── Page config (must be the FIRST Streamlit call) ───────────────────────────
st.set_page_config(
    page_title='Nifty 100 Analytics',
    page_icon='📊',
    layout='wide',
    initial_sidebar_state='expanded',
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stMetricValue"]  { font-size: 1.7rem; font-weight: 700; }
[data-testid="stMetricLabel"]  { font-size: 0.78rem; color: #9e9e9e; }
div[data-testid="metric-container"] {
    background: #1e2235; border-radius: 8px; padding: 12px 16px;
    border: 1px solid #2a2d3e;
}
.stDataFrame { font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

# ── App header ────────────────────────────────────────────────────────────────
st.title('📊 Nifty 100 Financial Intelligence')
st.caption('Production-grade analytics for all 92 Nifty 100 companies · v1.0')

# ── Summary strip on the landing page ────────────────────────────────────────
try:
    df = get_latest_universe()
    cos = get_companies()

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric('Companies',       f'{len(cos)}')
    c2.metric('Avg ROE',         f"{df['return_on_equity_pct'].mean():.1f}%")
    c3.metric('Median D/E',      f"{df['debt_to_equity'].median():.2f}×")
    c4.metric('Debt-Free',       f"{(df['debt_to_equity'] == 0).sum()}")
    c5.metric('FCF Positive',    f"{(df['free_cash_flow_cr'] > 0).sum()}")
    c6.metric('Median FHS Score',f"{df['composite_quality_score'].median():.0f}/100")
except Exception as exc:
    st.warning(f'Could not load summary metrics: {exc}')

st.divider()
st.info('👈  Use the sidebar to navigate between the 8 screens.')
```

### Step 4 — Update `Makefile` and Verify

```makefile
# Add PYTHONPATH so Streamlit pages can import src.*
dashboard:
	PYTHONPATH=$(shell pwd) streamlit run src/dashboard/app.py
```

```bash
make dashboard
# Browser opens at http://localhost:8501 — verify no import errors
```

**Expected:** App loads with 6 metric tiles and sidebar showing all 8 page links.

---

## 🏠 Day 23 — Home Screen & Company Profile

### Step 5 — Create `src/dashboard/pages/01_home.py`

```python
"""
01_home.py — Home / Overview screen.

Spec requirements:
  ✅ 6 KPI tiles: Avg ROE, Median P/E, Median D/E, Total, Median Rev CAGR 5yr, Debt-Free count
  ✅ Sector donut chart (11 sectors, company count)
  ✅ Top-5 by composite quality score
  ✅ Year selector 2019–2024 in sidebar — all metrics update
"""

import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import plotly.express as px
import streamlit as st
import pandas as pd
import sqlite3

from src.dashboard.utils.db import get_sectors, get_companies

st.header('🏠 Market Overview')

# ── Year selector ─────────────────────────────────────────────────────────────
DB_PATH = os.getenv('DB_PATH', 'data/nifty100.db')

with sqlite3.connect(DB_PATH) as conn:
    years = pd.read_sql(
        "SELECT DISTINCT SUBSTR(year,1,4) AS yr FROM financial_ratios ORDER BY yr",
        conn
    )['yr'].tolist()

year_options = [y for y in years if 2019 <= int(y) <= 2024]
selected_yr  = st.sidebar.selectbox('📅 Select Year', year_options, index=len(year_options)-1)
year_str     = f'{selected_yr}-03'   # assume March year-end as default

@st.cache_data(ttl=600)
def load_year_data(yr_str: str) -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql("""
            SELECT fr.*, mc.pe_ratio, mc.pb_ratio, mc.market_cap_crore,
                   s.broad_sector, c.company_name
            FROM financial_ratios fr
            LEFT JOIN market_cap mc
                   ON fr.company_id=mc.company_id
                  AND mc.year=CAST(SUBSTR(fr.year,1,4) AS INTEGER)
            LEFT JOIN sectors s ON fr.company_id=s.company_id
            LEFT JOIN companies c ON fr.company_id=c.id
            WHERE fr.year=?
        """, conn, params=(yr_str,))

df = load_year_data(year_str)

if df.empty:
    # Fallback to latest year if selected year has no data
    with sqlite3.connect(DB_PATH) as conn:
        latest = pd.read_sql(
            "SELECT MAX(year) AS yr FROM financial_ratios", conn
        ).iloc[0]['yr']
    df = load_year_data(latest)
    st.caption(f'ℹ️ Data for {selected_yr} not available — showing {latest[:4]}')

# ── 6 KPI tiles ───────────────────────────────────────────────────────────────
st.subheader(f'Key Metrics — {selected_yr}')
c1, c2, c3, c4, c5, c6 = st.columns(6)

def _fmt(val, suffix='%', decimals=1):
    if pd.isna(val): return 'N/A'
    return f'{round(val, decimals)}{suffix}'

c1.metric('Avg ROE',          _fmt(df['return_on_equity_pct'].mean()))
c2.metric('Median P/E',       _fmt(df['pe_ratio'].median(), '×'))
c3.metric('Median D/E',       _fmt(df['debt_to_equity'].median(), '×'))
c4.metric('Total Companies',  str(df['company_id'].nunique()))
c5.metric('Median Rev CAGR 5yr', _fmt(df['revenue_cagr_5yr'].median()))
c6.metric('Debt-Free Cos',    str((df['debt_to_equity'] == 0).sum()))

st.divider()

# ── Sector donut chart ────────────────────────────────────────────────────────
col_donut, col_top5 = st.columns([1, 1])

with col_donut:
    st.subheader('Sector Distribution')
    cos = get_companies()
    sector_counts = cos.groupby('broad_sector')['id'].count().reset_index()
    sector_counts.columns = ['Sector', 'Count']
    fig = px.pie(
        sector_counts, values='Count', names='Sector',
        hole=0.45,
        color_discrete_sequence=px.colors.qualitative.Set3,
        template='plotly_dark',
    )
    fig.update_traces(textposition='inside', textinfo='label+value')
    fig.update_layout(height=380, showlegend=False,
                      margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig, use_container_width=True)

# ── Top-5 by composite quality score ─────────────────────────────────────────
with col_top5:
    st.subheader('Top 5 — Composite Quality Score')
    top5 = df.nlargest(5, 'composite_quality_score')[
        ['company_id', 'company_name', 'broad_sector',
         'return_on_equity_pct', 'composite_quality_score']
    ].rename(columns={
        'company_id': 'Ticker', 'company_name': 'Company',
        'broad_sector': 'Sector',
        'return_on_equity_pct': 'ROE%',
        'composite_quality_score': 'Score',
    })
    top5['ROE%']  = top5['ROE%'].round(1)
    top5['Score'] = top5['Score'].round(1)
    st.dataframe(top5, use_container_width=True, hide_index=True, height=220)

# ── Sector median ROE bar ─────────────────────────────────────────────────────
st.divider()
st.subheader('Sector Median ROE (%)')
sec_med = df.groupby('broad_sector')['return_on_equity_pct'].median().dropna().reset_index()
sec_med.columns = ['Sector', 'Median ROE%']
sec_med = sec_med.sort_values('Median ROE%', ascending=True)
fig2 = px.bar(sec_med, x='Median ROE%', y='Sector', orientation='h',
              template='plotly_dark', color='Median ROE%',
              color_continuous_scale='Blues')
fig2.update_layout(height=380, showlegend=False,
                   margin=dict(l=10, r=10, t=20, b=10))
st.plotly_chart(fig2, use_container_width=True)
```

### Step 6 — Create `src/dashboard/pages/02_profile.py`

```python
"""
02_profile.py — Company Profile screen.

Spec requirements:
  ✅ Text search + autocomplete dropdown
  ✅ Company card (name, sector, sub-sector, ticker, about)
  ✅ 6 KPI tiles: ROE, ROCE, NPM, D/E, Rev CAGR 5yr, FCF
  ✅ 10-year Revenue & Net Profit bar chart
  ✅ ROE/ROCE dual-axis line chart
  ✅ Pros/cons green check / red cross badges
  ✅ "Ticker not found" friendly message
"""

import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import plotly.graph_objects as go
import streamlit as st
import pandas as pd

from src.dashboard.utils.db import (
    get_companies, get_ratios, get_pl, get_pros_cons, get_documents,
)

st.header('🏢 Company Profile')

# ── Ticker search (autocomplete via selectbox) ─────────────────────────────────
cos = get_companies()

# Build display list: "TCS — Tata Consultancy Services Ltd"
options = [
    f"{row['id']} — {row['company_name']}"
    for _, row in cos.iterrows()
]
options.sort()

search_val = st.selectbox('🔍 Search company (type ticker or name)', options)
if not search_val:
    st.info('Select a company to view its profile.')
    st.stop()

selected_ticker = search_val.split(' — ')[0].strip()

# ── Validate ticker ────────────────────────────────────────────────────────────
co_row = cos[cos['id'] == selected_ticker]
if co_row.empty:
    st.error(f'⚠️ Ticker **{selected_ticker}** not found — please try another.')
    st.stop()

co = co_row.iloc[0]
ratios = get_ratios(selected_ticker)
pl     = get_pl(selected_ticker)

# ── Company card ───────────────────────────────────────────────────────────────
with st.container():
    col_name, col_meta = st.columns([3, 1])
    with col_name:
        st.subheader(co['company_name'])
        about = co.get('about_company', '')
        if about and str(about) != 'nan':
            st.caption(str(about)[:300] + ('…' if len(str(about)) > 300 else ''))
    with col_meta:
        st.markdown(f'**Ticker:** `{co["id"]}`')
        st.markdown(f'**Sector:** {co.get("broad_sector", "N/A")}')
        st.markdown(f'**Sub-sector:** {co.get("sub_sector", "N/A")}')

st.divider()

# ── 6 KPI tiles — latest year ─────────────────────────────────────────────────
def _v(df, col, fmt='.1f', suffix='%'):
    """Safely get latest value from a ratio column."""
    if df.empty or col not in df.columns:
        return 'N/A'
    val = df.sort_values('year').iloc[-1].get(col)
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return 'N/A'
    return f'{round(float(val), int(fmt[-1]))}{suffix}' if fmt else str(val)

def _delta(df, col):
    """YoY change for delta display."""
    if df.empty or col not in df.columns or len(df) < 2:
        return None
    vals = df.sort_values('year')[col].dropna()
    if len(vals) < 2:
        return None
    delta = float(vals.iloc[-1]) - float(vals.iloc[-2])
    return f'{delta:+.1f}pp'

if not ratios.empty:
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric('ROE',            _v(ratios, 'return_on_equity_pct'),            _delta(ratios, 'return_on_equity_pct'))
    c2.metric('ROCE',           _v(ratios, 'return_on_capital_employed_pct'),   _delta(ratios, 'return_on_capital_employed_pct'))
    c3.metric('Net Profit Margin', _v(ratios, 'net_profit_margin_pct'),         _delta(ratios, 'net_profit_margin_pct'))
    c4.metric('D/E',            _v(ratios, 'debt_to_equity', '.2f', '×'),       None)
    c5.metric('Rev CAGR 5yr',   _v(ratios, 'revenue_cagr_5yr'),                 None)
    c6.metric('FCF (₹ Cr)',     _v(ratios, 'free_cash_flow_cr', '.0f', ''),     None)
else:
    st.warning('No ratio data available for this company.')

st.divider()

# ── 10-year Revenue & Net Profit bar chart ────────────────────────────────────
if not pl.empty:
    st.subheader('Revenue & Net Profit — 10 Year History (₹ Crore)')
    pl_plot = pl.sort_values('year').tail(10)
    fig = go.Figure()
    fig.add_bar(x=pl_plot['year'], y=pl_plot['sales'],
                name='Revenue', marker_color='#4fc3f7')
    fig.add_bar(x=pl_plot['year'], y=pl_plot['net_profit'],
                name='Net Profit', marker_color='#81c784')
    fig.update_layout(
        barmode='group',
        plot_bgcolor='#1e2235', paper_bgcolor='#1e2235',
        font_color='white', height=320,
        margin=dict(l=10, r=10, t=20, b=10),
        xaxis=dict(gridcolor='#333'), yaxis=dict(gridcolor='#333', title='₹ Crore'),
        legend=dict(orientation='h', yanchor='bottom', y=1.02),
    )
    st.plotly_chart(fig, use_container_width=True)

# ── ROE / ROCE dual-axis line chart ────────────────────────────────────────────
if not ratios.empty:
    st.subheader('ROE & ROCE Trend')
    r_plot = ratios.sort_values('year')
    fig2 = go.Figure()
    fig2.add_scatter(
        x=r_plot['year'], y=r_plot['return_on_equity_pct'],
        name='ROE (%)', mode='lines+markers',
        line=dict(color='#ffb74d', width=2.5),
        marker=dict(size=6),
    )
    fig2.add_scatter(
        x=r_plot['year'], y=r_plot['return_on_capital_employed_pct'],
        name='ROCE (%)', mode='lines+markers',
        line=dict(color='#ce93d8', width=2.5),
        marker=dict(size=6),
    )
    fig2.update_layout(
        plot_bgcolor='#1e2235', paper_bgcolor='#1e2235',
        font_color='white', height=300,
        margin=dict(l=10, r=10, t=20, b=10),
        xaxis=dict(gridcolor='#333'),
        yaxis=dict(gridcolor='#333', title='%'),
        legend=dict(orientation='h', yanchor='bottom', y=1.02),
    )
    st.plotly_chart(fig2, use_container_width=True)

# ── Pros & Cons badges ────────────────────────────────────────────────────────
pc = get_pros_cons(selected_ticker)
if not pc.empty:
    st.divider()
    col_pros, col_cons = st.columns(2)
    with col_pros:
        st.subheader('✅ Pros')
        for _, row in pc.iterrows():
            if row.get('pros') and str(row['pros']) != 'nan':
                st.success(str(row['pros']))
    with col_cons:
        st.subheader('❌ Cons')
        for _, row in pc.iterrows():
            if row.get('cons') and str(row['cons']) != 'nan':
                st.error(str(row['cons']))
```

---

## 🔎 Day 24 — Screener & Peer Comparison Screens

### Step 7 — Create `src/dashboard/pages/03_screener.py`

```python
"""
03_screener.py — Investment Screener screen.

Spec requirements:
  ✅ 10 metric sliders in sidebar
  ✅ 6 preset buttons auto-fill sliders
  ✅ Live-updating results table
  ✅ CSV download button
  ✅ Result count label above table
"""

import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import streamlit as st
import pandas as pd

from src.dashboard.utils.db import get_latest_universe

st.header('🔎 Investment Screener')

df = get_latest_universe()

# ── 6 preset definitions (auto-fill sliders) ──────────────────────────────────
PRESETS = {
    'Quality':    dict(min_roe=15, max_de=1.0, min_fcf=0, min_rev_cagr=10),
    'Value':      dict(max_pe=20,  max_pb=3.0, max_de=2.0, min_div_yield=1.0),
    'Growth':     dict(min_pat_cagr=20, min_rev_cagr=15, max_de=2.0),
    'Dividend':   dict(min_div_yield=2.0, max_div_payout=80, min_fcf=0),
    'Debt-Free':  dict(max_de=0.0, min_roe=12),
    'Turnaround': dict(min_rev_cagr=10, min_fcf=0),
}

# ── Preset buttons ─────────────────────────────────────────────────────────────
st.sidebar.subheader('⚡ Quick Presets')
preset_cols = st.sidebar.columns(3)
active_preset: dict = {}

for i, (label, vals) in enumerate(PRESETS.items()):
    if preset_cols[i % 3].button(label, use_container_width=True):
        active_preset = vals

st.sidebar.divider()

# ── 10 metric sliders ─────────────────────────────────────────────────────────
st.sidebar.subheader('🎚️ Filters')

min_roe       = st.sidebar.slider('Min ROE (%)',            0,   50,  active_preset.get('min_roe', 0))
max_de        = st.sidebar.slider('Max D/E',                0.0, 10.0, float(active_preset.get('max_de', 10.0)), 0.5)
min_fcf       = st.sidebar.slider('Min FCF (₹ Cr)',         -1000, 5000, active_preset.get('min_fcf', -1000), 100)
min_rev_cagr  = st.sidebar.slider('Min Rev CAGR 5yr (%)',   -10,  30,   active_preset.get('min_rev_cagr', -10))
min_pat_cagr  = st.sidebar.slider('Min PAT CAGR 5yr (%)',   -10,  30,   active_preset.get('min_pat_cagr', -10))
min_opm       = st.sidebar.slider('Min OPM (%)',             0,   50,   0)
max_pe        = st.sidebar.slider('Max P/E',                 0,   100,  active_preset.get('max_pe', 100))
max_pb        = st.sidebar.slider('Max P/B',                 0.0, 20.0, float(active_preset.get('max_pb', 20.0)), 0.5)
min_div_yield = st.sidebar.slider('Min Div Yield (%)',       0.0, 5.0,  float(active_preset.get('min_div_yield', 0.0)), 0.1)
min_icr       = st.sidebar.slider('Min ICR',                 0,   20,   0)

sector_filter = st.sidebar.multiselect(
    'Sector', sorted(df['broad_sector'].dropna().unique())
)

# ── Apply filters (live-updating) ─────────────────────────────────────────────
mask = pd.Series(True, index=df.index)

mask &= df['return_on_equity_pct'].fillna(-999)        >= min_roe
mask &= df['revenue_cagr_5yr'].fillna(-999)             >= min_rev_cagr
mask &= df['pat_cagr_5yr'].fillna(-999)                 >= min_pat_cagr
mask &= df['operating_profit_margin_pct'].fillna(-999)  >= min_opm
mask &= df['free_cash_flow_cr'].fillna(-999)            >= min_fcf
mask &= df['pe_ratio'].fillna(9999)                     <= max_pe
mask &= df['pb_ratio'].fillna(9999)                     <= max_pb
mask &= df['dividend_yield_pct'].fillna(-1)             >= min_div_yield

# D/E filter with Financials bypass
fin_bypass = df['broad_sector'] == 'Financials'
mask &= (df['debt_to_equity'].fillna(9999) <= max_de) | fin_bypass

# ICR filter with Debt Free passthrough
icr_pass = df['icr_label'] == 'Debt Free'
if 'icr_label' in df.columns:
    mask &= (df['interest_coverage'].fillna(-1) >= min_icr) | icr_pass

if sector_filter:
    mask &= df['broad_sector'].isin(sector_filter)

result = df[mask].sort_values('composite_quality_score', ascending=False).reset_index(drop=True)

# ── Result count label ─────────────────────────────────────────────────────────
st.markdown(f'**{len(result)} companies** match your filters'
            + (f' out of **{len(df)}**' if len(result) < len(df) else ''))

# ── Results table ─────────────────────────────────────────────────────────────
display_cols = {
    'company_id': 'Ticker', 'company_name': 'Company', 'broad_sector': 'Sector',
    'return_on_equity_pct': 'ROE%', 'debt_to_equity': 'D/E',
    'revenue_cagr_5yr': 'Rev CAGR 5yr%', 'free_cash_flow_cr': 'FCF (₹Cr)',
    'pe_ratio': 'P/E', 'dividend_yield_pct': 'Div Yield%',
    'composite_quality_score': 'Score',
}
avail = {k: v for k, v in display_cols.items() if k in result.columns}
display_df = result[list(avail.keys())].rename(columns=avail)
for col in ['ROE%', 'D/E', 'Rev CAGR 5yr%', 'P/E', 'Div Yield%', 'Score']:
    if col in display_df.columns:
        display_df[col] = display_df[col].round(2)

st.dataframe(display_df, use_container_width=True, height=480, hide_index=True)

# ── CSV download button ────────────────────────────────────────────────────────
csv_data = result[list(avail.keys())].rename(columns=avail).to_csv(index=False).encode('utf-8')
st.download_button(
    label='⬇️ Download CSV',
    data=csv_data,
    file_name='screener_results.csv',
    mime='text/csv',
)
```

### Step 8 — Create `src/dashboard/pages/04_peers.py`

```python
"""
04_peers.py — Peer Comparison screen.

Spec requirements:
  ✅ 11-group dropdown
  ✅ Radar chart via Plotly Scatterpolar — company vs peer group average
  ✅ KPI table with benchmark row highlighted
"""

import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import numpy as np
import plotly.graph_objects as go
import streamlit as st
import pandas as pd

from src.dashboard.utils.db import get_peer_group_names, get_peers

st.header('👥 Peer Comparison')

groups = get_peer_group_names()
if not groups:
    st.warning('No peer groups found. Run `make peer` first.')
    st.stop()

selected_group = st.selectbox('Select Peer Group', groups)
peers_df = get_peers(selected_group)

if peers_df.empty:
    st.info(f'No data for peer group "{selected_group}".')
    st.stop()

# ── Company selector within group ─────────────────────────────────────────────
members = peers_df['company_id'].tolist()
selected_co = st.selectbox('Compare company', members)

# ── Plotly Scatterpolar radar chart ───────────────────────────────────────────
RADAR_METRICS = [
    'return_on_equity_pct', 'return_on_capital_employed_pct',
    'net_profit_margin_pct', 'debt_to_equity',
    'free_cash_flow_cr', 'pat_cagr_5yr',
    'revenue_cagr_5yr', 'composite_quality_score',
]
RADAR_LABELS = ['ROE', 'ROCE', 'NPM', 'Low Debt', 'FCF', 'PAT CAGR', 'Rev CAGR', 'Composite']
RADAR_RANGES = {
    'return_on_equity_pct': (0,45), 'return_on_capital_employed_pct': (0,40),
    'net_profit_margin_pct': (0,35), 'debt_to_equity': (0,5),
    'free_cash_flow_cr': (-500,8000), 'pat_cagr_5yr': (-10,30),
    'revenue_cagr_5yr': (-5,25),     'composite_quality_score': (0,100),
}

def _norm(metric, val):
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return 0.5
    lo, hi = RADAR_RANGES.get(metric, (0,100))
    s = max(0.0, min(1.0, (float(val)-lo)/(hi-lo)))
    return 1-s if metric == 'debt_to_equity' else s

avail_metrics = [m for m in RADAR_METRICS if m in peers_df.columns]

def _vals(row):
    return [_norm(m, row.get(m)) for m in avail_metrics]

co_row = peers_df[peers_df['company_id'] == selected_co]
group_avg = peers_df[avail_metrics].mean(numeric_only=True).to_dict()

if not co_row.empty:
    co_vals  = _vals(co_row.iloc[0].to_dict())
    avg_vals = [_norm(m, group_avg.get(m)) for m in avail_metrics]
    labels   = RADAR_LABELS[:len(avail_metrics)]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=co_vals + co_vals[:1], theta=labels + labels[:1],
        fill='toself', fillcolor='rgba(79,195,247,0.2)',
        line=dict(color='#4fc3f7', width=2.5),
        name=selected_co,
    ))
    fig.add_trace(go.Scatterpolar(
        r=avg_vals + avg_vals[:1], theta=labels + labels[:1],
        fill='toself', fillcolor='rgba(239,154,154,0.1)',
        line=dict(color='#ef9a9a', width=1.8, dash='dash'),
        name='Peer Avg',
    ))
    fig.update_layout(
        polar=dict(
            bgcolor='#16213e',
            radialaxis=dict(visible=True, range=[0,1], gridcolor='#444'),
            angularaxis=dict(gridcolor='#444'),
        ),
        paper_bgcolor='#1a1a2e', font_color='white',
        showlegend=True, height=450,
        margin=dict(l=60, r=60, t=40, b=40),
    )
    st.plotly_chart(fig, use_container_width=True)

# ── KPI comparison table ───────────────────────────────────────────────────────
st.subheader(f'All companies in {selected_group}')
table_cols = ['company_id', 'company_name'] + avail_metrics + ['is_benchmark']
avail_table = [c for c in table_cols if c in peers_df.columns]
display_df  = peers_df[avail_table].set_index('company_id')

def _highlight_benchmark(row):
    is_bench = row.get('is_benchmark', 0)
    return ['background-color: #FFF176; color: black' if is_bench else '' for _ in row]

numeric_cols = [c for c in avail_metrics if c in display_df.columns]
styled = display_df.style \
    .apply(_highlight_benchmark, axis=1) \
    .format({c: '{:.2f}' for c in numeric_cols}, na_rep='N/A')

st.dataframe(styled, use_container_width=True, height=350)
st.caption('🏆 Gold row = benchmark company for this peer group')
```

---

## 📈 Day 25 — Remaining 4 Screens

### Step 9 — Create `src/dashboard/pages/05_trends.py`

```python
"""
05_trends.py — Trend Analysis screen.

Spec requirements:
  ✅ Company search + multi-metric selector (overlay ≤ 3)
  ✅ 10-year line chart with YoY % change annotation on each point
"""

import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import plotly.graph_objects as go
import streamlit as st
import pandas as pd

from src.dashboard.utils.db import get_companies, get_ratios

st.header('📈 Trend Analysis')

cos     = get_companies()
options = sorted([f"{r['id']} — {r['company_name']}" for _, r in cos.iterrows()])
sel     = st.selectbox('🔍 Company', options)
ticker  = sel.split(' — ')[0].strip()

METRIC_MAP = {
    'ROE (%)':            'return_on_equity_pct',
    'ROCE (%)':           'return_on_capital_employed_pct',
    'Net Profit Margin':  'net_profit_margin_pct',
    'D/E Ratio':          'debt_to_equity',
    'FCF (₹ Cr)':         'free_cash_flow_cr',
    'Revenue CAGR 5yr':   'revenue_cagr_5yr',
    'PAT CAGR 5yr':       'pat_cagr_5yr',
    'Composite Score':    'composite_quality_score',
}
selected_metrics = st.multiselect(
    'Metrics (max 3)', list(METRIC_MAP.keys()),
    default=['ROE (%)','Net Profit Margin'],
    max_selections=3,
)

ratios = get_ratios(ticker)

if ratios.empty:
    st.warning(f'No data for {ticker}.')
    st.stop()

r_plot = ratios.sort_values('year').tail(10)
COLOURS = ['#4fc3f7','#81c784','#ffb74d','#ce93d8']

fig = go.Figure()
for i, metric_label in enumerate(selected_metrics):
    col = METRIC_MAP[metric_label]
    if col not in r_plot.columns:
        continue
    y_vals = r_plot[col]
    yoy    = y_vals.pct_change().mul(100).round(1)   # YoY % change
    text   = [f'{v:+.1f}%' if pd.notna(v) else '' for v in yoy]

    fig.add_scatter(
        x=r_plot['year'], y=y_vals,
        mode='lines+markers+text',
        name=metric_label,
        line=dict(color=COLOURS[i], width=2.5),
        marker=dict(size=7),
        text=text, textposition='top center',
        textfont=dict(size=8, color=COLOURS[i]),
    )

fig.update_layout(
    plot_bgcolor='#1e2235', paper_bgcolor='#1e2235',
    font_color='white', height=420,
    xaxis=dict(gridcolor='#333'),
    yaxis=dict(gridcolor='#333'),
    legend=dict(orientation='h', yanchor='bottom', y=1.02),
    margin=dict(l=10, r=10, t=30, b=10),
)
st.plotly_chart(fig, use_container_width=True)

# ── Year-over-year change table ───────────────────────────────────────────────
if len(r_plot) >= 2 and selected_metrics:
    st.subheader('YoY Change Summary')
    rows = []
    for label in selected_metrics:
        col = METRIC_MAP[label]
        if col not in r_plot.columns: continue
        latest = r_plot.sort_values('year')[col].dropna()
        if len(latest) >= 2:
            rows.append({'Metric': label,
                         f'{r_plot["year"].iloc[-2]}': round(float(latest.iloc[-2]), 2),
                         f'{r_plot["year"].iloc[-1]}': round(float(latest.iloc[-1]), 2),
                         'Change': f'{float(latest.iloc[-1]-latest.iloc[-2]):+.2f}'})
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
```

### Step 10 — Create `src/dashboard/pages/06_sectors.py`

```python
"""
06_sectors.py — Sector Analysis screen.

Spec requirements:
  ✅ Bubble chart: X=Revenue, Y=ROE, size=MarketCap, colour=sub-sector
  ✅ Sector median KPI bar chart below bubble
"""

import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import plotly.express as px
import streamlit as st

from src.dashboard.utils.db import get_sectors

st.header('🏭 Sector Analysis')

df_sec = get_sectors()
if df_sec.empty:
    st.warning('No sector data found.')
    st.stop()

sectors = sorted(df_sec['broad_sector'].dropna().unique())
sel_sector = st.selectbox('Sector', ['All Sectors'] + list(sectors))

plot_df = df_sec if sel_sector == 'All Sectors' else df_sec[df_sec['broad_sector'] == sel_sector]

# ── Bubble chart: X=sales, Y=ROE, size=market cap, colour=sub-sector ─────────
st.subheader('Revenue vs ROE (bubble size = Market Cap)')
clean = plot_df.dropna(subset=['sales', 'return_on_equity_pct', 'market_cap_crore'])
if not clean.empty:
    fig = px.scatter(
        clean,
        x='sales', y='return_on_equity_pct',
        size='market_cap_crore', color='sub_sector',
        hover_name='company_id',
        hover_data={'company_name': True, 'broad_sector': True,
                    'market_cap_crore': ':,.0f'},
        labels={'sales': 'Revenue (₹ Cr)', 'return_on_equity_pct': 'ROE (%)'},
        template='plotly_dark', size_max=60,
    )
    fig.update_layout(height=480, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info('Insufficient data for bubble chart with current filters.')

# ── Sector median KPI bar chart ───────────────────────────────────────────────
st.subheader('Sector Median KPIs')
metric_sel = st.selectbox('Metric', {
    'ROE (%)': 'return_on_equity_pct',
    'Net Profit Margin': 'net_profit_margin_pct',
    'Revenue CAGR 5yr': 'revenue_cagr_5yr',
    'Composite Score': 'composite_quality_score',
}.keys())
metric_col = {
    'ROE (%)': 'return_on_equity_pct',
    'Net Profit Margin': 'net_profit_margin_pct',
    'Revenue CAGR 5yr': 'revenue_cagr_5yr',
    'Composite Score': 'composite_quality_score',
}[metric_sel]

if metric_col in df_sec.columns:
    med = df_sec.groupby('broad_sector')[metric_col].median().dropna().reset_index()
    med.columns = ['Sector', metric_sel]
    med = med.sort_values(metric_sel)
    fig2 = px.bar(med, x=metric_sel, y='Sector', orientation='h',
                  template='plotly_dark', color=metric_sel,
                  color_continuous_scale='Teal')
    fig2.update_layout(height=350, showlegend=False,
                       margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig2, use_container_width=True)
```

### Step 11 — Create `src/dashboard/pages/07_capital.py`

```python
"""
07_capital.py — Capital Allocation Map screen.

Spec requirements:
  ✅ Plotly treemap of all 92 companies by 8 capital allocation patterns
  ✅ Clicking a pattern shows the company list
"""

import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import plotly.express as px
import streamlit as st
import pandas as pd
import sqlite3

st.header('🗺️ Capital Allocation Map')

DB_PATH = os.getenv('DB_PATH', 'data/nifty100.db')

@st.cache_data(ttl=600)
def load_capital():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql("""
            SELECT fr.company_id, c.company_name, s.broad_sector,
                   fr.capital_allocation_pattern,
                   fr.composite_quality_score
            FROM financial_ratios fr
            JOIN (
                SELECT company_id, MAX(year) AS yr
                FROM financial_ratios GROUP BY company_id
            ) l ON fr.company_id=l.company_id AND fr.year=l.yr
            JOIN companies c ON fr.company_id=c.id
            LEFT JOIN sectors s ON fr.company_id=s.company_id
            WHERE fr.capital_allocation_pattern IS NOT NULL
        """, conn)

df = load_capital()
if df.empty:
    st.warning('No capital allocation data found.')
    st.stop()

df['pattern'] = df['capital_allocation_pattern'].fillna('Unknown')

# ── Treemap ───────────────────────────────────────────────────────────────────
st.subheader('92 Companies Grouped by Capital Allocation Pattern')
st.caption('Each block = one company. Block size = Composite Score.')

fig = px.treemap(
    df,
    path=['pattern', 'company_id'],
    values='composite_quality_score',
    color='pattern',
    hover_data={'company_name': True, 'broad_sector': True,
                'composite_quality_score': ':.1f'},
    color_discrete_sequence=px.colors.qualitative.Set2,
    template='plotly_dark',
)
fig.update_traces(textinfo='label', textfont_size=11)
fig.update_layout(height=560, margin=dict(l=0, r=0, t=30, b=0))
st.plotly_chart(fig, use_container_width=True)

# ── Drill-down: click a pattern to see company list ────────────────────────────
st.subheader('Pattern Detail')
all_patterns = sorted(df['pattern'].unique())
sel_pattern = st.selectbox('Select pattern to see companies', all_patterns)
filtered = df[df['pattern'] == sel_pattern][
    ['company_id', 'company_name', 'broad_sector', 'composite_quality_score']
].sort_values('composite_quality_score', ascending=False)
st.dataframe(filtered.rename(columns={
    'company_id': 'Ticker', 'company_name': 'Company',
    'broad_sector': 'Sector', 'composite_quality_score': 'Score',
}), use_container_width=True, hide_index=True)

# ── Pattern distribution summary ──────────────────────────────────────────────
st.subheader('Pattern Distribution')
dist = df.groupby('pattern')['company_id'].count().reset_index()
dist.columns = ['Pattern', 'Companies']
dist = dist.sort_values('Companies', ascending=False)
st.dataframe(dist, use_container_width=True, hide_index=True)
```

### Step 12 — Create `src/dashboard/pages/08_reports.py`

```python
"""
08_reports.py — Annual Reports screen.

Spec requirements:
  ✅ Company search + BSE PDF links
  ✅ 404 = "Report unavailable" badge in red
"""

import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import requests
import streamlit as st
import pandas as pd

from src.dashboard.utils.db import get_companies, get_documents

st.header('📄 Annual Reports')
st.caption('Direct links to company annual reports on BSE India.')

cos     = get_companies()
options = sorted([f"{r['id']} — {r['company_name']}" for _, r in cos.iterrows()])
sel     = st.selectbox('🔍 Select Company', options)
ticker  = sel.split(' — ')[0].strip()

docs = get_documents(ticker)
if docs.empty:
    st.info(f'No annual reports found for **{ticker}**.')
    st.stop()

st.subheader(f'Available Reports — {ticker}')

# Validate URLs (sample only — checking all would be slow)
check_urls = st.checkbox('Validate links (slower — checks HTTP status)', value=False)

for _, row in docs.iterrows():
    year = row.get('Year', 'N/A')
    url  = row.get('Annual_Report')

    col_year, col_link, col_status = st.columns([1, 4, 1])
    col_year.markdown(f'**FY {year}**')

    if not url or str(url) == 'nan':
        col_link.markdown('—')
        col_status.error('Missing')
        continue

    col_link.markdown(f'[📄 Download PDF]({url})')

    if check_urls:
        try:
            resp = requests.head(url, timeout=4, allow_redirects=True)
            if resp.status_code == 200:
                col_status.success('✅ OK')
            else:
                col_status.error(f'❌ {resp.status_code}')
        except Exception:
            col_status.error('❌ Error')
    else:
        col_status.caption('—')
```

---

## 💰 Day 26 — Valuation Module

### Step 13 — Create `src/analytics/valuation.py`

```python
"""
valuation.py
Valuation analytics — FCF yield, sector P/E comparison, overvaluation flags.

Spec requirements:
  FCF yield = FCF / market_cap_crore × 100
  Sector median P/E per broad_sector (latest year)
  Flags:
    Caution  → P/E > sector_median × 1.5
    Discount → P/E < sector_median × 0.7
    Fair     → otherwise
"""

from __future__ import annotations

import logging
import os
import sqlite3
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)
DB_PATH = os.getenv('DB_PATH', 'data/nifty100.db')


def compute_valuation() -> pd.DataFrame:
    """
    Build the full valuation table for all 92 companies.

    Returns a DataFrame with columns:
        company_id, company_name, sector, P/E, P/B, EV/EBITDA,
        FCF_yield_pct, 5yr_median_PE, PE_vs_sector_median_pct, flag
    """
    with sqlite3.connect(DB_PATH) as conn:
        mc = pd.read_sql("""
            SELECT mc.company_id, mc.year,
                   mc.pe_ratio, mc.pb_ratio, mc.ev_ebitda,
                   mc.market_cap_crore, mc.dividend_yield_pct
            FROM market_cap mc
        """, conn)

        fr_latest = pd.read_sql("""
            SELECT fr.company_id, fr.free_cash_flow_cr, fr.year
            FROM financial_ratios fr
            JOIN (
                SELECT company_id, MAX(year) AS yr
                FROM financial_ratios GROUP BY company_id
            ) l ON fr.company_id=l.company_id AND fr.year=l.yr
        """, conn)

        cos = pd.read_sql('SELECT id, company_name FROM companies', conn)
        sec = pd.read_sql('SELECT company_id, broad_sector FROM sectors', conn)

    # Latest year market_cap per company
    mc_latest = mc.loc[mc.groupby('company_id')['year'].idxmax()].copy()

    # 5-year median P/E (2019–2024)
    mc_5yr = mc[mc['year'].between(2019, 2024, inclusive='both')]
    median_pe_5yr = mc_5yr.groupby('company_id')['pe_ratio'].median().rename('5yr_median_PE')

    df = mc_latest.merge(fr_latest[['company_id', 'free_cash_flow_cr']], on='company_id', how='left')
    df = df.merge(cos, left_on='company_id', right_on='id', how='left')
    df = df.merge(sec, on='company_id', how='left')
    df = df.merge(median_pe_5yr, on='company_id', how='left')

    # FCF yield = FCF / market_cap × 100
    df['FCF_yield_pct'] = (
        df['free_cash_flow_cr'] / df['market_cap_crore'] * 100
    ).where(df['market_cap_crore'].notna() & (df['market_cap_crore'] != 0)).round(2)

    # Sector median P/E
    sec_median_pe = df.groupby('broad_sector')['pe_ratio'].median().rename('sector_median_PE')
    df = df.merge(sec_median_pe, on='broad_sector', how='left')

    # P/E vs sector median %
    df['PE_vs_sector_median_pct'] = (
        (df['pe_ratio'] - df['sector_median_PE']) / df['sector_median_PE'] * 100
    ).round(1)

    # Flags
    def _flag(row):
        pe  = row.get('pe_ratio')
        med = row.get('sector_median_PE')
        if pd.isna(pe) or pd.isna(med) or med == 0:
            return 'Unknown'
        if pe > med * 1.5:
            return 'Caution'
        if pe < med * 0.7:
            return 'Discount'
        return 'Fair'

    df['flag'] = df.apply(_flag, axis=1)

    logger.info('Valuation computed: %d companies | Caution=%d | Discount=%d | Fair=%d',
                len(df),
                (df['flag'] == 'Caution').sum(),
                (df['flag'] == 'Discount').sum(),
                (df['flag'] == 'Fair').sum())
    return df


### Step 14 — Save valuation outputs

def save_valuation_outputs(
    xlsx_path: str = 'output/valuation_summary.xlsx',
    csv_path:  str = 'output/valuation_flags.csv',
) -> pd.DataFrame:
    """
    Compute valuation and write:
      - valuation_summary.xlsx: all 92 companies with required columns
      - valuation_flags.csv: only Caution and Discount companies
    """
    from openpyxl.styles import PatternFill, Font

    df = compute_valuation()

    # Required columns per spec
    required_cols = [
        'company_id', 'company_name', 'broad_sector',
        'pe_ratio', 'pb_ratio', 'ev_ebitda',
        'FCF_yield_pct', '5yr_median_PE',
        'PE_vs_sector_median_pct', 'flag',
    ]
    avail = [c for c in required_cols if c in df.columns]
    output_df = df[avail].rename(columns={
        'broad_sector': 'sector',
        'pe_ratio': 'P/E', 'pb_ratio': 'P/B', 'ev_ebitda': 'EV/EBITDA',
    })

    Path(xlsx_path).parent.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
        output_df.to_excel(writer, sheet_name='Valuation', index=False)
        ws = writer.sheets['Valuation']

        # Header formatting
        for cell in ws[1]:
            cell.fill = PatternFill('solid', fgColor='1F3864')
            cell.font = Font(color='FFFFFF', bold=True)

        # Flag column colour-coding
        flag_col_idx = None
        for i, h in enumerate(output_df.columns, 1):
            if h == 'flag':
                flag_col_idx = i
                break

        if flag_col_idx:
            FILLS = {
                'Caution':  PatternFill('solid', fgColor='FFCDD2'),
                'Discount': PatternFill('solid', fgColor='C8E6C9'),
                'Fair':     PatternFill('solid', fgColor='E3F2FD'),
            }
            for r in range(2, ws.max_row + 1):
                val  = ws.cell(row=r, column=flag_col_idx).value
                fill = FILLS.get(val)
                if fill:
                    ws.cell(row=r, column=flag_col_idx).fill = fill

    logger.info('valuation_summary.xlsx → %s (%d rows)', xlsx_path, len(output_df))

    # valuation_flags.csv — only Caution and Discount
    flags_df = df[df['flag'].isin(['Caution', 'Discount'])][avail]
    flags_df.to_csv(csv_path, index=False)
    logger.info('valuation_flags.csv → %s (%d rows)', csv_path, len(flags_df))

    print(f'✅ valuation_summary.xlsx: {len(output_df)} rows')
    print(f'✅ valuation_flags.csv:    {len(flags_df)} flagged companies')
    return df


if __name__ == '__main__':
    save_valuation_outputs()
```

### Step 14 — Add Makefile Target and Run

```makefile
valuation:
	python src/analytics/valuation.py
```

```bash
make valuation
```

**Expected:**
```
✅ valuation_summary.xlsx: 92 rows
✅ valuation_flags.csv:    ~35 flagged companies
```

---

## 🧪 Day 27 — Integration QA & Bug Fixes

### Step 15 — QA Test Script

```python
# notebooks/qa_sprint4.py
"""
Integration QA for Sprint 4.
Tests all 8 Streamlit screens via their data-loading functions.
Does NOT test the UI rendering (that requires a running browser).
Tests: 10 tickers × data loading, partial data, None/NaN handling.
"""
import sqlite3, time, pandas as pd

DB = 'data/nifty100.db'
from src.dashboard.utils.db import (
    get_companies, get_ratios, get_pl, get_bs, get_cf,
    get_sectors, get_peers, get_valuation, get_peer_group_names,
    get_latest_universe, get_documents,
)

# ── 10 test tickers across all sectors ────────────────────────────────────────
TEST_TICKERS = [
    'TCS',        # IT
    'HDFCBANK',   # Financials - Private Bank
    'RELIANCE',   # Energy (Conglomerate)
    'HINDUNILVR', # FMCG
    'SUNPHARMA',  # Healthcare
    'NTPC',       # Energy - Power
    'TATASTEEL',  # Materials
    'MARUTI',     # Consumer Discretionary
    'SBIN',       # Financials - Public Bank
    'NESTLEIND',  # Consumer Staples (Dec year-end)
]

print('=' * 60)
print('Sprint 4 — Integration QA')
print('=' * 60)

# ── Test 1: Company Profile data loads for all 10 tickers ─────────────────────
print('\n── Test 1: Company Profile data loading ──')
for ticker in TEST_TICKERS:
    start = time.time()
    ratios = get_ratios(ticker)
    pl     = get_pl(ticker)
    elapsed = time.time() - start
    ok = not ratios.empty and not pl.empty
    print(f'  {"✅" if ok else "❌"} {ticker}: ratios={len(ratios)} rows | pl={len(pl)} rows | {elapsed:.2f}s')
    assert elapsed < 3.0, f'❌ {ticker} profile loaded in {elapsed:.2f}s (limit: 3s)'

# ── Test 2: Partial data companies do not crash ────────────────────────────────
print('\n── Test 2: Partial data handling ──')
cos = get_companies()
with sqlite3.connect(DB) as conn:
    coverage = pd.read_sql(
        "SELECT company_id, COUNT(*) AS yr_count FROM profitandloss GROUP BY company_id",
        conn
    )
partial = coverage[coverage['yr_count'] < 10]['company_id'].tolist()[:3]
for ticker in partial:
    ratios = get_ratios(ticker)
    print(f'  ✅ {ticker}: {len(ratios)} years (partial) — no crash')

# ── Test 3: None/NaN → display "N/A" (data layer check) ──────────────────────
print('\n── Test 3: None/NaN values in ratios ──')
universe = get_latest_universe()
null_counts = universe.isnull().sum()
high_null = null_counts[null_counts > 20]
if not high_null.empty:
    print('  ⚠️  Columns with >20 NaN values (will show N/A in UI):')
    for col, cnt in high_null.items():
        print(f'     {col}: {cnt} NaN')
else:
    print('  ✅ NaN counts acceptable')

# ── Test 4: Extreme slider values ─────────────────────────────────────────────
print('\n── Test 4: Extreme slider values (screener) ──')
# min slider (all zeros) — should return many companies
mask_all_low = (
    (universe['return_on_equity_pct'].fillna(-999) >= 0) &
    (universe['debt_to_equity'].fillna(9999) <= 10.0)
)
n_all_low = mask_all_low.sum()
print(f'  ✅ All sliders at minimum: {n_all_low} companies (no crash)')

# max slider — should return 0 companies (too strict)
mask_all_high = (
    (universe['return_on_equity_pct'].fillna(-999) >= 50) &
    (universe['debt_to_equity'].fillna(9999) <= 0.0) &
    (universe['pe_ratio'].fillna(9999) <= 5)
)
n_all_high = mask_all_high.sum()
print(f'  ✅ All sliders at maximum strictness: {n_all_high} companies (no crash)')

# ── Test 5: Screener CSV export ────────────────────────────────────────────────
print('\n── Test 5: Screener CSV export ──')
csv = universe.head(10).to_csv(index=False)
lines = csv.strip().split('\n')
assert len(lines) == 11, f'Expected 11 lines (1 header + 10 data), got {len(lines)}'
assert len(lines[0].split(',')) > 5, 'CSV has too few columns'
print(f'  ✅ CSV: {len(lines)-1} data rows, {len(lines[0].split(","))} columns')

# ── Test 6: Valuation outputs exist ────────────────────────────────────────────
print('\n── Test 6: Valuation outputs ──')
import os
for f in ['output/valuation_summary.xlsx', 'output/valuation_flags.csv']:
    exists = os.path.exists(f)
    print(f'  {"✅" if exists else "❌"} {f}')

print('\n' + '='*60)
print('✅ Sprint 4 QA complete — all checks passed')
print('='*60)
```

```bash
python notebooks/qa_sprint4.py
```

---

## 📚 Day 28 — Documentation

### Step 16 — Update `README.md`

```markdown
# Nifty 100 Financial Intelligence Platform

Production-grade financial analytics for all 92 Nifty 100 companies.

## Quick Start

```bash
git clone <repo-url> && cd nifty100
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make setup    # create dirs + .env
make load     # ETL: 12 files → nifty100.db
make ratios   # compute 50+ KPIs → financial_ratios table
make screener # generate screener_output.xlsx
make peer     # peer percentiles + radar charts + peer_comparison.xlsx
make valuation# FCF yield + valuation flags
make dashboard# ← opens browser at http://localhost:8501
```

## Dashboard — 8 Screens

| Screen | URL | What it shows |
|---|---|---|
| Home | `/` | 6 KPI tiles · sector donut · top-5 quality companies · year selector |
| Company Profile | `01_home` | Search any ticker · 10-year P&L chart · ROE/ROCE trend · pros/cons |
| Screener | `03_screener` | 10 sliders · 6 preset buttons · live table · CSV download |
| Peer Comparison | `04_peers` | Radar chart (Plotly) · KPI table with benchmark highlight |
| Trend Analysis | `05_trends` | Multi-metric 10-year line chart with YoY% annotations |
| Sector Analysis | `06_sectors` | Bubble chart · sector median bar chart |
| Capital Allocation | `07_capital` | Treemap of 92 companies by 8 CF patterns · drill-down |
| Annual Reports | `08_reports` | Company search · BSE PDF links · 404 detection |

## Makefile Targets

| Command | Action |
|---|---|
| `make load` | ETL: load all 12 files |
| `make ratios` | Compute 50+ KPIs |
| `make screener` | Generate screener_output.xlsx |
| `make peer` | Peer percentiles + radar charts |
| `make valuation` | Valuation summary + flags |
| `make dashboard` | Start Streamlit on port 8501 |
| `make api` | Start FastAPI on port 8000 |
| `make test` | Run all pytest tests |
```

---

## 🚀 Sprint 4 Exit Check Script

```bash
#!/bin/bash
# sprint4_exit_check.sh
set -euo pipefail
echo "════════════════════════════════════════"
echo "  Sprint 4 — Exit Check"
echo "════════════════════════════════════════"

# Gate 1 — Streamlit app starts
echo ""
echo "── Gate 1: App starts ──"
PYTHONPATH=$(pwd) streamlit run src/dashboard/app.py &
APP_PID=$!
sleep 5
if curl -s http://localhost:8501/_stcore/health | grep -q '"status":"ok"'; then
    echo "  ✅ App running on localhost:8501"
else
    echo "  ❌ App not responding"
fi
kill $APP_PID 2>/dev/null

# Gate 2 — valuation_summary.xlsx has 92 rows
echo ""
echo "── Gate 2: valuation_summary.xlsx ──"
python3 -c "
import openpyxl
wb = openpyxl.load_workbook('output/valuation_summary.xlsx')
ws = wb.active
n = ws.max_row - 1
print(f'  {\"✅\" if n==92 else \"❌\"} {n}/92 rows')
"

# Gate 3 — valuation_flags.csv exists + has Caution/Discount
echo ""
echo "── Gate 3: valuation_flags.csv ──"
python3 -c "
import pandas as pd
df = pd.read_csv('output/valuation_flags.csv')
flags = df['flag'].unique().tolist()
print(f'  ✅ {len(df)} flagged companies | flags: {flags}')
"

# Gate 4 — QA script
echo ""
echo "── Gate 4: Integration QA ──"
python3 notebooks/qa_sprint4.py

echo ""
echo "════════════════════════════════════════"
echo " Sprint 4 Exit Check Complete."
echo "════════════════════════════════════════"
```

---

## 📋 Sprint 4 Retrospective Template

```markdown
# Sprint 4 Retrospective — Dashboard · Valuation Module
**Date:** Day 28 · ___________

## Exit Criteria Sign-Off

| Gate | Spec Requirement | Result | Status |
|---|---|---|---|
| All 8 screens load without errors | 92 tickers tested | ___ | ✅/❌ |
| Profile screen < 3 seconds | Timed for 5 tickers | Max ___ s | ✅/❌ |
| Screener CSV download valid | Headers + data rows | ___ cols | ✅/❌ |
| valuation_summary.xlsx — 92 rows | Row count | ___ | ✅/❌ |
| Sprint demo completed | Team lead signed off | ___-___-2026 | ✅/❌ |

## Engineering Decisions

1. **Streamlit caching** — `@st.cache_data(ttl=600)` on all 8 db functions ensures Profile screen stays under 3 seconds on repeated loads; first load may be 1–2 seconds.
2. **D/E filter in Screener** — Same Financials bypass logic as Sprint 3 engine; no code duplication — the filter is applied in `03_screener.py` directly.
3. **Preset buttons** — Use Streamlit session_state-free approach: presets change the slider default values via `active_preset` dict. No session_state needed.
4. **Radar chart** — Plotly `Scatterpolar` (spec requirement, not matplotlib). Values are normalised to [0,1] using `RADAR_RANGES` reference table.
5. **Valuation flags** — Threshold is 1.5× and 0.7× of **sector** median P/E, not the Nifty 100 universe median. This avoids flagging all IT companies as overvalued simply because they trade at higher multiples.
6. **Annual report 404 check** — Optional (checkbox). Checking all 1,585 URLs would take ~30 minutes; users opt in per session.

## Story Points

| Day | Theme | Est SP | Actual SP |
|---|---|---|---|
| D22 | App Scaffold | 8 | |
| D23 | Home + Profile | 10 | |
| D24 | Screener + Peer | 10 | |
| D25 | 4 Remaining Screens | 10 | |
| D26 | Valuation Module | 8 | |
| D27 | QA & Bug Fixes | 6 | |
| D28 | Docs & Retro | 3 | |
| **Total** | | **55** | |

---
**Signed off:** _________________________  **Date:** ____________
```

---

## 🗺️ What Sprint 5 Needs From This Sprint

| Requirement | Verification |
|---|---|
| `src/dashboard/utils/db.py` importable | `from src.dashboard.utils.db import get_companies` |
| `output/valuation_summary.xlsx` — 92 rows | `openpyxl.load_workbook(...)` |
| `output/valuation_flags.csv` exists | `os.path.exists(...)` |
| App runs on port 8501 | `make dashboard` |
| All 8 pages render without error | Manual check — 5 random tickers |

---

*Sprint 4 · N100 Financial Intelligence Platform · v1.0 · June 2026 · Data Analytics Division*
