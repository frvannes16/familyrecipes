import datetime

from fastapi import status

from .testcase import DBTestCase
from api import models
from api.crud import create_user
from api.schemas import UserCreate


class GetRecipesTest(DBTestCase):
    def create_100_test_recipes(self, author_id: int):
        for idx in range(100):
            recipe = models.Recipe(
                name=f"Recipe #{idx}",
                steps="Step 1: Done!",
                author_id=author_id,
                created_at=datetime.datetime.utcnow(),
            )
            self.db.add(recipe)
        self.db.commit()

    def test_get_recipes_is_restricted(self):
        response = self.client.get("/recipes/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def setUpSessionUser(self):
        # create a user
        new_user = UserCreate(password="aBadPa$$w0rd!!", email="test@example.com")
        created_user = create_user(db=self.db, user=new_user)

        # Login in the user
        response = self.client.post(
            "/auth/token/",
            data={
                "username": new_user.email,
                "password": new_user.password.get_secret_value(),
            },
        )
        assert response.status_code == status.HTTP_200_OK, response.json()
        return created_user

    def test_get_paginated_recipes_default_first_page(self):
        created_user = self.setUpSessionUser()

        # TEST

        # Create 100 recipes
        self.create_100_test_recipes(author_id=created_user.id)

        # Just retrieves the first 10
        response = self.client.get("/recipes/")

        assert response.status_code == status.HTTP_200_OK, response.json()
        assert len(response.json()["data"]) == 10
        assert response.json()["page"] == 1
        assert response.json()["per_page"] == 10
        assert response.json()["max_page"] == 10
        assert response.json()["data"][0]["name"] == "Recipe #0"
        assert response.json()["data"][9]["name"] == "Recipe #9"
        assert response.json()["result_count"] == 100

    def test_get_paginated_recipes_different_page_len(self):
        created_user = self.setUpSessionUser()

        # Create 100 recipes
        self.create_100_test_recipes(author_id=created_user.id)

        # Just retrieves the first 80
        response = self.client.get("/recipes/?per_page=80&page=1")

        assert response.status_code == status.HTTP_200_OK, response.json()
        assert len(response.json()["data"]) == 80
        assert response.json()["page"] == 1
        assert response.json()["per_page"] == 80
        assert response.json()["max_page"] == 2
        assert response.json()["data"][0]["name"] == "Recipe #0"
        assert response.json()["data"][9]["name"] == "Recipe #9"
        assert response.json()["data"][-1]["name"] == "Recipe #79"
        assert response.json()["result_count"] == 100

        # Get the second page. There should only be 20 recipes

        response = self.client.get("/recipes/?per_page=80&page=2")

        assert response.status_code == status.HTTP_200_OK, response.json()
        assert len(response.json()["data"]) == 20
        assert response.json()["page"] == 2
        assert response.json()["per_page"] == 80
        assert response.json()["max_page"] == 2
        assert response.json()["data"][0]["name"] == "Recipe #80"
        assert response.json()["data"][9]["name"] == "Recipe #89"
        assert response.json()["data"][-1]["name"] == "Recipe #99"
        assert response.json()["result_count"] == 100

    def test_get_recipes_pagination_out_of_bounds(self):
        created_user = self.setUpSessionUser()

        # TEST

        # Create 100 recipes
        self.create_100_test_recipes(author_id=created_user.id)

        # Get page 2 for 100 recipes per page. This should be out of bounds and return no results.
        response = self.client.get("/recipes/?per_page=100&page=2")

        assert response.status_code == status.HTTP_200_OK, response.json()
        assert len(response.json()["data"]) == 0
        assert response.json()["page"] == 2
        assert response.json()["per_page"] == 100
        assert response.json()["max_page"] == 1
        assert response.json()["result_count"] == 100
