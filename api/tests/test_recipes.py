import datetime

from fastapi import status

from .testcase import DBTestCase
from api import models
from api.crud import create_user
from api.schemas import UserCreate


class GetRecipesTest(DBTestCase):
    def create_test_recipes(self, author_id: int, count: int):
        for idx in range(count):
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
        self.create_test_recipes(author_id=created_user.id, count=100)

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
        self.create_test_recipes(author_id=created_user.id, count=100)

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

        # Create 100 recipes that belong to the user
        self.create_test_recipes(author_id=created_user.id, count=100)

        # Get page 2 for 100 recipes per page. This should be out of bounds and return no results.
        response = self.client.get("/recipes/?per_page=100&page=2")

        assert response.status_code == status.HTTP_200_OK, response.json()
        assert len(response.json()["data"]) == 0
        assert response.json()["page"] == 2
        assert response.json()["per_page"] == 100
        assert response.json()["max_page"] == 1
        assert response.json()["result_count"] == 100

    def test_get_my_recipes(self):
        created_user = self.setUpSessionUser()

        # Create 15 recipes that belong to the session user.
        self.create_test_recipes(created_user.id, 15)

        # Create a secondary user and create 10 recipes belonging to them.
        other_user = UserCreate(password="aBadPa$$w0rd!!", email="test2@example.com")
        created_other_user = create_user(db=self.db, user=other_user)
        self.create_test_recipes(created_other_user.id, 10)

        # Retrieve all recipes. There should be 25 in total
        response = self.client.get("/recipes/?per_page=100")
        assert response.status_code == status.HTTP_200_OK, response.json()
        assert response.json()["result_count"] == 25
        assert len(response.json()["data"]) == 25

        # Retrieve only this user's recipes. There should be 15 in total.
        response = self.client.get(f"/users/{created_user.id}/recipes/?per_page=100")
        assert response.status_code == status.HTTP_200_OK, response.text
        assert response.json()["result_count"] == 15
        assert len(response.json()["data"]) == 15
        assert response.json()["data"][0]["author"]["email"] == "test@example.com"

    def test_get_missing_author_returns_404(self):
        _session_user = self.setUpSessionUser()

        response = self.client.get("/users/999/recipes/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_user_recipe(self):
        session_user = self.setUpSessionUser()

        recipe_count_before = self.db.query(models.Recipe).count()

        self.assertEqual(recipe_count_before, 0)

        recipe_data = {
            "name": "Momma Franklin's Famous Chili",
            "steps": "1. Make momma Franklin's famous chili\n2. Enjoy!",
        }

        response = self.client.post(f"/recipes/", json=recipe_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.json())
        data = response.json()
        self.assertIsNotNone(data)
        data = data.copy()
        self.assertIsNotNone(data["created_at"])
        data.pop("created_at")
        self.assertEqual(
            data,
            {
                "id": 1,
                "name": "Momma Franklin's Famous Chili",
                "steps": "1. Make momma Franklin's famous chili\n2. Enjoy!",
                "author_id": session_user.id,
                "author": {
                    "email": "test@example.com",
                    "first_name": None,
                    "last_name": None,
                    "id": session_user.id,
                },
            },
        )

        recipe_count_after = self.db.query(models.Recipe).count()

        self.assertEqual(
            recipe_count_after, recipe_count_before + 1
        )  # new recipe created.
