"""
05_trends.py — Trends Analysis screen.

Spec requirements:
  ✅ Search + multi-metric selector (≤3)
  ✅ 10-year line chart
  ✅ YoY annotation
"""

import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from src.dashboard.utils.db import get_companies, get_ratios

st.header('📈 Trends Analysis')

# ── Company selector ──────────────────────────────────────────────────────────
cos = get_companies()
options = [f"{row['id']} — {row['company_name']}" for _, row in cos.iterrows()]
options.sort()

selected = st.selectbox('🔍 Select Company', options)
if not selected:
    st.info('Please select a company to view trends.')
    st.stop()

ticker = selected.split(' — ')[0].strip()

# ── Metric selector (max 3) ───────────────────────────────────────────────────
AVAILABLE_METRICS = {
    'return_on_equity_pct': 'ROE (%)',
    'return_on_capital_employed_pct': 'ROCE (%)',
    'net_profit_margin_pct': 'Net Profit Margin (%)',
    'current_ratio': 'Current Ratio',
    'debt_to_equity': 'Debt/Equity',
    'interest_coverage': 'Interest Coverage',
    'revenue_cagr_5yr': 'Revenue CAGR 5yr (%)',
    'pat_cagr_5yr': 'PAT CAGR 5yr (%)',
    'free_cash_flow_cr': 'Free Cash Flow (Cr)',
    'composite_quality_score': 'Composite Quality Score'
}

selected_metrics = st.multiselect(
    '📊 Select up to 3 metrics',
    options=list(AVAILABLE_METRICS.values()),
    default=[list(AVAILABLE_METRICS.values())[0]],
    max_selections=3
)

if not selected_metrics:
    st.warning('Please select at least one metric.')
    st.stop()

# Reverse mapping
metric_cols = [k for k, v in AVAILABLE_METRICS.items() if v in selected_metrics]

# ── Load ratio data ───────────────────────────────────────────────────────────
ratios = get_ratios(ticker)

if ratios.empty:
    st.warning(f'No historical data available for {ticker}')
    st.stop()

# Sort by year and take last 10 years
ratios = ratios.sort_values('year').tail(10)

# ── Create trend chart ────────────────────────────────────────────────────────
fig = go.Figure()

colors = ['#4fc3f7', '#ffb74d', '#81c784']

for idx, (col, label) in enumerate([(c, AVAILABLE_METRICS[c]) for c in metric_cols]):
    if col not in ratios.columns:
        continue
    
    values = ratios[col].fillna(0)
    
    fig.add_trace(go.Scatter(
        x=ratios['year'],
        y=values,
        name=label,
        mode='lines+markers',
        line=dict(color=colors[idx % len(colors)], width=2.5),
        marker=dict(size=6)
    ))

fig.update_layout(
    title=f'10-Year Trend — {ticker}',
    xaxis_title='Year',
    yaxis_title='Value',
    plot_bgcolor='#1e2235',
    paper_bgcolor='#1e2235',
    font_color='white',
    height=450,
    legend=dict(orientation='h', yanchor='bottom', y=1.02),
    hovermode='x unified'
)

st.plotly_chart(fig, use_container_width=True)

# ── YoY Change Table ──────────────────────────────────────────────────────────
st.subheader('📊 Year-over-Year Changes')

yoy_data = []
for col, label in [(c, AVAILABLE_METRICS[c]) for c in metric_cols]:
    if col not in ratios.columns:
        continue
    
    values = ratios[col].fillna(0).values
    years = ratios['year'].values
    
    for i in range(1, len(values)):
        change = values[i] - values[i-1]
        pct_change = (change / values[i-1] * 100) if values[i-1] != 0 else 0
        yoy_data.append({
            'Metric': label,
            'Year': f'{years[i-1]} → {years[i]}',
            'Absolute Change': round(change, 2),
            'Percentage Change (%)': round(pct_change, 2)
        })

if yoy_data:
    yoy_df = pd.DataFrame(yoy_data)
    st.dataframe(yoy_df, use_container_width=True, hide_index=True, height=300)
else:
    st.info('Not enough data points for year-over-year comparison.')
