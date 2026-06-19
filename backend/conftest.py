"""Root conftest for Python 3.14 compatibility."""

import sys

# Monkey patch for anyio compatibility with Python 3.14 alpha
if sys.version_info >= (3, 14):
    import pathlib

    if not hasattr(pathlib, "types"):

        class PathInfo:  # noqa
            pass

        class Types:  # noqa
            PathInfo = PathInfo

        pathlib.types = Types()  # type: ignore
