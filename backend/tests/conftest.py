import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.main as main_module
from app.main import app
from app.config.settings import Settings, get_settings
from app.models.db import Base
from app.auth.deps import get_current_user
from app.models.user import User

# Setup in-memory database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(name="test_settings")
def fixture_test_settings():
    return Settings(
        app_env="test",
        gemini_api_key="test-api-key",
        db_url=TEST_DATABASE_URL,
        upload_dir="./test_uploads",
        chroma_persist_dir="./test_chroma_db",
    )


@pytest.fixture(name="test_db")
def fixture_test_db(test_settings):
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(name="client")
def fixture_client(test_settings, test_db):
    test_user = User(
        id="test-user-id",
        email="test@example.com",
        password_hash="test-password-hash",
        is_active=True,
        role="user",
    )

    # Override settings dependency
    app.dependency_overrides[get_settings] = lambda: test_settings
    app.dependency_overrides[get_current_user] = lambda: test_user
    main_module.settings = test_settings

    # Override app.state services with mock services if needed
    # (Here we can mock ChatService, EmbeddingService, etc. if we want)

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
