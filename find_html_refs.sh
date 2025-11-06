#!/usr/bin/env bash
# Description: Find all .py files (excluding test files) containing ".html" not preceded by "_bs5"
# and display the matching lines with line numbers.

set -euo pipefail

find ./src/apps -type f -name "*.py" ! -name "*test*" | while read -r file; do
    # Search for .html not preceded by '_' and exclude _bs5.html
    matches=$(grep -nE '[^_]\.html' "$file" | grep -v "_bs5\.html" || true)
    if [[ -n "$matches" ]]; then
        echo "=== $file ==="
        echo "$matches"
        echo
    fi
done
