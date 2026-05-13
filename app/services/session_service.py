from sqlalchemy.orm import Session

from app.db.repositories import SessionRepository


class SessionService:
    def __init__(self, db: Session):
        self.repository = SessionRepository(db)

    def load(self, session_id: str | None):
        session = self.repository.get_or_create(session_id)
        return session, self.repository.get_facts(session)

