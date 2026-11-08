"""Makes `python -m password_core` run the CLI."""

import sys

from .cli import main

sys.exit(main())
