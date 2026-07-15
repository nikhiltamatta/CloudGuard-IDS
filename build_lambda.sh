#!/bin/bash
# builds a slim lambda.zip that fits AWS size limits
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
BUILD="$ROOT/lambda/build"
ZIP="$ROOT/lambda/lambda.zip"
MODEL="logistic_regression"

rm -rf "$BUILD" "$ZIP"
mkdir -p "$BUILD/data/processed" "$BUILD/models/$MODEL"

echo "installing minimal python deps for Lambda..."
python3 -m pip install \
  --platform manylinux2014_x86_64 \
  --target "$BUILD" \
  --implementation cp \
  --python-version 3.11 \
  --only-binary=:all: \
  --upgrade \
  scikit-learn==1.6.1 numpy joblib scipy

# strip bulky test folders to reduce unzipped size
find "$BUILD" -type d \( -name tests -o -name test -o -name __pycache__ \) -prune -exec rm -rf {} + 2>/dev/null || true

cp "$ROOT/deploy/lambda_predict.py" "$BUILD/predict.py"
cp "$ROOT/data/processed/feature_columns.csv" "$BUILD/data/processed/"
cp "$ROOT/models/$MODEL/model.joblib" "$BUILD/models/$MODEL/"

(
  cd "$BUILD"
  zip -r9 "$ZIP" . -x "*.pyc" "__pycache__/*" "*.DS_Store"
)

UNZIPPED=$(du -sk "$BUILD" | cut -f1)
ZIP_SIZE=$(du -k "$ZIP" | cut -f1)
echo "created $ZIP"
echo "unzipped size: ${UNZIPPED} KB (limit 262144 KB)"
echo "zip size: ${ZIP_SIZE} KB"

if [ "$UNZIPPED" -gt 262144 ]; then
  echo "warning: unzipped size still exceeds Lambda limit"
  exit 1
fi
