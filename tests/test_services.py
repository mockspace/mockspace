import pytest

from mockspace.db import get_db


def test_index(client, auth):
    # redirect check for unauthorized user
    response = client.get("/")
    assert b"Redirecting" in response.data

    # page check for authorized user
    auth.login()
    response = client.get("/")
    assert b"Sign out" in response.data
    assert b"test" in response.data
    assert b"test_service" in response.data
    assert b'action="/test_service/update"' in response.data


@pytest.mark.parametrize("path", ("/create", "/test_service/update", "/test_service/delete"))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers["Location"] == "http://localhost/auth/login"


def test_author_required(app, client, auth):
    # change the service author to another user
    with app.app_context():
        db = get_db()
        db.execute("UPDATE service SET author_id = 2 WHERE id = 1")
        db.commit()

    auth.login()
    # current user can't modify other user's service
    assert client.post("/test_service/update").status_code == 403
    assert client.post("/test_service/delete").status_code == 403
    # current user doesn't see edit link
    assert b'href="/test_service/update"' not in client.get("/").data


@pytest.mark.parametrize("path", ("/non_existent_service/update", "/non_existent_service/delete"))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404


def test_create(client, auth, app):
    auth.login()
    assert client.get("/create").status_code == 200
    client.post("/create", data={"title": "created", "body": ""})

    with app.app_context():
        db = get_db()
        count = db.execute("SELECT COUNT(id) FROM service").fetchone()[0]
        assert count == 2


def test_update(client, auth, app):
    auth.login()
    assert client.get("/test_service/update").status_code == 200
    client.post("/test_service/update", data={"title": "updated", "body": ""})

    with app.app_context():
        db = get_db()
        service = db.execute("SELECT * FROM service WHERE id = 1").fetchone()
        assert service["title"] == "updated"


@pytest.mark.parametrize("path", ("/create", "/test_service/update"))
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={"title": "", "body": ""})
    assert b"Title is required." in response.data


def test_delete(client, auth, app):
    auth.login()
    response = client.post("/test_service/delete")
    assert response.headers["Location"] == "http://localhost/"

    with app.app_context():
        db = get_db()
        service = db.execute("SELECT * FROM service WHERE id = 1").fetchone()
        assert service is None
