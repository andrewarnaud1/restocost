"""Pytest plugin for Python 3.14 compatibility."""

import sys


def pytest_configure(config):
    """Apply Python 3.14 compatibility patches before test collection."""
    if sys.version_info >= (3, 14):
        import pathlib

        if not hasattr(pathlib, "types"):

            class PathInfo:  # noqa
                pass

            class Types:  # noqa
                PathInfo = PathInfo

            pathlib.types = Types()  # type: ignore
