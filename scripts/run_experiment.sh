#!/bin/bash
set -euo pipefail

PROJECT=${1:-}
VERSION=${2:-}

if [[ -z "$PROJECT" || -z "$VERSION" ]]; then
  echo "Usage: $0 <Defects4J project> <version>"
  exit 1
fi

WORKDIR="data/subjects/${PROJECT}_${VERSION}"
SLICE_OUT="data/outputs/${PROJECT}_${VERSION}_slice.json"
INVARIANT_OUT="data/outputs/${PROJECT}_${VERSION}_invariant.smt2"

mkdir -p data/subjects data/outputs

echo ">>> Setting up Defects4J project: $PROJECT $VERSION"
defects4j checkout -p "$PROJECT" -v "$VERSION" -w "$WORKDIR"

echo ">>> Phase 1: Running static slicer"
./scripts/run_slicer.sh "$WORKDIR" "${PROJECT}_${VERSION}" "$SLICE_OUT"

echo ">>> Phase 2: LLM reasoning"
python3 core/reasoning/engine.py \
  --project "$PROJECT" \
  --version "$VERSION" \
  --slice-file "$SLICE_OUT" \
  --output "$INVARIANT_OUT"

echo ">>> Invariant written to $INVARIANT_OUT"
