from datetime import datetime, timedelta, timezone

from ecommerce_chatbot.backend_routes import models, utils

def test_create_user_replaces_existing_pending_registration(
    client,
    db,
    pending_user,
    monkeypatch,
):
    old_pending, old_otp = pending_user
    pending_email = old_pending.email_id
    old_pending_id = old_pending.id

    sent = {}

    monkeypatch.setattr(
        utils,
        "send_otp_email",
        lambda email, otp: sent.update(
            email=email,
            otp=otp,
        ),
    )

    response = client.post(
        "/users",
        json={
            "email_id": pending_email,
            "password": "NewPassword123!",
        },
    )

    assert response.status_code == 200

    db.expire_all()

    pending_rows = (
        db.query(models.PendingUser)
        .filter_by(email_id=pending_email)
        .all()
    )

    assert len(pending_rows) == 1

    updated_pending = pending_rows[0]

    assert updated_pending.id != old_pending_id

    assert utils.verify(
        "NewPassword123!",
        updated_pending.password,
    )