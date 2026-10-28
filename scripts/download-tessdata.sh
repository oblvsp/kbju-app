#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p app/src/main/assets/tessdata
for lang in rus eng; do
  url="https://github.com/tesseract-ocr/tessdata_fast/raw/main/${lang}.traineddata"
  out="app/src/main/assets/tessdata/${lang}.traineddata"
  if [ -s "$out" ]; then
    echo "уже существует: $out"
  else
    echo "скачиваю $url"
    curl -fL --retry 3 -o "$out" "$url"
  fi
done
ls -la app/src/main/assets/tessdata
