#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../astro"
npm run build

cp ../data/meta.json ../docs/meta.json
cp ../data/clsvip_meta.json ../docs/clsvip_meta.json
