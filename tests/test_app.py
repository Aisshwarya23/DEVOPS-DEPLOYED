from app import app


def test_home():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200

    data = response.get_json()
    assert data["status"] == "success"


def test_health():
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200

    data = response.get_json()
    assert data["status"] == "healthy"


def test_about():
    client = app.test_client()
    response = client.get("/about")
    assert response.status_code == 200

    data = response.get_json()
    expected_project = "DEVOPS-DEPLOYED"
    assert data["project"] == expected_project


def test_metrics():
    client = app.test_client()
    response = client.get("/metrics")
    assert response.status_code == 200
    assert b"app_requests_total" in response.data
