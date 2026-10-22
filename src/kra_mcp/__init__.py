"""MCP server for kra-mcp."""
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

try:  # the installed package version, so it cannot drift from pyproject
    __version__ = _pkg_version("kra-mcp")
except PackageNotFoundError:  # a source tree that was never installed
    __version__ = "0+unknown"