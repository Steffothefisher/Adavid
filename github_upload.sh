#!/bin/bash
# 🚀 ADAVID GitHub Upload Script
# Automatisches Hochladen zum GitHub (Copy-Paste ready!)
# 
# Verwendung:
#   bash github_upload.sh "Your Name" "your.email@example.com" "YOUR_USERNAME"

set -e  # Exit on error

# ============================================
# FARBEN FÜR TERMINAL OUTPUT
# ============================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'  # No Color

# ============================================
# EINGABE VALIDIERUNG
# ============================================

if [ $# -lt 3 ]; then
    echo -e "${RED}❌ Zu wenig Argumente!${NC}"
    echo "Verwendung: bash github_upload.sh \"Your Name\" \"your.email@example.com\" \"YOUR_GITHUB_USERNAME\""
    echo ""
    echo "Beispiel:"
    echo "  bash github_upload.sh \"Max Mustermann\" \"max@example.com\" \"maxmustermann\""
    exit 1
fi

GIT_NAME="$1"
GIT_EMAIL="$2"
GITHUB_USERNAME="$3"
REPO_NAME="adavid-pharmaceutical-audit"

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  🚀 ADAVID zu GitHub hochladen${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""
echo -e "👤 Name: ${YELLOW}$GIT_NAME${NC}"
echo -e "📧 Email: ${YELLOW}$GIT_EMAIL${NC}"
echo -e "👨‍💻 GitHub Username: ${YELLOW}$GITHUB_USERNAME${NC}"
echo -e "📦 Repository: ${YELLOW}$REPO_NAME${NC}"
echo ""

# ============================================
# SCHRITT 1: Git Konfigurieren
# ============================================

echo -e "${BLUE}SCHRITT 1: Git konfigurieren...${NC}"
git config --global user.name "$GIT_NAME"
git config --global user.email "$GIT_EMAIL"
echo -e "${GREEN}✅ Git konfiguriert${NC}"
echo ""

# ============================================
# SCHRITT 2: Verzeichnisstruktur erstellen
# ============================================

echo -e "${BLUE}SCHRITT 2: Verzeichnisstruktur erstellen...${NC}"

mkdir -p adavid-pharmaceutical-audit/{docs,src/utils,frontend,examples,tests}
cd adavid-pharmaceutical-audit

echo -e "${GREEN}✅ Verzeichnisse erstellt${NC}"
echo ""

# ============================================
# SCHRITT 3: Git initialisieren
# ============================================

echo -e "${BLUE}SCHRITT 3: Git Repository initialisieren...${NC}"

git init
git branch -M main

echo -e "${GREEN}✅ Repository initialisiert${NC}"
echo ""

# ============================================
# SCHRITT 4: requirements.txt erstellen
# ============================================

echo -e "${BLUE}SCHRITT 4: requirements.txt erstellen...${NC}"

cat > requirements.txt << 'EOF'
pandas>=1.3.0
numpy>=1.21.0
scipy>=1.7.0
scikit-learn>=0.24.0
matplotlib>=3.4.0
jupyter>=1.0.0
EOF

echo -e "${GREEN}✅ requirements.txt erstellt${NC}"
echo ""

# ============================================
# SCHRITT 5: .gitignore erstellen
# ============================================

echo -e "${BLUE}SCHRITT 5: .gitignore erstellen...${NC}"

cat > .gitignore << 'EOF'
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST
.venv
venv/
ENV/
env/
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store
Thumbs.db
data/
results/
*.csv
*.json
*.log
.ipynb_checkpoints/
.pytest_cache/
.coverage
htmlcov/
EOF

echo -e "${GREEN}✅ .gitignore erstellt${NC}"
echo ""

# ============================================
# SCHRITT 6: setup.py erstellen
# ============================================

echo -e "${BLUE}SCHRITT 6: setup.py erstellen...${NC}"

cat > setup.py << 'EOF'
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="adavid-pharmaceutical-audit",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Advanced Data-Driven Pharmaceutical Audit System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/USERNAME/adavid-pharmaceutical-audit",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "scikit-learn>=0.24.0",
    ],
)
EOF

echo -e "${GREEN}✅ setup.py erstellt${NC}"
echo ""

# ============================================
# SCHRITT 7: LICENSE erstellen
# ============================================

echo -e "${BLUE}SCHRITT 7: MIT LICENSE erstellen...${NC}"

cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2026 ADAVID Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
EOF

echo -e "${GREEN}✅ LICENSE erstellt${NC}"
echo ""

# ============================================
# SCHRITT 8: __init__.py Dateien
# ============================================

echo -e "${BLUE}SCHRITT 8: Python __init__.py Dateien erstellen...${NC}"

touch src/__init__.py
touch src/utils/__init__.py
touch tests/__init__.py

echo -e "${GREEN}✅ __init__.py Dateien erstellt${NC}"
echo ""

# ============================================
# SCHRITT 9: Git Add & Commit
# ============================================

echo -e "${BLUE}SCHRITT 9: Git Add & Commit...${NC}"

git add .
git commit -m "Initial ADAVID commit: Pharmaceutical audit system with Simpson's Paradox detection and deep subgroup analysis"

echo -e "${GREEN}✅ Alle Dateien committed${NC}"
echo ""

# ============================================
# SCHRITT 10: GitHub Remote verbinden
# ============================================

echo -e "${BLUE}SCHRITT 10: GitHub Remote verbinden...${NC}"

REPO_URL="https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"
git remote add origin "$REPO_URL"

echo -e "${GREEN}✅ GitHub Remote hinzugefügt: $REPO_URL${NC}"
echo ""

# ============================================
# SCHRITT 11: INSTRUKTION FÜR PUSH
# ============================================

echo -e "${YELLOW}════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}⚠️  WICHTIG - Folgende Schritte sind MANUELL notwendig:${NC}"
echo -e "${YELLOW}════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}1️⃣  Erstelle ein neues GitHub Repository:${NC}"
echo -e "   → Gehe zu: ${YELLOW}https://github.com/new${NC}"
echo -e "   → Repository Name: ${YELLOW}adavid-pharmaceutical-audit${NC}"
echo -e "   → Public ✅"
echo -e "   → NO README (wir haben schon einen!)"
echo -e "   → Add .gitignore: Python ✅"
echo -e "   → Click: ${YELLOW}Create repository${NC}"
echo ""
echo -e "${BLUE}2️⃣  Dann kopiere & führe folgende Kommandos aus:${NC}"
echo -e "${YELLOW}git push -u origin main${NC}"
echo ""
echo -e "${BLUE}3️⃣  Danach sollte dein Repository erreichbar sein:${NC}"
echo -e "   ${YELLOW}https://github.com/${GITHUB_USERNAME}/${REPO_NAME}${NC}"
echo ""
echo -e "${GREEN}✅ Setup abgeschlossen!${NC}"
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo -e "Hilfreiche Befehle für später:${NC}"
echo -e "  ${YELLOW}git status${NC}          - Zeige Status"
echo -e "  ${YELLOW}git add .${NC}             - Stage Änderungen"
echo -e "  ${YELLOW}git commit -m \"msg\"${NC}  - Commit mit Nachricht"
echo -e "  ${YELLOW}git push origin main${NC}   - Push zu GitHub"
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
