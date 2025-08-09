from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.user import UserORM
from app.services.user_service import sync_user_from_clerk_webhook
from app.db.session import Base


def test_sync_user_from_clerk_webhook_upsert():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    payload = {
        "data": {
            "id": "user_123",
            "email_addresses": [{"email_address": "user@example.com"}],
            "full_name": "User",
            "image_url": "http://example.com/a.png",
        }
    }
    user = sync_user_from_clerk_webhook(db, payload)
    assert user.email == "user@example.com"
    # Update email
    payload["data"]["email_addresses"][0]["email_address"] = "new@example.com"
    user2 = sync_user_from_clerk_webhook(db, payload)
    assert user2.email == "new@example.com"
    assert db.query(UserORM).count() == 1
    db.close()
