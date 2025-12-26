#!/bin/bash
# GEM-LLM Experiment Runner [cite: 213, 233]

PROJECT=$1  # e.g., Chart
VERSION=$2  # e.g., 1b

echo ">>> Setting up Defects4J project: $PROJECT $VERSION"
defects4j checkout -p $PROJECT -v $VERSION -w data/subjects/${PROJECT}_${VERSION}

echo ">>> Phase 1: Running Static Slicer (Soot)"
mvn -f core/slicer/pom.xml exec:java -Dexec.mainClass="ir.ac.ilam.tanhaei.ContextSlicer"

echo ">>> Phase 2 & 3: LLM Reasoning and SMT Verification"
python3 core/reasoning/engine.py --project $PROJECT --version $VERSION
