from sqlalchemy.orm import Session

from app.db.repositories import SessionRepository


class TraceService:
    def __init__(self, db: Session):
        self.repository = SessionRepository(db)

    def save(self, session_id: str, agent_name: str, event_type: str, input_summary=None, output_summary=None):
        self.repository.add_trace(session_id, agent_name, event_type, input_summary, output_summary)

