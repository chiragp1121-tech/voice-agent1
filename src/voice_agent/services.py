from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import CallLog, User


@dataclass
class AgentAnswer:
    transcript: str
    response_text: str
    tts_audio_stub: str


class SpeechToTextService:
    def transcribe(self, audio_text: str | None) -> str:
        if audio_text:
            return audio_text
        return "Hello, I need help with my account and a follow-up appointment."


class RagService:
    def contextual_answer(self, user: User | None, query: str, domain: str = "general") -> str:
        prefix = {
            "finance": "For your finance request",
            "ecommerce": "For your ecommerce request",
            "health": "For your health request",
        }.get(domain, "For your request")

        if user:
            return (
                f"{prefix}, welcome back {user.name}. Based on your previous issue "
                f"('{user.query_summary or 'no previous summary'}'), here is the next best action: {query}."
            )
        return (
            f"{prefix}, thanks for contacting us. I'll capture your details and route your query: {query}."
        )


class TextToSpeechService:
    def synthesize(self, text: str) -> str:
        return f"audio://generated/{abs(hash(text)) % 100000}"


class CRMService:
    def notify_missed_or_dropped(self, call_sid: str, phone_number: str, status: str) -> dict:
        return {
            "crm_ticket": f"CRM-{call_sid[-6:]}",
            "phone_number": phone_number,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
        }


class CalendarService:
    def create_event(self, phone_number: str, date: str, time: str, purpose: str) -> str:
        return f"gcal-{phone_number[-4:]}-{date.replace('-', '')}-{time.replace(':', '')}"


class SmsService:
    def send(self, phone_number: str, message: str) -> bool:
        return True


class VoiceAgentOrchestrator:
    def __init__(self) -> None:
        self.stt = SpeechToTextService()
        self.rag = RagService()
        self.tts = TextToSpeechService()
        self.crm = CRMService()
        self.calendar = CalendarService()
        self.sms = SmsService()

    def process_call(
        self,
        db: Session,
        call_sid: str,
        phone_number: str,
        call_status: str,
        audio_text: str | None,
        domain: str,
    ) -> tuple[str, AgentAnswer, dict | None]:
        user = db.scalar(select(User).where(User.phone_number == phone_number))
        user_type = "existing" if user else "new"
        transcript = self.stt.transcribe(audio_text)
        response_text = self.rag.contextual_answer(user=user, query=transcript, domain=domain)
        tts_audio_stub = self.tts.synthesize(response_text)

        call_log = CallLog(
            call_sid=call_sid,
            phone_number=phone_number,
            status=call_status,
            transcript=transcript,
            response_text=response_text,
            user_id=user.id if user else None,
        )
        db.add(call_log)

        crm_payload = None
        if call_status in {"no-answer", "busy", "failed", "dropped"}:
            crm_payload = self.crm.notify_missed_or_dropped(call_sid, phone_number, call_status)

        db.commit()

        return user_type, AgentAnswer(transcript, response_text, tts_audio_stub), crm_payload

    def register_new_user(self, db: Session, phone_number: str, name: str, query: str, address: str | None) -> User:
        user = User(phone_number=phone_number, name=name, query_summary=query, address=address)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def schedule_appointment(
        self,
        phone_number: str,
        preferred_date: str,
        preferred_time: str,
        purpose: str,
    ) -> tuple[bool, str, str]:
        event_id = self.calendar.create_event(phone_number, preferred_date, preferred_time, purpose)
        message = (
            f"Your appointment is scheduled on {preferred_date} at {preferred_time} for {purpose}. "
            f"Reference: {event_id}"
        )
        sms_sent = self.sms.send(phone_number, message)
        return sms_sent, event_id, message
