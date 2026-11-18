from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.commons.db.base import Base


class PrekeyBundleSchema(Base):
    __tablename__ = "prekey_bundles"
    __table_args__ = (
        Index(
            "ix_prekey_bundles_active_user",
            "user_id",
            unique=True,
            postgresql_where=(func.coalesce(func.cast("is_active", Boolean), True) == True),
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    signed_prekey_pub: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    signature: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
