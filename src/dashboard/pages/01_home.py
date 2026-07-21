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
