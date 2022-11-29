#!/usr/bin/env python
"""Django's command-line utility for administrative tasks.

The reason this file is relative imports' issues. The way I solved them
was packaging the whole project and importing things within it just like
with third party libraries. For this to work, the python interpreter needs
to be in the root folder.
"""

import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epic_events.epic_events.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
