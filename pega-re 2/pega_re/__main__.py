"""
__main__.py — Entry point for running PegaRE as a module.

This allows users to run: python -m pega_re.auto_dispatcher "analyze my application"
"""
from .auto_dispatcher import main

if __name__ == "__main__":
    exit(main())
