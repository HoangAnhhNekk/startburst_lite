#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [[ ! -d .venv ]]; then python3 -m venv .venv; fi
source .venv/bin/activate
python -m pip install -r requirements.txt
if [[ "${1:-author}" == "demo" ]]; then
  python demo_simulate.py --jobs "${2:-1500}" --capacity "${3:-64}"
else
  bash download_author_log.sh
  python plot_fig9_author.py
fi
