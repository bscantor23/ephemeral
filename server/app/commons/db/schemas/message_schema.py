from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Index, Integer, SmallInteger, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.commons.db.base import Base


class MessageSchema(Base):
    __tablename__ = "messages"
    __table_args__ = (
        Index(
            "ix_messages_undelivered_recipient",
            "recipient_id",
            "created_at",
            postgresql_where=(func.cast("delivered_at", DateTime(timezone=True)).is_(None)),
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    chat_session_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    sender_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    recipient_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    protocol_version: Mapped[int] = mapped_column(
        SmallInteger,
        default=1,
        nullable=False,
    )
    msg_num: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    ephemeral_pub: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    signed_prekey_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("prekey_bundles.id", ondelete="SET NULL"),
        nullable=True,
    )
    ciphertext: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    delivered_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
