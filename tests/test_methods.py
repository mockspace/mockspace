import pytest

from mockspace.db import get_db


def test_index(client, auth):
    # redirect check for unauthorized user
    response = client.get("/test_service")
    assert b"Redirecting" in response.data

    # page check for authorized user
    auth.login()
    response = client.get("/test_service")
    assert b"Sign out" in response.data
    assert b"test" in response.data
    assert b"test_method" in response.data
    assert b'action="/test_service/test_method/update_method"' in response.data


@pytest.mark.parametrize("path", (
        "/create_method", "/test_service/test_method/update_method", "/test_service/test_method/delete_method"))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers["Location"] == "http://localhost/auth/login"


def test_author_required(app, client, auth):
    # change the service author to another user
    with app.app_context():
        db = get_db()
        db.execute("UPDATE method SET author_id = 2 WHERE id = 1")
        db.commit()

    auth.login()
    # current user can't modify other user's service
    assert client.post("/test_service/test_method/update_method").status_code == 403
    assert client.post("/test_service/test_method/delete_method").status_code == 403
    # current user doesn't see edit link
    assert b'href="/test_service/test_method/update_method"' not in client.get("/").data


@pytest.mark.parametrize("path", (
        "/non_existent_service/test_method/update_method", "/non_existent_service/test_method/delete_method"))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404


def test_create(client, auth, app):
    auth.login()
    assert client.get("/test_service/create_method").status_code == 200
    client.post("/test_service/create_method",
                data={"title": "created", "status_code": 200, "delay": 500, "supported_method": "GET", "body": "",
                      "headers": ""})

    with app.app_context():
        db = get_db()
        count = db.execute("SELECT COUNT(id) FROM method").fetchone()[0]
        assert count == 2


def test_update(client, auth, app):
    auth.login()
    assert client.get("/test_service/test_method/update_method").status_code == 200
    client.post("/test_service/test_method/update_method",
                data={"title": "updated", "status_code": 201, "delay": 100, "supported_method": "GET", "body": "",
                      "headers": ""})

    with app.app_context():
        db = get_db()
        method = db.execute("SELECT * FROM method WHERE id = 1").fetchone()
        assert method["title"] == "updated"


@pytest.mark.parametrize("path", ("/test_service/create_method", "/test_service/test_method/update_method"))
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path,
                           data={"title": "", "body": "", "status_code": 200, "delay": 500, "supported_method": "GET"})
    assert b"Title is required." in response.data


def test_delete(client, auth, app):
    auth.login()
    response = client.post("/test_service/test_method/delete_method")
    assert response.headers["Location"] == "http://localhost/test_service"

    with app.app_context():
        db = get_db()
        service = db.execute("SELECT * FROM method WHERE id = 1").fetchone()
        assert service is None


def test_method_response(client):
    response = client.get("/test_service/test_method")
    assert b'body' in response.data
    assert response.headers["Content-Type"] == "application/json"


def test_method_not_allowed_message(client):
    # send POST to "GET only" method
    response = client.post("/test_service/test_method", data={})
    assert b'POST is not allowed' in response.data
