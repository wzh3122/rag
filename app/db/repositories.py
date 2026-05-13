import json
import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.api.schemas import LegalSource
from app.config import get_settings
from app.db.models import AgentTrace, ChatMessage, LegalSourceModel, QASession
from app.utils.security import sanitize_payload


class SessionRepository:
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()

    def get_or_create(self, session_id: str | None) -> QASession:
        if session_id:
            existing = self.db.get(QASession, session_id)
            if existing:
                return existing
        session = QASession(id=session_id or uuid.uuid4().hex)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_facts(self, session: QASession) -> dict[str, Any]:
        try:
            return json.loads(session.accumulated_facts_json or "{}")
        except json.JSONDecodeError:
            return {}

    def update_session(
        self,
        session: QASession,
        *,
        status: str,
        legal_domain: str,
        region: str | None,
        facts: dict[str, Any],
        final_answer: str = "",
        retry_count: int = 0,
    ) -> None:
        session.status = status
        session.legal_domain = legal_domain
        session.region = region
        session.accumulated_facts_json = json.dumps(facts, ensure_ascii=False)
        session.final_answer = final_answer
        session.retry_count = retry_count
        self.db.add(session)
        self.db.commit()

    def add_message(self, session_id: str, role: str, content: str) -> None:
        if not self.settings.should_save_chat_history:
            return
        self.db.add(ChatMessage(session_id=session_id, role=role, content=content))
        self.db.commit()

    def add_trace(
        self,
        session_id: str,
        agent_name: str,
        event_type: str,
        input_summary: Any = None,
        output_summary: Any = None,
        error_message: str | None = None,
    ) -> None:
        if not self.settings.enable_agent_trace:
            return
        self.db.add(
            AgentTrace(
                session_id=session_id,
                agent_name=agent_name,
                event_type=event_type,
                input_summary_json=json.dumps(
                    sanitize_payload(input_summary, self.settings.trace_max_text_length),
                    ensure_ascii=False,
                )
                if input_summary is not None
                else None,
                output_summary_json=json.dumps(
                    sanitize_payload(output_summary, self.settings.trace_max_text_length),
                    ensure_ascii=False,
                )
                if output_summary is not None
                else None,
                error_message=error_message,
            )
        )
        self.db.commit()

    def replace_sources(self, session_id: str, sources: list[LegalSource]) -> None:
        self.db.query(LegalSourceModel).filter(LegalSourceModel.session_id == session_id).delete()
        for source in sources:
            self.db.add(LegalSourceModel(session_id=session_id, **source.model_dump()))
        self.db.commit()

