from app.commons.config.settings import Settings, get_settings


def test_effective_database_url_constructed_when_none():
    """
    ↳ Settings: construye URL con credenciales si DATABASE_URL es None
    """
    s = Settings(
        APP_ENV="test",
        API_PORT=8000,
        POSTGRES_DB="ephemeral_db",
        POSTGRES_USER="user",
        POSTGRES_PASSWORD="secretpassword",
        POSTGRES_PORT=5432,
        DATABASE_URL=None,
        ENABLE_PURGE_WORKER=True,
    )
    assert s.effective_database_url == "postgresql+psycopg://user:secretpassword@db:5432/ephemeral_db"
    assert s.ENABLE_PURGE_WORKER is True


def test_effective_database_url_returns_provided_url():
    """
    ↳ Settings: respeta DATABASE_URL explicita si se suministra
    """
    url = "postgresql+psycopg://custom:secret@db.host:5432/custom_db"
    s = Settings(
        APP_ENV="test",
        API_PORT=8000,
        POSTGRES_DB="ephemeral_db",
        POSTGRES_USER="user",
        POSTGRES_PASSWORD="password",
        DATABASE_URL=url,
        ENABLE_PURGE_WORKER=False,
    )
    assert s.effective_database_url == url
    assert s.ENABLE_PURGE_WORKER is False


def test_get_settings_cached_instance():
    """
    ↳ Settings: get_settings retorna instancia cacheada via lru_cache
    """
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2
    assert s1.MESSAGE_RETENTION_MINUTES == 60
    assert s1.PURGE_INTERVAL_SECONDS == 1800
