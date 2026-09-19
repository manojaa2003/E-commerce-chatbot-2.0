import os
import sys
import types

os.environ["DATABASE_HOSTNAME"] = "localhost"
os.environ["DATABASE_PORT"] = "5433"
os.environ["DATABASE_PASSWORD"] = "manu@123"
os.environ["DATABASE_NAME"] = "E_commerce_test_db"
os.environ["DATABASE_USERNAME"] = "postgres"

os.environ.setdefault(
    "SECRET_KEY",
    "test-secret-key-for-pytest-only"
)

os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault(
    "ACCESS_TOKEN_EXPIRE_MINUTES",
    "30"
)

class _DummyChatbot:

    def invoke(self, state):
        query = state["messages"][-1].content

        return {
            "messages": [
                types.SimpleNamespace(
                    content=f"Test AI response for: {query}"
                )
            ]
        }


_fake_orchestration = types.ModuleType(
    "ecommerce_chatbot.Orchestration.Orchestration"
)

_fake_orchestration.app = _DummyChatbot()

sys.modules[_fake_orchestration.__name__] = _fake_orchestration

from ecommerce_chatbot.backend_routes.main import fast_app
from ecommerce_chatbot.backend_routes import database, models
from ecommerce_chatbot.backend_routes.Oauth2 import create_access_token

from fastapi.testclient import TestClient

import pytest

def _override_get_db():

    db = database.Sesssionlocal()

    try:
        yield db

    finally:
        db.close()


fast_app.dependency_overrides[database.get_db] = _override_get_db

@pytest.fixture(scope="session", autouse=True)
def create_test_schema():

    models.Base.metadata.create_all(
        bind=database.engine
    )

    yield

    models.Base.metadata.drop_all(
        bind=database.engine
    )

@pytest.fixture(autouse=True)
def clean_database():

    db = database.Sesssionlocal()

    try:

        db.query(models.Message).delete(
            synchronize_session=False
        )

        db.query(models.PasswordResetOTP).delete(
            synchronize_session=False
        )

        db.query(models.PendingUser).delete(
            synchronize_session=False
        )

        db.query(models.Users).delete(
            synchronize_session=False
        )

        db.commit()

    finally:

        db.close()

@pytest.fixture
def client():

    with TestClient(fast_app) as test_client:
        yield test_client

@pytest.fixture
def db():

    session = database.Sesssionlocal()

    try:
        yield session

    finally:
        session.close()

@pytest.fixture
def user(db):

    from ecommerce_chatbot.backend_routes import utils

    item = models.Users(
        email_id="user@example.com",
        password=utils.hash("CorrectPassword123!"),
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return item

@pytest.fixture
def auth_headers(user):

    token = create_access_token(
        {"user_id": user.id}
    )

    return {
        "Authorization": f"Bearer {token}"
    }

@pytest.fixture
def pending_user(db):

    from datetime import datetime, timedelta, timezone
    from ecommerce_chatbot.backend_routes import utils

    otp = "123456"

    item = models.PendingUser(
        email_id="pending@example.com",
        password=utils.hash("PendingPassword123!"),
        otp_hash=utils.hash(otp),
        expires_at=(
            datetime.now(timezone.utc)
            + timedelta(minutes=5)
        ),
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return item, otp

@pytest.fixture
def password_reset_otp(db, user):

    from datetime import datetime, timedelta, timezone
    from ecommerce_chatbot.backend_routes import utils

    otp = "654321"

    item = models.PasswordResetOTP(
        email_id=user.email_id,
        otp_hash=utils.hash(otp),
        expires_at=(
            datetime.now(timezone.utc)
            + timedelta(minutes=5)
        ),
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return item, otp