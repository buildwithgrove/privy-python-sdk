"""Pytest configuration and shared fixtures."""

import pytest


@pytest.fixture
def httpx_mock(request):
    """Fixture for mocking httpx requests.

    This requires pytest-httpx to be installed.
    Install with: pip install pytest-httpx
    """
    try:
        from pytest_httpx import HTTPXMock
    except ImportError:
        pytest.skip("pytest-httpx not installed")

    return HTTPXMock()
