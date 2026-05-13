from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class QASession(Base):
    __tablename__ = "qa_sessions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    status: Mapped[str] = mapped_column(String(64), default="created")
    jurisdiction: Mapped[str] = mapped_column(String(64), default="china_mainland")
    legal_domain: Mapped[str] = mapped_column(String(64), default="unknown")
    region: Mapped[str | None] = mapped_column(String(128), nullable=True)
    accumulated_facts_json: Mapped[str] = mapped_column(Text, default="{}")
    final_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = relationship("ChatMessage", cascade="all, delete-orphan")
    traces = relationship("AgentTrace", cascade="all, delete-orphan")
    sources = relationship("LegalSourceModel", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("qa_sessions.id"), index=True)
    role: Mapped[str] = mapped_column(String(32))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AgentTrace(Base):
    __tablename__ = "agent_traces"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("qa_sessions.id"), index=True)
    agent_name: Mapped[str] = mapped_column(String(128))
    event_type: Mapped[str] = mapped_column(String(64))
    input_summary_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    output_summary_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class LegalSourceModel(Base):
    __tablename__ = "legal_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("qa_sessions.id"), index=True)
    title: Mapped[str] = mapped_column(String(512))
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str | None] = mapped_column(String(256), nullable=True)
    snippet: Mapped[str | None] = mapped_column(Text, nullable=True)
    quote_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    authority_level: Mapped[str] = mapped_column(String(32), default="unknown")
    effective_status: Mapped[str] = mapped_column(String(32), default="unknown")
    basis_type: Mapped[str] = mapped_column(String(64), default="unknown")
    relevance_score: Mapped[float] = mapped_column(Float, default=0.0)
    used_for: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

