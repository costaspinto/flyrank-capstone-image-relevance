from fastapi.testclient import TestClient
from app.main import app
def test_health():
    with TestClient(app) as client:
        response=client.get("/health")
        assert response.status_code==200 and response.json()["status"]=="ok"
def test_home_and_docs():
    with TestClient(app) as client:
        assert client.get("/").status_code==200
        assert client.get("/docs").status_code==200
