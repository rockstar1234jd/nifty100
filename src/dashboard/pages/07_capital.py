"""
07_capital.py — Capital Allocation screen.

Spec requirements:
  ✅ Plotly treemap by 8 allocation patterns
"""

import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.header('💰 Capital Allocation Patterns')

# ── Load capital allocation data ──────────────────────────────────────────────
CAPITAL_FILE = Path('output/capital_allocation.csv')

if not CAPITAL_FILE.exists():
    st.warning('Capital allocation data file not found. Please run the capital allocation analysis first.')
    st.info('Expected file: output/capital_allocation.csv')
    st.stop()

try:
    capital_df = pd.read_csv(CAPITAL_FILE)
except Exception as e:
    st.error(f'Error reading capital allocation file: {e}')
    st.stop()

if capital_df.empty:
    st.warning('No capital allocation data available.')
    st.stop()

# ── Validate required columns ─────────────────────────────────────────────────
required_cols = ['company_id', 'capital_allocation_pattern']
missing_cols = [c for c in required_cols if c not in capital_df.columns]

if missing_cols:
    st.error(f'Missing required columns: {", ".join(missing_cols)}')
    st.stop()

# ── Add company names ─────────────────────────────────────────────────────────
from src.dashboard.utils.db import get_companies

companies = get_companies()
capital_df = capital_df.merge(
    companies[['id', 'company_name', 'broad_sector']],
    left_on='company_id',
    right_on='id',
    how='left'
)

# ── Pattern distribution ──────────────────────────────────────────────────────
st.subheader('📊 Pattern Distribution')

pattern_counts = capital_df['capital_allocation_pattern'].value_counts().reset_index()
pattern_counts.columns = ['Pattern', 'Count']

c1, c2, c3 = st.columns(3)
c1.metric('Total Companies', len(capital_df))
c2.metric('Unique Patterns', len(pattern_counts))
c3.metric('Most Common', pattern_counts.iloc[0]['Pattern'] if not pattern_counts.empty else 'N/A')

st.divider()

# ── Treemap visualization ─────────────────────────────────────────────────────
st.subheader('🗂️ Capital Allocation Treemap')
st.caption('Size = Number of companies | Color = Allocation pattern')

# Prepare treemap data
treemap_df = capital_df.copy()
treemap_df['value'] = 1  # Each company counts as 1

# Create treemap
fig = px.treemap(
    treemap_df,
    path=['capital_allocation_pattern', 'company_name'],
    values='value',
    color='capital_allocation_pattern',
    hover_data=['broad_sector'],
    color_discrete_sequence=px.colors.qualitative.Set3,
    template='plotly_dark',
    height=600
)

fig.update_traces(
    textposition='middle center',
    marker=dict(line=dict(width=2, color='white'))
)

fig.update_layout(
    margin=dict(l=10, r=10, t=30, b=10)
)

st.plotly_chart(fig, use_container_width=True)

# ── Pattern descriptions ──────────────────────────────────────────────────────
st.divider()
st.subheader('📋 Pattern Definitions')

PATTERN_DESCRIPTIONS = {
    'High Growth Reinvestment': 'Companies reinvesting heavily in growth with minimal shareholder payouts',
    'Balanced Growth & Returns': 'Companies balancing growth investments with shareholder returns',
    'Dividend Focus': 'Companies prioritizing dividend payouts to shareholders',
    'Share Buybacks': 'Companies actively buying back shares',
    'Debt Reduction': 'Companies focused on paying down debt',
    'Accumulation': 'Companies accumulating cash without clear allocation strategy',
    'Distressed': 'Companies with negative cash flows or severe financial constraints',
    'Special Situations': 'Companies with unique or irregular allocation patterns'
}

for pattern, desc in PATTERN_DESCRIPTIONS.items():
    count = len(capital_df[capital_df['capital_allocation_pattern'] == pattern])
    if count > 0:
        with st.expander(f'**{pattern}** ({count} companies)'):
            st.write(desc)
            companies_in_pattern = capital_df[
                capital_df['capital_allocation_pattern'] == pattern
            ][['company_id', 'company_name', 'broad_sector']].sort_values('company_name')
            st.dataframe(companies_in_pattern, use_container_width=True, hide_index=True)

# ── Pattern statistics ────────────────────────────────────────────────────────
st.divider()
st.subheader('📈 Pattern Statistics')

pattern_stats = capital_df.groupby('capital_allocation_pattern').agg({
    'company_id': 'count'
}).reset_index()
pattern_stats.columns = ['Pattern', 'Company Count']
pattern_stats = pattern_stats.sort_values('Company Count', ascending=False)

col1, col2 = st.columns(2)

with col1:
    # Bar chart of pattern counts
    fig2 = px.bar(
        pattern_stats,
        x='Company Count',
        y='Pattern',
        orientation='h',
        template='plotly_dark',
        color='Company Count',
        color_continuous_scale='Viridis'
    )
    fig2.update_layout(
        height=400,
        showlegend=False,
        margin=dict(l=10, r=10, t=20, b=10)
    )
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    # Pie chart of pattern distribution
    fig3 = px.pie(
        pattern_stats,
        values='Company Count',
        names='Pattern',
        template='plotly_dark',
        hole=0.4
    )
    fig3.update_layout(
        height=400,
        margin=dict(l=10, r=10, t=20, b=10)
    )
    st.plotly_chart(fig3, use_container_width=True)
