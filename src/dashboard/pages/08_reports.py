"""
08_reports.py — Annual Reports screen.

Spec requirements:
  ✅ Search + BSE PDF links
  ✅ 404 badge for unavailable reports
"""

import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import streamlit as st
import pandas as pd

from src.dashboard.utils.db import get_companies, get_documents

st.header('📄 Annual Reports')

# ── Company selector ──────────────────────────────────────────────────────────
cos = get_companies()
options = [f"{row['id']} — {row['company_name']}" for _, row in cos.iterrows()]
options.sort()

selected = st.selectbox('🔍 Select Company', options)
if not selected:
    st.info('Please select a company to view annual reports.')
    st.stop()

ticker = selected.split(' — ')[0].strip()
company_name = selected.split(' — ')[1].strip()

st.subheader(f'Annual Reports — {company_name}')

# ── Load documents ────────────────────────────────────────────────────────────
docs = get_documents(ticker)

if docs.empty:
    st.warning(f'No annual reports found for {ticker}.')
    st.info('Annual reports may not be available in the database.')
    st.stop()

# ── Display reports ───────────────────────────────────────────────────────────
st.caption(f'Found {len(docs)} annual reports')

# Create display dataframe
display_docs = docs.copy()

# Check if Annual_Report column exists and has valid URLs
if 'Annual_Report' not in display_docs.columns:
    st.error('Annual_Report column not found in documents table.')
    st.stop()

# Add status column
display_docs['Status'] = display_docs['Annual_Report'].apply(
    lambda x: '🔗 Available' if pd.notna(x) and str(x).strip() and str(x) != 'nan' else '❌ Not Available'
)

# Display table with clickable links
for idx, row in display_docs.iterrows():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.write(f"**{row['Year']}**")
    
    with col2:
        url = row.get('Annual_Report', '')
        if pd.notna(url) and str(url).strip() and str(url) != 'nan':
            st.markdown(f"[📥 Download PDF]({url})")
        else:
            st.write('—')
    
    with col3:
        if pd.notna(url) and str(url).strip() and str(url) != 'nan':
            st.success('Available')
        else:
            st.error('404')
    
    st.divider()

# ── Summary statistics ────────────────────────────────────────────────────────
st.subheader('📊 Report Availability')

available_count = display_docs['Annual_Report'].apply(
    lambda x: 1 if pd.notna(x) and str(x).strip() and str(x) != 'nan' else 0
).sum()

unavailable_count = len(display_docs) - available_count

col1, col2, col3 = st.columns(3)
col1.metric('Total Reports', len(display_docs))
col2.metric('Available', available_count)
col3.metric('Not Available', unavailable_count)

# ── Help text ─────────────────────────────────────────────────────────────────
st.divider()
st.info("""
**Note:** Annual reports are sourced from BSE. Some reports may be unavailable due to:
- Company not listed on BSE
- Reports not yet published
- Technical issues with source links
- Historical reports predating digital archives
""")
