#!/usr/bin/env python
import os
import sys
from pathlib import Path

# Optional: load .env in dev/local
try:
    from dotenv import load_dotenv  # pdm add python-dotenv

    load_dotenv(dotenv_path=Path(".env"), override=False)
except Exception:
    pass  # In production, real environment variables can be used.

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", os.getenv("DJANGO_SETTINGS_MODULE", "config.settings")
)

# If you use the src layout without installing the package in dev
sys.path.insert(0, os.getenv("PYTHONPATH", "src"))

from django.core.management import execute_from_command_line

execute_from_command_line(sys.argv)
