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
