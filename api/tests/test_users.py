import time

from jose import jwt
from fastapi import status

from api.testutils.testcase import DBTestCase
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

    def test_create_without_names_fails(self):
        data = {"email": "test@example.com", "password": "testPassword!123"}

        response = self.client.post("/auth/users/", json=data)

        assert response.status_code == 422
        

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

    def test_create_same_user_twice_notifies_user(self):
        # Ensure that when we sign up the same user email again, ask the user to sign in.
        data = {
            "email": "example@example.com",
            "first_name": "Example",
            "last_name": "User",
            "password": "testPassword!123",
        }

        response = self.client.post("/auth/users/", json=data)
        assert response.status_code == status.HTTP_200_OK

        # Creat the user a second time.
        response = self.client.post("/auth/users/", json=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()['detail'] == "User already exists. Please sign in with your username and password."


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
        token = response.json()["access_token"]
        assert token is not None
        assert response.json()["token_type"] == "bearer"

        set_cookie_header = response.headers["set-cookie"]
        assert f'access_token="bearer {token}"' in set_cookie_header
        # assert "HttpOnly" in set_cookie_header
        # assert "Secure" in set_cookie_header

        access_token = response.json()["access_token"]
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
            first_login_response.json()["token_type"]
            == second_login_response.json()["token_type"]
            == "bearer"
        )

        assert (
            first_login_response.json()["access_token"]
            != second_login_response.json()["access_token"]
        )

        # Decrypt the JWT tokens and compare their contents.

        first_resp_jwt = jwt.decode(
            first_login_response.json()["access_token"],
            settings.secret_key,
            algorithms=[JWT_ALGORITHM],
        )
        second_resp_jwt = jwt.decode(
            second_login_response.json()["access_token"],
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
        assert login_response.cookies.get("access_token") is not None

        assert self.client.cookies.get("access_token") is not None

        jwt_token = login_response.json()["access_token"]

        # Retry the earlier request for user data, and include the user's token in the response.
        response = self.client.get("/users/me/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "user@example.com"
        assert data["role"] == "MEMBER"
        assert data["token"]["access_token"] is not None
