#!/bin/bash
set -euo pipefail

CLASSPATH_DIR=${1:-}
MAIN_CLASS=${2:-}
OUTPUT_JSON=${3:-data/outputs/slice.json}
TARGET_METHOD=${4:-}

if [[ -z "$CLASSPATH_DIR" || -z "$MAIN_CLASS" ]]; then
  echo "Usage: $0 <classpath-dir> <main-class> [output-json] [target-method-signature]"
  exit 1
fi

mkdir -p "$(dirname "$OUTPUT_JSON")"

mvn -q -f core/slicer/pom.xml exec:java \
  -Dexec.mainClass="ir.ac.ilam.tanhaei.ContextSlicer" \
  -Dexec.args="$CLASSPATH_DIR $MAIN_CLASS $OUTPUT_JSON $TARGET_METHOD"

echo ">>> Slice written to $OUTPUT_JSON"
