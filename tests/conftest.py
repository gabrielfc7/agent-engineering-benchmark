"""Pytest fixtures for agent engineering benchmark."""

import pytest
from agent_benchmark.harness.suite import get_standard_engineering_suite


@pytest.fixture
def engineering_suite():
    return get_standard_engineering_suite()
