from fastapi.testclient import TestClient
from main import app
import json

client = TestClient(app)

def test_endpoints():
    print("Testing /health")
    response = client.get("/health")
    assert response.status_code == 200
    print("Health check passed:", response.json())

    print("\nTesting /api/request")
    req_data = {
        "user_id": "user123",
        "query": "Schedule a meeting with my manager tomorrow."
    }
    response = client.post("/api/request", json=req_data)
    assert response.status_code == 200
    resp_json = response.json()
    print("Request passed:", resp_json)
    assert resp_json["intent"] == "Scheduling"

    print("\nTesting /api/memory (POST)")
    mem_data = {
        "user_id": "user123",
        "tier": "LTM",
        "content": "User prefers afternoon meetings.",
        "significance_score": 0.85
    }
    response = client.post("/api/memory", json=mem_data)
    assert response.status_code == 200
    print("Memory POST passed:", response.json())

    print("\nTesting /api/memory/{user_id} (GET)")
    response = client.get("/api/memory/user123")
    assert response.status_code == 200
    memories = response.json()
    print("Memory GET passed:", memories)
    assert len(memories) >= 2  # One from the request, one from manual POST

    print("\nTesting /api/audit (GET)")
    response = client.get("/api/audit")
    assert response.status_code == 200
    audits = response.json()
    print("Audit GET passed:", audits)
    assert len(audits) >= 1
    
    print("\nAll tests passed successfully!")

if __name__ == "__main__":
    test_endpoints()
