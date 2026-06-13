"""
Backward-compatible CLI entry point.

This module provides backward compatibility with the original monolithic
lsystem.py file. For new code, use the lsystem_renderer package instead.
"""

from lsystem_renderer.cli import main

if __name__ == "__main__":
    main()