#!/bin/bash
# builds cloudguard-eb.zip for Elastic Beanstalk upload
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
BUILD="$ROOT/deploy/build"
ZIP="$ROOT/cloudguard-eb.zip"
REPORTS="$ROOT/data/processed/reports"

rm -rf "$BUILD" "$ZIP"
mkdir -p "$BUILD/.ebextensions" "$BUILD/.platform/nginx/conf.d/elasticbeanstalk"
mkdir -p "$BUILD/data/processed/reports/figures"

cp "$ROOT/deploy/Procfile" "$BUILD/"
cp "$ROOT/deploy/startup.sh" "$BUILD/"
cp "$ROOT/deploy/requirements.txt" "$BUILD/"
cp "$ROOT/deploy/.ebextensions/01_streamlit.config" "$BUILD/.ebextensions/"
cp "$ROOT/deploy/.platform/nginx/conf.d/elasticbeanstalk/00_application.conf" "$BUILD/.platform/nginx/conf.d/elasticbeanstalk/"
# same Flask app used locally and on EB
cp "$ROOT/application.py" "$BUILD/"
cp "$ROOT/config.py" "$ROOT/predict.py" "$BUILD/"

# bundle report charts so they work even if S3 chart upload is missing
if [ -d "$REPORTS/figures" ]; then
  cp -R "$REPORTS/figures/." "$BUILD/data/processed/reports/figures/"
fi
if [ -f "$REPORTS/model_comparison.csv" ]; then
  cp "$REPORTS/model_comparison.csv" "$BUILD/data/processed/reports/"
fi
for chart in "$REPORTS"/learning_curve_*.png "$REPORTS/error_heatmap.png"; do
  if [ -f "$chart" ]; then
    cp "$chart" "$BUILD/data/processed/reports/"
  fi
done

chmod +x "$BUILD/startup.sh"

(
  cd "$BUILD"
  zip -r "$ZIP" . -x "*.DS_Store"
)

echo "created $ZIP"
echo "upload this zip in Elastic Beanstalk -> Create environment -> Upload your code"
