"""
check_upload.py - Verify files for GitHub upload

Run this before pushing to GitHub to see what will be uploaded.
"""

import os
from pathlib import Path

# Files that SHOULD be uploaded
ESSENTIAL_PATTERNS = [
    'src/**/*.py',
    'tests/**/*.py',
    'config/*.yaml',
    'config/*.template',
    'db/*.sql',
    '*.md',
    '*.txt',
    '*.ini',
    'Makefile',
    '.gitignore',
    'notebooks/*.sql',
    '*/.gitkeep'
]

# Files that should NOT be uploaded
EXCLUDED_PATTERNS = [
    '.venv/',
    '__pycache__/',
    '*.pyc',
    'data/*.db',
    'data/raw/*.xlsx',
    'data/supporting/*.xlsx',
    'output/*.xlsx',
    'output/*.csv',
    'output/*.log',
    'reports/**/*.png',
    'reports/**/*.pdf',
    '.env',
    '.kiro/',
]

def get_file_size_mb(path):
    """Get file size in MB."""
    try:
        return os.path.getsize(path) / (1024 * 1024)
    except:
        return 0

def check_files():
    """Check which files will be uploaded."""
    
    print("=" * 70)
    print("GitHub Upload Verification")
    print("=" * 70)
    
    # Get all files
    all_files = []
    for root, dirs, files in os.walk('.'):
        # Skip .git directory
        if '.git' in root:
            continue
        for file in files:
            filepath = os.path.join(root, file)
            all_files.append(filepath)
    
    # Categorize files
    to_upload = []
    excluded = []
    large_files = []
    
    for filepath in all_files:
        size_mb = get_file_size_mb(filepath)
        
        # Check if excluded
        is_excluded = False
        for pattern in EXCLUDED_PATTERNS:
            if pattern.replace('/', os.sep) in filepath:
                excluded.append((filepath, size_mb))
                is_excluded = True
                break
        
        if not is_excluded:
            to_upload.append((filepath, size_mb))
            if size_mb > 1:  # Flag files > 1MB
                large_files.append((filepath, size_mb))
    
    # Print results
    print(f"\n✅ Files TO UPLOAD: {len(to_upload)}")
    print(f"❌ Files EXCLUDED: {len(excluded)}")
    
    total_upload_size = sum(size for _, size in to_upload)
    total_excluded_size = sum(size for _, size in excluded)
    
    print(f"\n📊 Upload Size: {total_upload_size:.2f} MB")
    print(f"💾 Saved (excluded): {total_excluded_size:.2f} MB")
    
    # Show large files
    if large_files:
        print(f"\n⚠️  WARNING: Large files (>1MB) to upload:")
        for filepath, size in sorted(large_files, key=lambda x: x[1], reverse=True):
            print(f"   {filepath}: {size:.2f} MB")
    
    # Show sample of files to upload
    print(f"\n✅ Sample files TO UPLOAD (first 20):")
    for filepath, size in sorted(to_upload[:20]):
        print(f"   {filepath}")
    
    # Show sample of excluded files
    print(f"\n❌ Sample files EXCLUDED (first 20):")
    for filepath, size in sorted(excluded[:20]):
        print(f"   {filepath} ({size:.2f} MB)")
    
    # Final check
    print("\n" + "=" * 70)
    if total_upload_size > 50:
        print("⚠️  WARNING: Upload size > 50MB - consider excluding more files")
    elif any(size > 10 for _, size in large_files):
        print("⚠️  WARNING: Some files > 10MB - GitHub may reject them")
    else:
        print("✅ Upload size looks good! Ready to push to GitHub")
    print("=" * 70)
    
    # Security check
    print("\n🔒 SECURITY CHECK:")
    security_issues = []
    for filepath, _ in to_upload:
        if '.env' in filepath and 'template' not in filepath.lower():
            security_issues.append(f"⚠️  {filepath} contains .env (may have secrets)")
        if 'password' in filepath.lower() or 'secret' in filepath.lower():
            security_issues.append(f"⚠️  {filepath} may contain sensitive data")
    
    if security_issues:
        print("⚠️  POTENTIAL SECURITY ISSUES:")
        for issue in security_issues:
            print(f"   {issue}")
    else:
        print("✅ No obvious security issues detected")
    
    print("\n")

if __name__ == '__main__':
    check_files()
