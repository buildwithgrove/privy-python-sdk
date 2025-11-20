"""Pytest configuration and shared fixtures."""

import pytest

# Try to enable pytest_httpx plugin if available
try:
    import pytest_httpx  # noqa: F401
    pytest_plugins = ["pytest_httpx"]
except ImportError:
    # pytest-httpx not installed, httpx_mock fixture will not be available
    pass
