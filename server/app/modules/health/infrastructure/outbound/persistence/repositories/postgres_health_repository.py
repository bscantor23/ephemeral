from collections.abc import Generator

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.commons.db.session import get_db_session
from app.modules.health.domain.ports.health_repository_port import (
    HealthRepositoryPort,
)


class PostgresHealthRepository(HealthRepositoryPort):
    def __init__(self, session_factory: Generator[Session, None, None] = get_db_session) -> None:
        self._session_factory = session_factory

    def is_database_connected(self) -> bool:
        session_gen = self._session_factory()
        session: Session = next(session_gen)
        try:
            session.execute(text("SELECT 1"))
            return True
        except SQLAlchemyError:
            return False
        finally:
            try:
                next(session_gen)
            except StopIteration:
                pass


DatabaseHealthRepository = PostgresHealthRepository
