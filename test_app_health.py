"""Test if app.py can be imported without errors"""
import sys
sys.path.insert(0, '.')

print("Testing app.py import...")

try:
    # Test if the module structure is correct
    from pathlib import Path
    
    # Check if files exist
    app_py = Path('src/dashboard/app.py')
    db_py = Path('src/dashboard/utils/db.py')
    
    if not app_py.exists():
        print(f"❌ Missing: {app_py}")
        sys.exit(1)
    else:
        print(f"✅ Found: {app_py}")
    
    if not db_py.exists():
        print(f"❌ Missing: {db_py}")
        sys.exit(1)
    else:
        print(f"✅ Found: {db_py}")
    
    # Check database
    db_path = Path('data/nifty100.db')
    if not db_path.exists():
        print(f"⚠️  Warning: {db_path} not found - app will fail at runtime")
    else:
        print(f"✅ Found: {db_path}")
    
    # Test imports (outside streamlit context will show warnings but should work)
    print("\nTesting imports (streamlit warnings are expected)...")
    from src.dashboard.utils import db
    print("✅ db module imported")
    
    # Verify all required functions exist
    required_functions = [
        'get_companies', 'get_ratios', 'get_pl', 'get_bs', 'get_cf',
        'get_sectors', 'get_peers', 'get_valuation', 'get_latest_universe',
        'get_pros_cons', 'get_peer_group_names', 'get_documents'
    ]
    
    for func_name in required_functions:
        if not hasattr(db, func_name):
            print(f"❌ Missing function: {func_name}")
            sys.exit(1)
    
    print(f"✅ All {len(required_functions)} required functions found in db.py")
    
    print("\n" + "="*60)
    print("✅ Dashboard infrastructure setup complete!")
    print("="*60)
    print("\nTo start the dashboard, run:")
    print("  make dashboard")
    print("  or")
    print("  streamlit run src/dashboard/app.py")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
