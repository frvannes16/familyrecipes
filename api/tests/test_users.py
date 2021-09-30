import time

from jose import jwt
from fastapi import status

from .testcase import DBTestCase
from api.models import OAuth2Token, User
from api.settings import settings
from api.auth import JWT_ALGORITHM


class UsersTestCase(DBTestCase):
    def test_create_and_get_user(self):
        user_count = self.db.query(User).count()
        assert user_count == 0
        data = {
            "email": "example@example.com",
            "first_name": "Example",
            "last_name": "User",
            "password": "testPassword!123",
        }

        response = self.client.post("/auth/users/", json=data)

        assert response.status_code == 200
        assert response.json() == {
            "id": 1,
            "first_name": "Example",
            "last_name": "User",
            "email": "example@example.com",
        }, response.json()

        user_count = self.db.query(User).count()
        assert user_count == 1

        response = self.client.get("/users/1/")
        assert response.status_code == 200, response.status_code
        assert response.json() == {
            "id": 1,
            "first_name": "Example",
            "last_name": "User",
            "email": "example@example.com",
        }, response.json()

    def test_create_without_names(self):
        data = {"email": "test@example.com", "password": "testPassword!123"}

        response = self.client.post("/auth/users/", json=data)

        assert response.status_code == 200
        assert response.json() == {
            "id": 1,
            "email": "test@example.com",
            "first_name": None,
            "last_name": None,
        }

    def test_invalid_password_fails(self):
        data = {
            "email": "example@example.com",
            "first_name": "Example",
            "last_name": "User",
            "password": "pass",
        }

        response = self.client.post("/auth/users/", json=data)

        assert response.status_code == 422

        assert response.json()["detail"][0]["loc"] == ["body", "password"]
        assert response.json()["detail"][0]["type"] == "value_error"

    def test_invalid_email_fails(self):
        data = {
            "email": "example.example.com",
            "first_name": "Example",
            "last_name": "User",
            "password": "testPassword!123",
        }

        response = self.client.post("/auth/users/", json=data)

        assert response.status_code == 422

        assert response.json()["detail"][0]["type"] == "value_error.email"


class AuthTestCase(DBTestCase):
    def test_create_and_login_user(self):
        token_count = self.db.query(OAuth2Token).count()
        assert token_count == 0

        create_user_data = {
            "email": "user@example.com",
            "first_name": "Example",
            "last_name": "User",
            "password": "testPassword!123",
        }

        response = self.client.post("/auth/users/", json=create_user_data)

        assert response.status_code == 200

        # We still shouldn't have any tokens created.
        token_count = self.db.query(OAuth2Token).count()
        assert token_count == 0

        # log the user in.

        login_form = {
            "username": "user@example.com",
            "password": "testPassword!123",
        }

        response = self.client.post("/auth/token/", data=login_form)
        assert response.status_code == 200

        assert response.json()["email"] == "user@example.com"
        assert response.json()["token"]["name"] == "OAuth2"
        assert response.json()["token"]["access_token"] is not None

        access_token = response.json()["token"]["access_token"]
        token_count = self.db.query(OAuth2Token).count()
        assert token_count == 1
        db_token = self.db.query(OAuth2Token).first()
        assert db_token is not None
        assert db_token.access_token == access_token

    def test_login_twice(self):
        # SETUP. Create a user
        create_user_data = {
            "email": "user@example.com",
            "first_name": "Example",
            "last_name": "User",
            "password": "testPassword!123",
        }

        response = self.client.post("/auth/users/", json=create_user_data)
        assert response.status_code == 200

        login_form = {
            "username": "user@example.com",
            "password": "testPassword!123",
        }

        # Login the first time.
        first_login_response = self.client.post("/auth/token/", data=login_form)
        assert first_login_response.status_code == 200

        # Wait a second so that we see the token exp unix timestamp change.
        time.sleep(1.1)

        # Login a second time
        second_login_response = self.client.post("/auth/token/", data=login_form)
        assert second_login_response.status_code == 200

        # The tokens should match, except for JWT and expiration, simply because the expiration updated.
        assert (
            first_login_response.json()["email"]
            == second_login_response.json()["email"]
        )
        assert (
            first_login_response.json()["token"]["name"]
            == second_login_response.json()["token"]["name"]
        )
        assert (
            first_login_response.json()["token"]["token_type"]
            == second_login_response.json()["token"]["token_type"]
        )

        assert (
            first_login_response.json()["token"]["expires_at"]
            != second_login_response.json()["token"]["expires_at"]
        )

        assert (
            first_login_response.json()["token"]["access_token"]
            != second_login_response.json()["token"]["access_token"]
        )

        # Decrypt the JWT tokens and compare their contents.

        first_resp_jwt = jwt.decode(
            first_login_response.json()["token"]["access_token"],
            settings.secret_key,
            algorithms=[JWT_ALGORITHM],
        )
        second_resp_jwt = jwt.decode(
            second_login_response.json()["token"]["access_token"],
            settings.secret_key,
            algorithms=[JWT_ALGORITHM],
        )

        assert first_resp_jwt != second_resp_jwt
        assert first_resp_jwt["exp"] != second_resp_jwt["exp"]
        assert first_resp_jwt["name"] == second_resp_jwt["name"]
        assert first_resp_jwt["sub"] == second_resp_jwt["sub"]

    def test_privileged_endpoint__my_user(self):

        # SETUP: Create a user

        create_user_data = {
            "email": "user@example.com",
            "first_name": "Example",
            "last_name": "User",
            "password": "testPassword!123",
        }

        response = self.client.post("/auth/users/", json=create_user_data)
        assert response.status_code == status.HTTP_200_OK

        # Assert that we cannot access the user's data without logging in.

        response = self.client.get("/users/me/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Login and store access token.

        login_form = {
            "username": "user@example.com",
            "password": "testPassword!123",
        }

        # Login the first time.
        login_response = self.client.post("/auth/token/", data=login_form)
        assert login_response.status_code == status.HTTP_200_OK

        jwt_token = login_response.json()["token"]["access_token"]

        # Retry the earlier request for user data, and include the user's token in the response.
        response = self.client.get(
            "/users/me/", headers={"Authorization": f"bearer {jwt_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
