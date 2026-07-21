"""
06_sectors.py — Sector Analysis screen.

Spec requirements:
  ✅ Bubble chart X=Revenue, Y=ROE, size=MarketCap, colour=sub-sector
  ✅ Median KPI bar chart below bubble
"""

import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import streamlit as st
import pandas as pd
import plotly.express as px

from src.dashboard.utils.db import get_sectors

st.header('🏢 Sector Analysis')

# ── Load sector data ──────────────────────────────────────────────────────────
sectors_df = get_sectors()

if sectors_df.empty:
    st.warning('No sector data available.')
    st.stop()

# ── Sector selector ───────────────────────────────────────────────────────────
available_sectors = sorted(sectors_df['broad_sector'].dropna().unique().tolist())

selected_sector = st.selectbox('📊 Select Sector', ['All Sectors'] + available_sectors)

# Filter by sector if specific sector selected
if selected_sector != 'All Sectors':
    display_df = sectors_df[sectors_df['broad_sector'] == selected_sector].copy()
else:
    display_df = sectors_df.copy()

if display_df.empty:
    st.warning(f'No data available for {selected_sector}')
    st.stop()

# ── Prepare bubble chart data ─────────────────────────────────────────────────
# Need: Revenue (from sales column in latest P&L), ROE, Market Cap, Sub-sector

# Get sales data from database
import sqlite3
DB_PATH = os.getenv('DB_PATH', 'data/nifty100.db')

@st.cache_data(ttl=600)
def get_sales_data():
    with sqlite3.connect(DB_PATH) as conn:
        query = """
        SELECT pl.company_id, pl.sales, pl.year
        FROM profitandloss pl
        JOIN (
            SELECT company_id, MAX(year) AS yr
            FROM profitandloss
            GROUP BY company_id
        ) l ON pl.company_id = l.company_id AND pl.year = l.yr
        """
        return pd.read_sql(query, conn)

sales_df = get_sales_data()

# Merge sales with sector data
bubble_df = display_df.merge(sales_df, on='company_id', how='left')

# Filter out rows with missing critical data
bubble_df = bubble_df[
    bubble_df['sales'].notna() &
    bubble_df['return_on_equity_pct'].notna() &
    bubble_df['market_cap_crore'].notna()
]

if bubble_df.empty:
    st.warning('Insufficient data for bubble chart.')
else:
    st.subheader('💹 Revenue vs ROE Bubble Chart')
    st.caption('Bubble size = Market Cap | Color = Sub-sector')
    
    # Create bubble chart
    fig = px.scatter(
        bubble_df,
        x='sales',
        y='return_on_equity_pct',
        size='market_cap_crore',
        color='sub_sector',
        hover_data=['company_id', 'market_cap_crore'],
        labels={
            'sales': 'Revenue (₹ Crore)',
            'return_on_equity_pct': 'ROE (%)',
            'market_cap_crore': 'Market Cap (₹ Cr)',
            'sub_sector': 'Sub-sector'
        },
        template='plotly_dark',
        height=500
    )
    
    fig.update_traces(marker=dict(line=dict(width=1, color='white')))
    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(orientation='v', yanchor='top', y=1, xanchor='left', x=1.02)
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ── Median KPI bar chart ──────────────────────────────────────────────────────
st.divider()
st.subheader('📊 Sector Median KPIs')

# Calculate median KPIs per sector
if selected_sector == 'All Sectors':
    agg_df = sectors_df.groupby('broad_sector').agg({
        'return_on_equity_pct': 'median',
        'return_on_capital_employed_pct': 'median',
        'net_profit_margin_pct': 'median',
        'debt_to_equity': 'median',
        'current_ratio': 'median'
    }).reset_index()
    
    agg_df.columns = ['Sector', 'Median ROE%', 'Median ROCE%', 'Median NPM%', 'Median D/E', 'Median Current Ratio']
    
    # Display all sectors comparison
    st.dataframe(agg_df.round(2), use_container_width=True, hide_index=True)
    
    # Bar chart for ROE comparison
    fig2 = px.bar(
        agg_df.sort_values('Median ROE%'),
        x='Median ROE%',
        y='Sector',
        orientation='h',
        template='plotly_dark',
        color='Median ROE%',
        color_continuous_scale='Viridis',
        labels={'Median ROE%': 'Median ROE (%)'}
    )
    fig2.update_layout(height=400, showlegend=False, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig2, use_container_width=True)
    
else:
    # Show KPIs for selected sector only
    kpis = {
        'Median ROE (%)': display_df['return_on_equity_pct'].median(),
        'Median ROCE (%)': display_df['return_on_capital_employed_pct'].median(),
        'Median NPM (%)': display_df['net_profit_margin_pct'].median(),
        'Median D/E': display_df['debt_to_equity'].median(),
        'Median Current Ratio': display_df['current_ratio'].median(),
        'Companies': len(display_df)
    }
    
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric('Median ROE', f"{kpis['Median ROE (%)']:.1f}%")
    c2.metric('Median ROCE', f"{kpis['Median ROCE (%)']:.1f}%")
    c3.metric('Median NPM', f"{kpis['Median NPM (%)']:.1f}%")
    c4.metric('Median D/E', f"{kpis['Median D/E']:.2f}×")
    c5.metric('Median CR', f"{kpis['Median Current Ratio']:.2f}×")
    c6.metric('Companies', f"{kpis['Companies']}")
    
    # List companies in sector
    st.divider()
    st.subheader(f'Companies in {selected_sector}')
    
    company_list = display_df[['company_id', 'sub_sector', 'return_on_equity_pct', 'market_cap_crore']].copy()
    company_list = company_list.rename(columns={
        'company_id': 'Ticker',
        'sub_sector': 'Sub-sector',
        'return_on_equity_pct': 'ROE%',
        'market_cap_crore': 'Market Cap (Cr)'
    })
    company_list = company_list.sort_values('ROE%', ascending=False)
    st.dataframe(company_list.round(2), use_container_width=True, hide_index=True, height=300)
