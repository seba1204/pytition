"""Management command to update pytition installation from GitHub."""

import os
import subprocess
from functools import partial
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

run = partial(subprocess.run, shell=True, check=True)


# FIXME: this is a naive implementation, it should handle more edge cases
class Command(BaseCommand):
    """Update pytition install."""

    def handle(self, *args: object, **opts: object) -> None:
        """Update pytition installation from GitHub."""
        try:
            git_path = Path(settings.BASE_DIR).parent
            os.chdir(git_path)
            run("git checkout master -q && git pull -q ")

            version_cmd = (
                "curl -s "
                "https://api.github.com/repos/pytition/pytition/releases/latest"
                " | grep 'tag_name' | cut -d : -f2,3 | tr -d \\\" | tr -d ,"
            )
            version = run(version_cmd, capture_output=True).stdout.strip()

            checkout_cmd = f"git checkout {version} -q"
            run(checkout_cmd)

            run("pdm sync")

            os.chdir(settings.BASE_DIR)
            run("python3 manage.py migrate")
            run("python3 manage.py collectstatic --no-input")
            run("python3 manage.py compilemessages")
        except subprocess.CalledProcessError as e:
            print(e)
            if e.stdout is not None:
                print(f"stdout: {e.stdout}")
            if e.stderr is not None:
                print(f"stderr:{e.stderr}")
