#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path


def main():
    """Run administrative tasks."""
    # Determine the project root (where manage.py lives)
    ROOT_DIR = Path(__file__).resolve().parent
    SRC_DIR = ROOT_DIR / "src"

    # Add the src directory to the Python path so imports like
    # `from media_downloader import settings` work properly
    sys.path.insert(0, str(SRC_DIR))

    # Django settings module — remains the same
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "media_downloader.settings")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
