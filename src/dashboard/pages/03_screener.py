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

st.header('🔎 Stock Screener')

# ── Load latest universe ──────────────────────────────────────────────────────
df = get_latest_universe()

if df.empty:
    st.warning('No data available for screening.')
    st.stop()

# ── Preset configurations ─────────────────────────────────────────────────────
PRESETS = {
    'Quality Leaders': {
        'roe_min': 15.0, 'roce_min': 15.0, 'npm_min': 10.0,
        'current_ratio_min': 1.0, 'de_max': 1.0, 'icr_min': 5.0,
        'rev_cagr_min': 10.0, 'fcf_min': 0.0, 'pe_max': 50.0, 'mcap_min': 1000.0
    },
    'Value Buys': {
        'roe_min': 10.0, 'roce_min': 10.0, 'npm_min': 5.0,
        'current_ratio_min': 1.0, 'de_max': 2.0, 'icr_min': 3.0,
        'rev_cagr_min': 5.0, 'fcf_min': 0.0, 'pe_max': 15.0, 'mcap_min': 500.0
    },
    'Growth Stars': {
        'roe_min': 12.0, 'roce_min': 12.0, 'npm_min': 8.0,
        'current_ratio_min': 1.0, 'de_max': 1.5, 'icr_min': 4.0,
        'rev_cagr_min': 15.0, 'fcf_min': 0.0, 'pe_max': 100.0, 'mcap_min': 2000.0
    },
    'Dividend Kings': {
        'roe_min': 10.0, 'roce_min': 10.0, 'npm_min': 5.0,
        'current_ratio_min': 1.0, 'de_max': 1.0, 'icr_min': 5.0,
        'rev_cagr_min': 5.0, 'fcf_min': 100.0, 'pe_max': 50.0, 'mcap_min': 1000.0
    },
    'Debt-Free': {
        'roe_min': 10.0, 'roce_min': 10.0, 'npm_min': 5.0,
        'current_ratio_min': 1.0, 'de_max': 0.0, 'icr_min': 0.0,
        'rev_cagr_min': 5.0, 'fcf_min': 0.0, 'pe_max': 50.0, 'mcap_min': 500.0
    },
    'High ROE': {
        'roe_min': 20.0, 'roce_min': 18.0, 'npm_min': 10.0,
        'current_ratio_min': 1.0, 'de_max': 2.0, 'icr_min': 5.0,
        'rev_cagr_min': 8.0, 'fcf_min': 0.0, 'pe_max': 100.0, 'mcap_min': 1000.0
    },
}

# ── Sidebar: Preset buttons ───────────────────────────────────────────────────
st.sidebar.subheader('📋 Presets')
selected_preset = None
cols = st.sidebar.columns(2)
for idx, preset_name in enumerate(PRESETS.keys()):
    col = cols[idx % 2]
    if col.button(preset_name, use_container_width=True):
        selected_preset = preset_name

# ── Sidebar: 10 metric sliders ────────────────────────────────────────────────
st.sidebar.subheader('🎚️ Filters')

# Initialize with default values or preset values
if selected_preset:
    preset_vals = PRESETS[selected_preset]
else:
    preset_vals = {
        'roe_min': 0.0, 'roce_min': 0.0, 'npm_min': 0.0,
        'current_ratio_min': 0.0, 'de_max': 10.0, 'icr_min': 0.0,
        'rev_cagr_min': -50.0, 'fcf_min': -1000.0, 'pe_max': 200.0, 'mcap_min': 0.0
    }

roe_min = st.sidebar.slider('ROE (%) ≥', -50.0, 100.0, preset_vals.get('roe_min', 0.0), 1.0)
roce_min = st.sidebar.slider('ROCE (%) ≥', -50.0, 100.0, preset_vals.get('roce_min', 0.0), 1.0)
npm_min = st.sidebar.slider('Net Profit Margin (%) ≥', -50.0, 100.0, preset_vals.get('npm_min', 0.0), 1.0)
current_ratio_min = st.sidebar.slider('Current Ratio ≥', 0.0, 10.0, preset_vals.get('current_ratio_min', 0.0), 0.1)
de_max = st.sidebar.slider('Debt/Equity ≤', 0.0, 10.0, preset_vals.get('de_max', 10.0), 0.1)
icr_min = st.sidebar.slider('Interest Coverage ≥', 0.0, 50.0, preset_vals.get('icr_min', 0.0), 1.0)
rev_cagr_min = st.sidebar.slider('Revenue CAGR 5yr (%) ≥', -50.0, 100.0, preset_vals.get('rev_cagr_min', -50.0), 1.0)
fcf_min = st.sidebar.slider('Free Cash Flow (Cr) ≥', -1000.0, 10000.0, preset_vals.get('fcf_min', -1000.0), 100.0)
pe_max = st.sidebar.slider('P/E Ratio ≤', 0.0, 200.0, preset_vals.get('pe_max', 200.0), 5.0)
mcap_min = st.sidebar.slider('Market Cap (Cr) ≥', 0.0, 100000.0, preset_vals.get('mcap_min', 0.0), 500.0)

# ── Apply filters ─────────────────────────────────────────────────────────────
filtered = df.copy()

# Apply each filter
filtered = filtered[
    (filtered['return_on_equity_pct'].fillna(-999) >= roe_min) &
    (filtered['return_on_capital_employed_pct'].fillna(-999) >= roce_min) &
    (filtered['net_profit_margin_pct'].fillna(-999) >= npm_min) &
    (filtered['current_ratio'].fillna(0) >= current_ratio_min) &
    (filtered['debt_to_equity'].fillna(999) <= de_max) &
    (filtered['interest_coverage'].fillna(0) >= icr_min) &
    (filtered['revenue_cagr_5yr'].fillna(-999) >= rev_cagr_min) &
    (filtered['free_cash_flow_cr'].fillna(-999) >= fcf_min) &
    (filtered['pe_ratio'].fillna(999) <= pe_max) &
    (filtered['market_cap_crore'].fillna(0) >= mcap_min)
]

# ── Sort by composite quality score ───────────────────────────────────────────
filtered = filtered.sort_values('composite_quality_score', ascending=False)

# ── Display results ───────────────────────────────────────────────────────────
st.subheader(f'📊 Results: {len(filtered)} companies')

if filtered.empty:
    st.info('No companies match the current filters. Try adjusting the criteria.')
else:
    # Select display columns
    display_cols = [
        'company_id', 'company_name', 'broad_sector',
        'return_on_equity_pct', 'return_on_capital_employed_pct', 'net_profit_margin_pct',
        'debt_to_equity', 'current_ratio', 'interest_coverage',
        'revenue_cagr_5yr', 'free_cash_flow_cr',
        'pe_ratio', 'market_cap_crore', 'composite_quality_score'
    ]
    
    # Filter columns that exist
    display_cols = [c for c in display_cols if c in filtered.columns]
    display_df = filtered[display_cols].copy()
    
    # Rename for display
    display_df = display_df.rename(columns={
        'company_id': 'Ticker',
        'company_name': 'Company',
        'broad_sector': 'Sector',
        'return_on_equity_pct': 'ROE%',
        'return_on_capital_employed_pct': 'ROCE%',
        'net_profit_margin_pct': 'NPM%',
        'debt_to_equity': 'D/E',
        'current_ratio': 'Current Ratio',
        'interest_coverage': 'ICR',
        'revenue_cagr_5yr': 'Rev CAGR 5yr%',
        'free_cash_flow_cr': 'FCF (Cr)',
        'pe_ratio': 'P/E',
        'market_cap_crore': 'Market Cap (Cr)',
        'composite_quality_score': 'Quality Score'
    })
    
    # Round numeric columns
    numeric_cols = ['ROE%', 'ROCE%', 'NPM%', 'D/E', 'Current Ratio', 'ICR', 'Rev CAGR 5yr%', 'FCF (Cr)', 'P/E', 'Market Cap (Cr)', 'Quality Score']
    for col in numeric_cols:
        if col in display_df.columns:
            display_df[col] = display_df[col].round(2)
    
    st.dataframe(display_df, use_container_width=True, hide_index=True, height=400)
    
    # ── CSV Download ──────────────────────────────────────────────────────────
    csv = display_df.to_csv(index=False)
    st.download_button(
        label='📥 Download Results as CSV',
        data=csv,
        file_name='screener_results.csv',
        mime='text/csv',
    )
