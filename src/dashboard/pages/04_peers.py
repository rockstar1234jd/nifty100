"""
04_peers.py — Peer Comparison screen.

Spec requirements:
  ✅ 11-group dropdown
  ✅ Radar chart via Plotly Scatterpolar — company vs peer avg
  ✅ KPI table with benchmark row highlighted
"""

import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from src.dashboard.utils.db import get_peers, get_peer_group_names

st.header('🔄 Peer Comparison')

# ── Peer group selector ───────────────────────────────────────────────────────
peer_groups = get_peer_group_names()

if not peer_groups:
    st.warning('No peer groups found in the database.')
    st.stop()

selected_group = st.selectbox('📊 Select Peer Group', peer_groups)

if not selected_group:
    st.info('Please select a peer group to view comparison.')
    st.stop()

# ── Load peer data ────────────────────────────────────────────────────────────
peers_df = get_peers(selected_group)

if peers_df.empty:
    st.warning(f'No data found for peer group: {selected_group}')
    st.stop()

# ── Radar chart metrics ───────────────────────────────────────────────────────
RADAR_METRICS = {
    'return_on_equity_pct': 'ROE',
    'return_on_capital_employed_pct': 'ROCE',
    'net_profit_margin_pct': 'NPM',
    'current_ratio': 'Current Ratio',
    'debt_to_equity': 'D/E (inverted)',
    'interest_coverage': 'Interest Coverage'
}

# Calculate peer averages
peer_avg = {}
for col, label in RADAR_METRICS.items():
    if col in peers_df.columns:
        # For D/E, invert so lower is better (higher on radar)
        if col == 'debt_to_equity':
            # Invert: 1 / (1 + D/E) so 0 D/E = 100%, high D/E = low%
            peers_df[f'{col}_radar'] = 100 / (1 + peers_df[col].fillna(999))
            peer_avg[label] = peers_df[f'{col}_radar'].mean()
        else:
            peer_avg[label] = peers_df[col].mean()

# ── Display peer table ────────────────────────────────────────────────────────
st.subheader('📋 Peer Group Members')

display_cols = ['company_id', 'company_name'] + [c for c in RADAR_METRICS.keys() if c in peers_df.columns]
if 'is_benchmark' in peers_df.columns:
    display_cols.append('is_benchmark')

display_df = peers_df[display_cols].copy()

# Rename columns
rename_dict = {
    'company_id': 'Ticker',
    'company_name': 'Company',
    'return_on_equity_pct': 'ROE%',
    'return_on_capital_employed_pct': 'ROCE%',
    'net_profit_margin_pct': 'NPM%',
    'current_ratio': 'Current Ratio',
    'debt_to_equity': 'D/E',
    'interest_coverage': 'Interest Coverage',
    'is_benchmark': 'Benchmark'
}
display_df = display_df.rename(columns=rename_dict)

# Round numeric columns
for col in ['ROE%', 'ROCE%', 'NPM%', 'Current Ratio', 'D/E', 'Interest Coverage']:
    if col in display_df.columns:
        display_df[col] = display_df[col].round(2)

# Highlight benchmark row
if 'Benchmark' in display_df.columns:
    benchmark_row = display_df[display_df['Benchmark'] == 1]
    if not benchmark_row.empty:
        st.info(f'⭐ Benchmark company: {benchmark_row.iloc[0]["Company"]}')

st.dataframe(display_df, use_container_width=True, hide_index=True, height=300)

# ── Radar chart for each company ──────────────────────────────────────────────
st.subheader('📡 Radar Chart Comparison')

selected_company = st.selectbox(
    '🏢 Select company for radar comparison',
    peers_df['company_name'].tolist()
)

company_row = peers_df[peers_df['company_name'] == selected_company].iloc[0]

# Prepare radar data
categories = list(RADAR_METRICS.values())
company_values = []
peer_avg_values = []

for col, label in RADAR_METRICS.items():
    if col in peers_df.columns:
        if col == 'debt_to_equity':
            company_values.append(100 / (1 + company_row[col]) if pd.notna(company_row[col]) else 0)
        else:
            company_values.append(company_row[col] if pd.notna(company_row[col]) else 0)
        peer_avg_values.append(peer_avg.get(label, 0))

# Create radar chart
fig = go.Figure()

fig.add_trace(go.Scatterpolar(
    r=company_values,
    theta=categories,
    fill='toself',
    name=selected_company,
    line=dict(color='#4fc3f7', width=2)
))

fig.add_trace(go.Scatterpolar(
    r=peer_avg_values,
    theta=categories,
    fill='toself',
    name='Peer Average',
    line=dict(color='#ffb74d', width=2),
    opacity=0.6
))

fig.update_layout(
    polar=dict(
        radialaxis=dict(visible=True, range=[0, max(max(company_values), max(peer_avg_values)) * 1.1])
    ),
    showlegend=True,
    template='plotly_dark',
    height=500
)

st.plotly_chart(fig, use_container_width=True)

# ── KPI comparison table ──────────────────────────────────────────────────────
st.subheader('📊 Detailed Metrics Comparison')

comparison_data = {
    'Metric': list(RADAR_METRICS.values()),
    selected_company: company_values,
    'Peer Average': peer_avg_values
}

comparison_df = pd.DataFrame(comparison_data)
comparison_df[selected_company] = comparison_df[selected_company].round(2)
comparison_df['Peer Average'] = comparison_df['Peer Average'].round(2)

st.dataframe(comparison_df, use_container_width=True, hide_index=True)
