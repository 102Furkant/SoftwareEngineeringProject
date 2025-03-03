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

# Basic shape tests
def test_simulate_square():
    response = client.post("/simulate", data={"shape": "square", "size": 10})
    assert response.status_code == 200
    assert response.json() == {"shape": "square", "size": 10, "height": None, "result": 100}

def test_simulate_circle():
    response = client.post("/simulate", data={"shape": "circle", "size": 5})
    assert response.status_code == 200
    assert response.json() == {"shape": "circle", "size": 5, "height": None, "result": 78.5}

def test_simulate_triangle():
    response = client.post("/simulate", data={"shape": "triangle", "size": 3, "height": 4})
    assert response.status_code == 200
    assert response.json() == {"shape": "triangle", "size": 3, "height": 4, "result": 6}

# Edge cases and error handling
def test_simulate_negative_values():
    response = client.post("/simulate", data={"shape": "square", "size": -5})
    assert response.status_code == 200
    assert response.json()["result"] == "Size cannot be negative"

def test_simulate_zero_values():
    response = client.post("/simulate", data={"shape": "square", "size": 0})
    assert response.status_code == 200
    assert response.json()["result"] == 0

def test_simulate_triangle_without_height():
    response = client.post("/simulate", data={"shape": "triangle", "size": 3})
    assert response.status_code == 200
    assert response.json()["result"] == "height is required for triangle"

def test_simulate_square_with_height():
    response = client.post("/simulate", data={"shape": "square", "size": 5, "height": 10})
    assert response.status_code == 200
    assert response.json()["result"] == 25

def test_simulate_circle_with_height():
    response = client.post("/simulate", data={"shape": "circle", "size": 5, "height": 10})
    assert response.status_code == 200
    assert response.json()["result"] == 78.5

# Invalid input tests
def test_simulate_invalid_shape():
    response = client.post("/simulate", data={"shape": "pentagon", "size": 5})
    assert response.status_code == 200
    assert response.json()["result"] == "Unsupported shape: pentagon"

def test_simulate_missing_size():
    response = client.post("/simulate", data={"shape": "square"})
    assert response.status_code == 422

def test_simulate_case_insensitive():
    response = client.post("/simulate", data={"shape": "SQUARE", "size": 5})
    assert response.status_code == 200
    assert response.json()["result"] == 25

# String validation
def test_simulate_non_numeric_size():
    response = client.post("/simulate", data={"shape": "square", "size": "abc"})
    assert response.status_code == 422
