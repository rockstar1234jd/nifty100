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
