from .testcase import DBTestCase


class UsersTestCase(DBTestCase):
    def test_create_and_get_user(self):
        data = {
            "email": "example@example.com",
            "first_name": "Example",
            "last_name": "User",
        }

        response = self.client.post("/users/", json=data)

        assert response.status_code == 200, response.json()
        assert response.json() == {
            "id": 1,
            "first_name": "Example",
            "last_name": "User",
            "email": "example@example.com",
        }, response.json()

        response = self.client.get("/users/1/")
        assert response.status_code == 200, response.status_code
        assert response.json() == {
            "id": 1,
            "first_name": "Example",
            "last_name": "User",
            "email": "example@example.com",
        }, response.json()

    def test_create_without_names(self):
        data = {"email": "test@example.com"}

        response = self.client.post("/users/", json=data)

        assert response.status_code == 200, response.json()
        assert response.json() == {
            "id": 1,
            "email": "test@example.com",
            "first_name": None,
            "last_name": None,
        }

    def test_invalid_email_fails(self):
        data = {
            "email": "example.example.com",
            "first_name": "Example",
            "last_name": "User",
        }

        response = self.client.post("/users/", json=data)

        assert response.status_code == 422

        assert response.json()["detail"][0]["type"] == "value_error.email"
