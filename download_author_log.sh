#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p data
DEST="data/ablate_waiting_policies.log"
if [ -s "$DEST" ]; then echo "Already exists: $DEST"; exit 0; fi
echo 'Downloading published simulation log from author public GCS bucket...'
if command -v gsutil >/dev/null 2>&1; then
  gsutil cp gs://starburst_bucket/logs/ablate_waiting_policies.log "$DEST"
elif command -v gcloud >/dev/null 2>&1; then
  gcloud storage cp gs://starburst_bucket/logs/ablate_waiting_policies.log "$DEST"
elif command -v curl >/dev/null 2>&1; then
  curl -fL --retry 3 -o "$DEST.part" https://storage.googleapis.com/starburst_bucket/logs/ablate_waiting_policies.log
  mv "$DEST.part" "$DEST"
else
  echo 'Install curl or gsutil, or manually copy the author log into data/' >&2
  exit 1
fi
ls -lh "$DEST"
