"""Pytest configuration and shared fixtures."""

import pytest


def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line("markers", "unit: mark test as a unit test")
