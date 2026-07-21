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
