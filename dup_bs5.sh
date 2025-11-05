#!/usr/bin/env bash
set -euo pipefail

# Usage: ./dup_bs5.sh [racine]
ROOT="${1:-src/apps}"

copied=0
skipped=0

find "$ROOT" \
  \( -path "*/templates/*" -o -path "*/template/*" \) \
  -type f \( -name "*.html" -o -name "*.htm" \) \
  ! -name "*_bs5.html" ! -name "*_bs5.htm" \
  -print0 |
while IFS= read -r -d '' f; do
  dir=$(dirname "$f")
  base=$(basename "$f")
  ext="${base##*.}"          # html | htm
  name="${base%.*}"          # nom sans extension
  dest="$dir/${name}_bs5.$ext"

  if [[ -e "$dest" ]]; then
    echo "SKIP (existe déjà): $dest"
    ((skipped++)) || true
  else
    cp -p -- "$f" "$dest"    # -p préserve les timestamps/permissions
    echo "COPY: $f -> $dest"
    ((copied++)) || true
  fi
done

echo "----"
echo "Fichiers copiés : $copied"
echo "Déjà présents   : $skipped"
