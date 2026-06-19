"""Tests package with Python 3.14 compatibility patches."""

# Monkey patch for anyio compatibility with Python 3.14 alpha
import sys

if sys.version_info >= (3, 14):
    import pathlib

    if not hasattr(pathlib, "types"):
        # Create fake pathlib.types for anyio compatibility
        class PathInfo:
            pass

        class Types:
            PathInfo = PathInfo

        pathlib.types = Types()  # type: ignore
