from fastapi.testclient import TestClient
from src.main import app 

client = TestClient(app)

# test for root "/" endpoint with JSON response
def test_read_root_json():
    response = client.get("/", headers={"Accept": "application/json"})
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

# test for root "/" endpoint with HTML response
def test_read_root_html():
    response = client.get("/", headers={"Accept": "text/html"})
    assert response.status_code == 200
    assert "<h1>Status: OK</h1>" in response.text

# test for ping "/ping" endpoint with JSON response
def test_ping_json():
    response = client.get("/ping", headers={"Accept": "application/json"})
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

# test for ping "/ping" endpoint with HTML response
def test_ping_html():
    response = client.get("/ping", headers={"Accept": "text/html"})
    assert response.status_code == 200
    assert "<h1>Status: OK</h1>" in response.text

# test for GET /simulate (should return an HTML page)
def test_get_simulate():
    response = client.get("/simulate")
    assert response.status_code == 200
    assert "<h1>Simulation Page</h1>" in response.text

# test for valid simulation (POST request)
def test_simulate_valid():
    response = client.post("/simulate", data={"shape": "square", "size": 10})
    assert response.status_code == 200
    assert response.json() == {"shape": "square", "size": 10, "result": 100}

# test for valid simulation with circle
def test_simulate_circle():
    response = client.post("/simulate", data={"shape": "circle", "size": 5})
    assert response.status_code == 200
    assert response.json()["shape"] == "circle"
    assert response.json()["size"] == 5
    assert response.json()["result"] == 3.14 * 5 * 5

# test for invalid shape
def test_simulate_invalid_shape():
    response = client.post("/simulate", data={"shape": "triangle", "size": 5})
    assert response.status_code == 200
    assert response.json()["shape"] == "triangle"
    assert response.json()["result"] == 0  # triangle is not supported

# test for missing parameters
def test_simulate_missing_parameters():
    response = client.post("/simulate", data={"shape": "square"})  # size missing
    assert response.status_code == 422  # fastAPI resolves error automaticly

