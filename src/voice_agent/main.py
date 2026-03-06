from fastapi import Depends, FastAPI, Query
from sqlalchemy.orm import Session

from .database import SessionLocal, init_db
from .schemas import (
    AppointmentRequest,
    AppointmentResponse,
    CallResponse,
    TwilioCallWebhook,
    UserRegistration,
)
from .services import VoiceAgentOrchestrator

app = FastAPI(title="Multi-Platform Voice Agent")
orchestrator = VoiceAgentOrchestrator()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/webhooks/twilio/call", response_model=CallResponse)
def twilio_call_webhook(
    payload: TwilioCallWebhook,
    domain: str = Query("general", description="Target platform domain: finance/ecommerce/health/general"),
    db: Session = Depends(get_db),
):
    user_type, answer, crm_payload = orchestrator.process_call(
        db=db,
        call_sid=payload.call_sid,
        phone_number=payload.from_number,
        call_status=payload.call_status,
        audio_text=payload.audio_text,
        domain=domain,
    )
    _ = crm_payload
    return CallResponse(
        call_sid=payload.call_sid,
        user_type=user_type,
        transcript=answer.transcript,
        response_text=answer.response_text,
        tts_audio_stub=answer.tts_audio_stub,
    )


@app.post("/users/register")
def register_user(payload: UserRegistration, db: Session = Depends(get_db)) -> dict:
    user = orchestrator.register_new_user(
        db=db,
        phone_number=payload.phone_number,
        name=payload.name,
        query=payload.query,
        address=payload.address,
    )
    return {"id": user.id, "phone_number": user.phone_number, "name": user.name}


@app.post("/appointments", response_model=AppointmentResponse)
def schedule_appointment(payload: AppointmentRequest) -> AppointmentResponse:
    sms_sent, event_id, message = orchestrator.schedule_appointment(
        phone_number=payload.phone_number,
        preferred_date=payload.preferred_date,
        preferred_time=payload.preferred_time,
        purpose=payload.purpose,
    )
    return AppointmentResponse(sms_sent=sms_sent, calendar_event_id=event_id, message=message)
