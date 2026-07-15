#!/bin/bash
# builds cloudguard-eb.zip for Elastic Beanstalk upload
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
BUILD="$ROOT/deploy/build"
ZIP="$ROOT/cloudguard-eb.zip"

rm -rf "$BUILD" "$ZIP"
mkdir -p "$BUILD/ui" "$BUILD/.ebextensions" "$BUILD/.platform/nginx/conf.d/elasticbeanstalk" "$BUILD/.streamlit"

cp "$ROOT/deploy/Procfile" "$BUILD/"
cp "$ROOT/deploy/startup.sh" "$BUILD/"
cp "$ROOT/deploy/requirements.txt" "$BUILD/"
cp "$ROOT/deploy/.ebextensions/01_streamlit.config" "$BUILD/.ebextensions/"
cp "$ROOT/deploy/.platform/nginx/conf.d/elasticbeanstalk/00_application.conf" "$BUILD/.platform/nginx/conf.d/elasticbeanstalk/"
cp "$ROOT/deploy/.streamlit/config.toml" "$BUILD/.streamlit/" 2>/dev/null || true
cp "$ROOT/deploy/application.py" "$BUILD/"
cp "$ROOT/config.py" "$ROOT/predict.py" "$BUILD/"
cp "$ROOT/ui/app.py" "$BUILD/ui/"

chmod +x "$BUILD/startup.sh"

(
  cd "$BUILD"
  zip -r "$ZIP" . -x "*.DS_Store"
)

echo "created $ZIP"
echo "upload this zip in Elastic Beanstalk -> Create environment -> Upload your code"
