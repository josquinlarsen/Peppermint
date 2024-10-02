import pytest
from fastapi.testclient import TestClient
from main import app
import json
from domain.transaction.transaction_crud import (
    get_account_transactions,
    get_account_transaction_by_id,
)
from domain.user.user_crud import get_user_by_username, get_user_by_id
from domain.account.account_crud import (
    create_account,
    get_account_by_id,
    account_balance_update,
)
from database import SessionLocal


client_401 = TestClient(app)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_user():
    return {"username": "testuser", "password": "testpassword"}


@pytest.fixture
def test_account():
    return {
        "id": "0",
        "institution": "testbank",
        "account_type": "checking",
        "current_balance": "0",
    }


def test_setup_user(client):
    """
    Register user for testing
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


def test_setup_login_user(client, test_user):
    """
    Login user for testing
    """
    response = client.post("/peppermint/user/login", data=test_user)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()
    assert "username" in response.json()

    return response.json()["access_token"]


def test_setup_add_account(client, test_user):
    """
    Create account for testing
    """
    db = SessionLocal()
    access_token = test_setup_login_user(client, test_user)
    data = {
        "institution": "testbank",
        "account_type": "checking",
        "current_balance": 0.0,
    }

    response = client.post(
        "/peppermint/account/",
        json=data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200


def test_transaction_create(client, test_user):
    """
    Create transaction endpoint test
    """
    access_token = test_setup_login_user(client, test_user)
    account_response01 = client.get(
        "/peppermint/account/my_accounts",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    account = account_response01.json()[0]

    transaction_data = {
        "transaction_date": "2024-09-29T19:51:34.898000",
        "transaction_amount": 100.0,
    }

    response = client.post(f"/peppermint/{account['id']}", json=transaction_data)

    account_response02 = client.get(
        "/peppermint/account/my_accounts",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    account_check = account_response02.json()[0]

    assert response.status_code == 200
    assert response.json()["transaction_date"] == "2024-09-29T19:51:34.898000"
    assert "transaction_amount" in response.json()
    assert account_check["current_balance"] == 100.0


# ---------------------------------------------------------
#   DELETE
# ---------------------------------------------------------


def test_delete_setup_users(client, test_user):
    """
    Deletes users created during testing
    """
    access_token = test_setup_login_user(client, test_user)
    db = SessionLocal()
    testuser = get_user_by_username(db, "testuser")

    response = client.delete(
        f"/peppermint/user/{testuser.id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 204