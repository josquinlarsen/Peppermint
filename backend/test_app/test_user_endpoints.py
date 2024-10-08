import pytest
from fastapi.testclient import TestClient
from main import app
import json
from domain.user.user_crud import get_user_by_username, get_user_by_id
from database import SessionLocal

client_401 = TestClient(app)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_user():
    return {"username": "testuser", "password": "testpassword"}


@pytest.fixture
def test_user2():
    return {"username": "testuser2", "password": "testpassword2"}


def test_user_register(client):
    """
    User registration endpoint test
    """
    data = {
        "username": "testuser",
        "password1": "testpassword",
        "password2": "testpassword",
        "first_name": "TEST",
        "last_name": "USER",
        "email": "testuser@testuser.com",
    }
    response = client.post("/peppermint/user/register", json=data)
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["username"] == "testuser"
    assert response.json()["first_name"] == "TEST"
    assert response.json()["last_name"] == "USER"
    assert response.json()["email"] == "testuser@testuser.com"


def test_user_duplicate_username_register(client):
    """
    User duplicate registration endpoint test
    """
    data = {
        "username": "testuser",
        "password1": "testpassword",
        "password2": "testpassword",
        "first_name": "TEST",
        "last_name": "USER",
        "email": "testuser1@testuser.com",
    }
    response = client.post("/peppermint/user/register", json=data)
    assert response.status_code == 409


def test_user_duplicate_email_register(client):
    """
    User duplicate registration endpoint test
    """
    data = {
        "username": "testuser1",
        "password1": "testpassword",
        "password2": "testpassword",
        "first_name": "TEST",
        "last_name": "USER",
        "email": "testuser@testuser.com",
    }
    response = client.post("/peppermint/user/register", json=data)
    assert response.status_code == 409


def test_testuser_login_incorrect_username(client):
    """
    Login test with incorrect username
    """
    test_user = {
        "username": "testuser1",
        "password": "testpassword",
    }
    response = client.post("/peppermint/user/login", data=test_user)
    assert response.status_code == 401


def test_testuser_login_incorrect_password(client):
    """
    Login test with incorrect username
    """
    test_user = {
        "username": "testuser",
        "password": "testpassword1",
    }
    response = client.post("/peppermint/user/login", data=test_user)
    assert response.status_code == 401


def test_testuser_login(client, test_user):
    """
    Login test
    """
    response = client.post("/peppermint/user/login", data=test_user)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()
    assert "username" in response.json()

    return response.json()["access_token"]


def test_testuser_get(client, test_user):
    """
    GET /user/ test
    """
    login_response = client.post("/peppermint/user/login", data=test_user)
    access_token = login_response.json()["access_token"]
    response = client.get(
        "/peppermint/user/", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
    assert "password" not in response.json()


def test_get_user_all(client):
    """
    Test return all users endpoint
    """
    data01 = {
        "username": "testu1",
        "password1": "testpassword",
        "password2": "testpassword",
        "first_name": "TEST",
        "last_name": "USER",
        "email": "test1@testuser.com",
    }
    data02 = {
        "username": "testu2",
        "password1": "testpassword2",
        "password2": "testpassword2",
        "first_name": "TEST",
        "last_name": "USER2",
        "email": "test2@testuser.com",
    }

    client.post("/peppermint/user/register", json=data01)
    client.post("/peppermint/user/register", json=data02)

    temp_user01 = {
        "username": "testu1",
        "password": "testpassword",
    }

    # get token
    login_response = client.post(
        "/peppermint/user/login",
        data=temp_user01,
    )
    access_token = login_response.json()["access_token"]
    response = client.get(
        "/peppermint/user/",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )
    # authorized needs token headers
    user_all_response = client.get(
        "/peppermint/user/all/",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )
    assert response.status_code == 200
    assert user_all_response.status_code == 200
    # convert binary json into readable json
    user_all_response_json = json.loads(user_all_response._content)
    assert len(user_all_response_json) == 3


def test_user_update(client, test_user):
    """
    Test user update endpoint
    """
    access_token = test_testuser_login(client, test_user)
    update_data = {
        "username": "testuser",
        "password1": "testpassword",
        "password2": "testpassword",
        "first_name": "UPDATE",
        "last_name": "USER",
        "email": "update@testuser.com",
    }
    response = client.put(
        "/peppermint/user/",
        json=update_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.json()["first_name"] == "UPDATE"
    assert response.json()["email"] == "update@testuser.com"

    assert response.json()["first_name"] != "TEST"
    assert response.json()["email"] != "testuser@testuser.com"


def test_user_update_by_user_id(client, test_user):
    """
    Test user update by user id endpoint
    """
    access_token = test_testuser_login(client, test_user)
    db = SessionLocal()
    test01 = get_user_by_username(db, "testuser")

    update_data = {
        "username": "testuser",
        "password1": "testpassword",
        "password2": "testpassword",
        "first_name": "UPDATENOW",
        "last_name": "USER",
        "email": "updatenow@testuser.com",
    }
    response = client.put(
        f"/peppermint/user/{test01.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.json()["first_name"] == "UPDATENOW"
    assert response.json()["email"] == "updatenow@testuser.com"

    assert response.json()["first_name"] != "TEST"
    assert response.json()["email"] != "testuser@testuser.com"


#  -------------------------------------------------------------------
#  DELETE
#  -------------------------------------------------------------------


def test_delete_testusers(client, test_user):
    """
    Deletes users created during testing
    """

    access_token = test_testuser_login(client, test_user)
    db = SessionLocal()
    testu2 = get_user_by_username(db, "testu2")
    testu1 = get_user_by_username(db, "testu1")
    testuser = get_user_by_username(db, "testuser")

    response = client.delete(
        f"/peppermint/user/{testu2.id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 204

    response = client.delete(
        f"/peppermint/user/{testu1.id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 204

    response = client.delete(
        f"/peppermint/user/{testuser.id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 204
