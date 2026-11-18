from unittest.mock import MagicMock, patch

from app.commons.db.session import get_db_session


def test_get_db_session_yields_and_closes():
    """Sesión BD: get_db_session entrega sesión y la cierra en finally"""
    mock_session = MagicMock()

    with patch("app.commons.db.session.SessionLocal", return_value=mock_session):
        gen = get_db_session()
        session = next(gen)

        assert session == mock_session

        try:
            next(gen)
        except StopIteration:
            pass

        mock_session.close.assert_called_once()
