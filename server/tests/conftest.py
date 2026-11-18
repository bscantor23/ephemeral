import os

os.environ["APP_ENV"] = "test"
os.environ["API_PORT"] = "8000"
os.environ["POSTGRES_DB"] = "ephemeral_test"
os.environ["POSTGRES_USER"] = "ephemeral_test"
os.environ["POSTGRES_PASSWORD"] = "test_password"
os.environ["DATABASE_URL"] = "postgresql+psycopg://test:test@localhost:5432/ephemeral_test"


def pytest_itemcollected(item):
    if item.obj and item.obj.__doc__:
        description = item.obj.__doc__.strip().split("\n")[0]
        item._nodeid = f"{item.nodeid}\n    ↳ {description}"
