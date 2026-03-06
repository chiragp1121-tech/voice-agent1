from pydantic import BaseModel, Field


class TwilioCallWebhook(BaseModel):
    call_sid: str = Field(..., description="Twilio Call SID")
    from_number: str = Field(..., description="Caller phone number")
    call_status: str = Field(..., description="Twilio call status")
    audio_text: str | None = Field(None, description="Optional already-transcribed utterance")


class CallResponse(BaseModel):
    call_sid: str
    user_type: str
    transcript: str
    response_text: str
    tts_audio_stub: str


class UserRegistration(BaseModel):
    phone_number: str
    name: str
    query: str
    address: str | None = None


class AppointmentRequest(BaseModel):
    phone_number: str
    preferred_date: str
    preferred_time: str
    purpose: str


class AppointmentResponse(BaseModel):
    sms_sent: bool
    calendar_event_id: str
    message: str
