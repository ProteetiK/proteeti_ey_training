import sys
from pathlib import Path

import pytest

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app


@pytest.fixture
def client():
    app = create_app()

    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client