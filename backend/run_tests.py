#!/usr/bin/env python
"""Test runner with Python 3.14 compatibility patches."""

import sys

# Apply patch before importing anything else
if sys.version_info >= (3, 14):
    import pathlib

    if not hasattr(pathlib, "types"):

        class PathInfo:
            pass

        class Types:
            PathInfo = PathInfo

        pathlib.types = Types()  # type: ignore

# Now import and run pytest
import pytest

if __name__ == "__main__":
    sys.exit(pytest.main())
