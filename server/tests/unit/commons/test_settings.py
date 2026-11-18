from app.commons.config.settings import Settings


def test_effective_database_url_constructed_when_none():
    """Settings: construye URL con credenciales si DATABASE_URL es None"""
    settings = Settings(
        APP_ENV="test",
        API_PORT=8000,
        POSTGRES_DB="testdb",
        POSTGRES_USER="testuser",
        POSTGRES_PASSWORD="testpass",
        POSTGRES_PORT=5432,
        DATABASE_URL=None,
    )
    assert settings.effective_database_url == "postgresql+psycopg://testuser:testpass@db:5432/testdb"


def test_effective_database_url_returns_provided_url():
    """Settings: respeta DATABASE_URL explicita si se suministra"""
    settings = Settings(
        APP_ENV="test",
        API_PORT=8000,
        POSTGRES_DB="testdb",
        POSTGRES_USER="testuser",
        POSTGRES_PASSWORD="testpass",
        POSTGRES_PORT=5432,
        DATABASE_URL="postgresql+psycopg://custom:url@localhost:5432/customdb",
    )
    assert settings.effective_database_url == "postgresql+psycopg://custom:url@localhost:5432/customdb"
