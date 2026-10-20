"""Allow `python3 -m engines.baq` execution."""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
