from ecommerce_chatbot.backend_routes import models


def test_chat_requires_authentication(client):
    response = client.post("/chat", json={"query": "Show me Nike shoes"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_chat_success(client, db, user, auth_headers):
    response = client.post(
        "/chat",
        headers=auth_headers,
        json={"query": "Show me Nike shoes under 3000"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "response": "Test AI response for: Show me Nike shoes under 3000"
    }

    messages = (
        db.query(models.Message)
        .filter_by(user_id=user.id)
        .order_by(models.Message.id)
        .all()
    )
    assert len(messages) == 2
    assert messages[0].role == "human"
    assert messages[0].content == "Show me Nike shoes under 3000"
    assert messages[1].role == "ai"
    assert messages[1].content == "Test AI response for: Show me Nike shoes under 3000"


def test_chat_history_requires_authentication(client):
    response = client.get("/chat/history")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_chat_history_empty(client, user, auth_headers):
    response = client.get("/chat/history", headers=auth_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "No conversation yet!"


def test_chat_history_success(client, db, user, auth_headers):
    db.add_all(
        [
            models.Message(user_id=user.id, role="human", content="Hello"),
            models.Message(user_id=user.id, role="ai", content="Hi! How can I help?"),
        ]
    )
    db.commit()

    response = client.get("/chat/history", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert body[0]["role"] == "human"
    assert body[0]["content"] == "Hello"
    assert body[1]["role"] == "ai"
    assert body[1]["content"] == "Hi! How can I help?"
    assert all("id" in message for message in body)
    assert all("created_at" in message for message in body)


def test_chat_history_is_user_specific(client, db, user, auth_headers):
    other = models.Users(email_id="other@example.com", password="hashed")
    db.add(other)
    db.commit()
    db.refresh(other)

    db.add(models.Message(user_id=other.id, role="human", content="Private message"))
    db.commit()

    response = client.get("/chat/history", headers=auth_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "No conversation yet!"


def test_delete_chat_requires_authentication(client):
    response = client.delete("/chat/delete")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_delete_chat_empty(client, user, auth_headers):
    response = client.delete("/chat/delete", headers=auth_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "No conversation yet!"


def test_delete_chat_success(client, db, user, auth_headers):
    db.add_all(
        [
            models.Message(user_id=user.id, role="human", content="Hello"),
            models.Message(user_id=user.id, role="ai", content="Hi"),
        ]
    )
    db.commit()

    response = client.delete("/chat/delete", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == {"message": "conversation deleted successfully"}
    assert db.query(models.Message).filter_by(user_id=user.id).count() == 0
