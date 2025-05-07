# tests/test_main.py
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

# Simulation: square shape, zero steps => initial density mask

def test_simulate_square_initial():
    payload = {
        "shape": "square",
        "size": 4,
        "height": 4,
        "dt": 0.1,
        "steps": 0,
        "fluid_type": "water",
        "env_type": "bounded"
    }
    expected = [
        [0.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 1.0, 0.0],
        [0.0, 1.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 0.0]
    ]
    response = client.post("/simulate", json=payload)
    assert response.status_code == 200
    assert response.json()["density"] == expected

# Invalid shape should return HTTP 400

def test_simulate_invalid_shape():
    payload = {
        "shape": "pentagon",
        "size": 4,
        "height": 4,
        "dt": 0.1,
        "steps": 0,
        "fluid_type": "water",
        "env_type": "bounded"
    }
    response = client.post("/simulate", json=payload)
    assert response.status_code == 400
    assert "Unknown shape" in response.json()["detail"]

# Missing required field should return HTTP 422

def test_simulate_missing_size():
    payload = {
        "shape": "square",
        "height": 4,
        "dt": 0.1,
        "steps": 0,
        "fluid_type": "water",
        "env_type": "bounded"
    }
    response = client.post("/simulate", json=payload)
    assert response.status_code == 422

# Custom shape initialization

def test_simulate_custom_shape():
    mask = [
        [0, 1, 0],
        [1, 1, 1],
        [0, 1, 0]
    ]
    payload = {
        "shape": "custom",
        "custom_shape": mask,
        "size": 3,
        "height": 3,
        "dt": 0.1,
        "steps": 0,
        "fluid_type": "water",
        "env_type": "bounded"
    }
    response = client.post("/simulate", json=payload)
    assert response.status_code == 200
    assert response.json()["density"] == mask
