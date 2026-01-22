import sys
import pytest

# We are on macOS, so we can likely rely on system libraries for imports.
# Specific mocks will be handled in test files.

@pytest.fixture(autouse=True)
def setup_testing_environment():
    """
    Common setup if needed.
    """
    pass
