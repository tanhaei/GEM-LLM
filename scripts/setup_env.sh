#!/bin/bash
set -euo pipefail

echo ">>> Installing Python dependencies..."
pip install -r requirements.txt

echo ">>> Verifying Z3 installation..."
python3 -c "import z3; print('Z3 Version:', z3.get_version_string())"

echo ">>> Checking Java/Maven environment..."
command -v java >/dev/null && java -version
command -v mvn >/dev/null && mvn -version

echo ">>> Environment ready. Place Defects4J datasets in data/subjects/"
