from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.core.database import get_db, Base
import pytest

# Setup SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_session():
    response = client.post("/api/v1/sessions/", json={"title": "Test Session"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Session"
    assert "id" in data

def test_get_sessions():
    client.post("/api/v1/sessions/", json={"title": "Session 1"})
    response = client.get("/api/v1/sessions/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["title"] == "Session 1"

def test_get_session_not_found():
    response = client.get("/api/v1/sessions/non-existent-id")
    assert response.status_code == 404

def test_create_message(monkeypatch):
    # First create a session
    resp1 = client.post("/api/v1/sessions/", json={"title": "Session for message"})
    session_id = resp1.json()["id"]

    # Mock provider generate
    from app.services.agent import LLMProvider
    def mock_generate(self, messages, system_prompt=""):
        return "This is a mocked response."
    monkeypatch.setattr(LLMProvider, "generate", mock_generate)
    
    # Mock retrieval to avoid DB issues
    import app.services.agent
    app.services.agent.search_transcripts = lambda q, db, limit=5: []

    # Create message
    resp2 = client.post(f"/api/v1/sessions/{session_id}/messages", json={
        "role": "user",
        "content": "Hello, world!",
        "provider": "ollama"
    })
    assert resp2.status_code == 200
    msg = resp2.json()
    assert msg["role"] == "assistant"
    assert msg["content"] == "This is a mocked response."
    assert msg["session_id"] == session_id

    # Check if session returns messages
    resp3 = client.get(f"/api/v1/sessions/{session_id}")
    assert len(resp3.json()["messages"]) == 2 # 1 user, 1 assistant

def test_ship30_skill(monkeypatch):
    resp1 = client.post("/api/v1/sessions/", json={"title": "Session for ship30"})
    session_id = resp1.json()["id"]

    from app.services.agent import LLMProvider
    def mock_generate(self, messages, system_prompt=""):
        assert "SHIP 30 FOR 30 SKILL ACTIVATED" in system_prompt
        return "```artifact\n# Mock Essay\nThis is a 1250 word essay.\n```"
    monkeypatch.setattr(LLMProvider, "generate", mock_generate)
    
    import app.services.agent
    app.services.agent.search_transcripts = lambda q, db, limit=5: []

    resp2 = client.post(f"/api/v1/sessions/{session_id}/messages", json={
        "role": "user",
        "content": "Write an essay about growth.",
        "provider": "ollama",
        "skill": "ship30"
    })
    
    assert resp2.status_code == 200
    msg = resp2.json()
    assert "artifact" in msg["content"]

