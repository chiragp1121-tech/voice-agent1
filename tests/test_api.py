from fastapi.testclient import TestClient

from voice_agent.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_register_and_existing_user_flow():
    reg = client.post(
        "/users/register",
        json={
            "phone_number": "+19998887777",
            "name": "Alex",
            "query": "Need mortgage support",
            "address": "123 Market St",
        },
    )
    assert reg.status_code == 200

    call = client.post(
        "/webhooks/twilio/call?domain=finance",
        json={
            "call_sid": "CA-existing-001",
            "from_number": "+19998887777",
            "call_status": "in-progress",
            "audio_text": "Can you explain my loan options?",
        },
    )
    body = call.json()
    assert call.status_code == 200
    assert body["user_type"] == "existing"
    assert "welcome back Alex" in body["response_text"]


def test_new_user_call_and_appointment():
    call = client.post(
        "/webhooks/twilio/call?domain=ecommerce",
        json={
            "call_sid": "CA-new-002",
            "from_number": "+18887776666",
            "call_status": "dropped",
            "audio_text": "I need help with a return",
        },
    )
    assert call.status_code == 200
    assert call.json()["user_type"] == "new"

    appointment = client.post(
        "/appointments",
        json={
            "phone_number": "+18887776666",
            "preferred_date": "2026-10-15",
            "preferred_time": "14:30",
            "purpose": "return support follow-up",
        },
    )
    assert appointment.status_code == 200
    assert appointment.json()["sms_sent"] is True
