import os

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("API_PORT", "8000")
os.environ.setdefault("POSTGRES_DB", "ephemeral_test")
os.environ.setdefault("POSTGRES_USER", "ephemeral_test")
os.environ.setdefault("POSTGRES_PASSWORD", "test_insecure_local_only")
os.environ.setdefault("ENABLE_PURGE_WORKER", "false")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://ephemeral_test:test_insecure_local_only@localhost:5432/ephemeral_test",
)


def pytest_itemcollected(item):
    if item.obj and item.obj.__doc__:
        description = item.obj.__doc__.strip().split("\n")[0].lstrip("↳ ").strip()
        item._nodeid = f"{item.nodeid}\n    ↳ {description}"
