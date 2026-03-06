# Multi-Platform Voice Agent (Finance, Ecommerce, Health)

This project is a reusable **AI voice-agent backend** that can be integrated into multiple domains:
- Finance
- Ecommerce
- Health

It models the workflow you described:
1. Caller dials a Twilio number.
2. AI checks whether caller already exists.
3. Existing users get contextual responses from prior records.
4. New users can be registered with basic details.
5. Dropped/unconnected calls are forwarded to CRM callback flow.
6. Appointments are scheduled and confirmed by SMS (with a Google Calendar-style event reference).

## Architecture

- **FastAPI service** exposes Twilio and business endpoints.
- **SQLite + SQLAlchemy** stores users and call logs.
- **Voice Orchestrator** coordinates:
  - STT (speech-to-text placeholder)
  - RAG-style contextual answer generator
  - TTS (text-to-speech placeholder)
  - CRM handoff for missed/dropped calls
  - Calendar + SMS appointment confirmation
- **n8n workflow JSON** included in `docs/n8n/workflow.json` for automation wiring.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn voice_agent.main:app --reload --app-dir src
```

Open docs at: `http://127.0.0.1:8000/docs`

## Main APIs

### 1) Twilio call webhook
`POST /webhooks/twilio/call?domain=finance|ecommerce|health|general`

Example payload:

```json
{
  "call_sid": "CA123456789",
  "from_number": "+14155550100",
  "call_status": "in-progress",
  "audio_text": "I want to check my recent order status"
}
```

### 2) Register new user
`POST /users/register`

### 3) Schedule appointment + SMS
`POST /appointments`

## n8n automation

Import `docs/n8n/workflow.json` into n8n and replace placeholders:
- Voice agent API URL
- CRM API URL
- Twilio webhook URL + credentials
- (Optional) real Google Calendar and SMS nodes

## Notes for production hardening

- Replace placeholder STT/TTS with real-time providers.
- Add vector database + retrieval for full RAG.
- Add auth, tenant isolation, retries, dead-letter queue.
- Encrypt PII and comply with HIPAA/PCI/GDPR as needed.
