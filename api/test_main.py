from fastapi.testclient import TestClient
from .main import app

client = TestClient(app)


def test_get_hello():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_get_index_html():
    response = client.get("/index.html")
    assert response.status_code == 200
    assert "<title>Family Recipes</title>" in response.text
