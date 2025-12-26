#!/bin/bash
# Setup script for GEM-LLM Replication Package

echo ">>> Installing Python dependencies..."
pip install -r requirements.txt

echo ">>> Verifying Z3 Installation..."
python3 -c "import z3; print('Z3 Version:', z3.get_version_string())"

echo ">>> Checking Java Environment for Soot..."
java -version
mvn -version

echo ">>> Environment ready. Place Defects4J datasets in /data/subjects/"
