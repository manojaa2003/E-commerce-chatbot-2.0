def test_login_success(client, user):
    response = client.post(
        "/login",
        data={
            "username": user.email_id,
            "password": "CorrectPassword123!",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["token_type"] == "Bearer"
    assert isinstance(body["access_token"], str)
    assert body["access_token"]


def test_login_unknown_user(client):
    response = client.post(
        "/login",
        data={
            "username": "missing@example.com",
            "password": "anything",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Invalid credentials"


def test_login_wrong_password(client, user):
    response = client.post(
        "/login",
        data={
            "username": user.email_id,
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_delete_user_success(client, user, auth_headers, db):
    # Capture the ID BEFORE the API deletes the ORM object.
    user_id = user.id

    response = client.delete(
        "/delete_user",
        headers=auth_headers,
    )

    # Keep the existing API behavior unchanged.
    assert response.status_code == 200

    # Refresh the test session.
    db.expire_all()

    # Use the plain integer ID captured before deletion.
    deleted_user = (
        db.query(type(user))
        .filter(type(user).id == user_id)
        .first()
    )

    assert deleted_user is None


def test_delete_user_requires_authentication(client):
    response = client.delete("/delete_user")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_delete_user_invalid_token(client):
    response = client.delete(
        "/delete_user",
        headers={
            "Authorization": "Bearer invalid-token"
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "could not validate credentials"