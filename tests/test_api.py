
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.database import Base, get_db


# Separate temporary database for automated tests
TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client():
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def sample_lead():
    return {
        "name": "Rahul Sharma",
        "email": "rahul@example.com",
        "phone": "9876543210",
        "company": "ABC Technologies",
        "requirement": (
            "AI-powered workflow automation "
            "for sales lead management."
        ),
        "budget": 150000,
        "source": "Website",
    }


def test_root_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200


def test_application_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_database_health(client):
    response = client.get("/api/health/database")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_lead(client, sample_lead):
    response = client.post(
        "/api/leads",
        json=sample_lead,
    )

    assert response.status_code == 201


def test_duplicate_lead(client, sample_lead):
    first_response = client.post(
        "/api/leads",
        json=sample_lead,
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/api/leads",
        json=sample_lead,
    )

    assert second_response.status_code == 409


def test_get_all_leads(client, sample_lead):
    client.post("/api/leads", json=sample_lead)

    response = client.get("/api/leads")

    assert response.status_code == 200
    assert "rahul@example.com" in str(response.json())


def test_get_specific_lead(client, sample_lead):
    create_response = client.post(
        "/api/leads",
        json=sample_lead,
    )

    assert create_response.status_code == 201

    created_data = create_response.json()
    lead_id = created_data.get("id") or created_data.get("lead_id")

    assert lead_id is not None

    response = client.get(f"/api/leads/{lead_id}")

    assert response.status_code == 200


def test_update_lead_status(client, sample_lead):
    create_response = client.post(
        "/api/leads",
        json=sample_lead,
    )

    assert create_response.status_code == 201

    created_data = create_response.json()
    lead_id = created_data.get("id") or created_data.get("lead_id")

    assert lead_id is not None

    response = client.patch(
        f"/api/leads/{lead_id}/status",
        json={"sales_status": "CONTACTED"},
    )

    assert response.status_code == 200
    assert "CONTACTED" in str(response.json())
