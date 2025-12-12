import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="module")
def test_app():
    # Use TestClient for synchronous testing of the FastAPI app
    # This allows us to use simple def test_something(): ...
    with TestClient(app) as client:
        yield client
