"""Test script to verify dashboard imports"""
import sys
sys.path.insert(0, '.')

print("Testing dashboard imports...")

try:
    from src.dashboard.utils.db import (
        get_companies, 
        get_ratios, 
        get_pl, 
        get_bs, 
        get_cf, 
        get_sectors, 
        get_peers, 
        get_valuation,
        get_latest_universe,
        get_pros_cons,
        get_peer_group_names,
        get_documents
    )
    print("✅ All db.py functions imported successfully")
except Exception as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

try:
    import streamlit
    print("✅ Streamlit is available")
except Exception as e:
    print(f"❌ Streamlit import error: {e}")
    sys.exit(1)

print("\n✅ All imports successful - dashboard infrastructure is ready")
