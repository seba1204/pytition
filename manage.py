#!/usr/bin/env python
import os, sys
from pathlib import Path

# Optionnel: charge .env en dev/local
try:
    from dotenv import load_dotenv  # pip install python-dotenv
    load_dotenv(dotenv_path=Path(".env"), override=False)
except Exception:
    pass  # en prod, on peut s'appuyer sur de vraies vars d'env

os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                      os.getenv("DJANGO_SETTINGS_MODULE", "config.settings"))

# Si tu utilises le src layout sans installer le paquet en dev
sys.path.insert(0, os.getenv("PYTHONPATH", "src"))

from django.core.management import execute_from_command_line
execute_from_command_line(sys.argv)
