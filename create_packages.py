#!/usr/bin/env python3
"""
Erstelle ZIP-Archive und strukturierte Packages
"""

import os
import shutil
import zipfile
from datetime import datetime

# Create organized folders
packages = {
    'ADAVID_Core': [
        'README.md',
        'COMPLETE_FILE_INDEX.md',
        'adavid_scoring_system.py',
        'adavid_deep_audit_engine.py',
        'adavid_v2_improvements.py',
    ],
    'ADAVID_Documentation': [
        'ADAVID_Code_Analysis.md',
        'ADAVID_Scoring_System_Documentation.md',
        'ADAVID_Deep_Audit_Documentation.md',
        'ADAVID_Deep_Audit_Quick_Reference.md',
        'ADAVID_IMPROVEMENTS_ROADMAP.md',
        'ADAVID_v2_EXECUTIVE_SUMMARY.md',
    ],
    'ADAVID_Tools': [
        'adavid_dataset_loader.py',
        'adavid_scoring_dashboard.jsx',
        'adavid_audit_dashboard.jsx',
        'adavid_visual_guide.html',
    ],
    'Setup_and_GitHub': [
        'QUICK_START_GUIDE.md',
        'GITHUB_UPLOAD_GUIDE.md',
        'github_upload.sh',
        'ANDROID_GIT_APPS_GUIDE.md',
        'ANDROID_GIT_APPS_2025_UPDATED.md',
    ],
    'Data_Resources': [
        'Public_Clinical_Datasets_Guide.md',
    ]
}

# Create ZIP files
for package_name, files in packages.items():
    zip_filename = f'{package_name}.zip'
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in files:
            if os.path.exists(file):
                zipf.write(file, arcname=f'{package_name}/{file}')
                print(f'✅ Added {file} to {zip_filename}')
    
    print(f'📦 Created {zip_filename}\n')

# Create master archive with everything
master_zip = 'ADAVID_Complete_System.zip'
with zipfile.ZipFile(master_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith(('.md', '.py', '.jsx', '.html', '.sh')):
                filepath = os.path.join(root, file)
                arcname = filepath.lstrip('./')
                zipf.write(filepath, arcname)
                print(f'✅ Added {filepath}')

print(f'\n🎉 Master archive created: {master_zip}')
