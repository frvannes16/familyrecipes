import datetime

from fastapi import status

from api.testutils.testcase import DBTestCase
from api import models
from api.crud import create_user
from api.schemas import UserCreate


class GetRecipesTest(DBTestCase):
    def create_test_recipes(self, author_id: int, count: int):
        for idx in range(count):
            recipe = models.Recipe(
                name=f"Recipe #{idx}",
                author_id=author_id,
                created_at=datetime.datetime.utcnow(),
            )
            self.db.add(recipe)
            self.db.commit()

            steps = [
                models.RecipeStep(
                    position=idx,
                    content=f"Add {idx + 1} flax eggs",
                    recipe_id=recipe.id,
                )
                for idx in range(0, 5)
            ]
            ingredients = [
                models.RecipeIngredient(
                    position=idx,
                    content=f"{idx + 1} tbsp ground flax seed",
                    recipe_id=recipe.id,
                )
                for idx in range(0, 5)
            ]
            self.db.bulk_save_objects(steps)
            self.db.bulk_save_objects(ingredients)
            self.db.commit()

    def test_get_recipes_is_restricted(self):
        response = self.client.get("/recipes/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_paginated_recipes_default_first_page(self):
        created_user = self.create_and_login_user()

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
        created_user = self.create_and_login_user()

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
        created_user = self.create_and_login_user()

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
        created_user = self.create_and_login_user()

        # Create 15 recipes that belong to the session user.
        self.create_test_recipes(created_user.id, 15)

        # Create a secondary user and create 10 recipes belonging to them.
        created_other_user = self.create_user(
            password="aBadPa$$w0rd!!", email="test2@example.com"
        )
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
        _session_user = self.create_and_login_user()

        response = self.client.get("/users/999/recipes/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_user_recipe(self):
        session_user = self.create_and_login_user()

        recipe_count_before = self.db.query(models.Recipe).count()

        self.assertEqual(recipe_count_before, 0)

        recipe_data = {
            "name": "Momma Franklin's Famous Chili",
        }

        response = self.client.post(f"/recipes/", json=recipe_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
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
                "steps": [],
                "ingredients": [],
                "author_id": session_user.id,
                "author": {
                    "email": "test@example.com",
                    "first_name": "Test",
                    "last_name": "User",
                    "id": session_user.id,
                },
            },
        )

        recipe_count_after = self.db.query(models.Recipe).count()

        self.assertEqual(
            recipe_count_after, recipe_count_before + 1
        )  # new recipe created.

    def test_get_recipe_with_ingredients_and_steps(self):
        user = self.create_and_login_user(email="test@example.com")

        # SETUP

        recipe = models.Recipe(
            name="Chili", author_id=user.id, created_at=datetime.datetime.utcnow()
        )
        self.db.add(recipe)
        self.db.commit()

        # Add some ingredients and some steps
        ingredients = [
            models.RecipeIngredient(
                position=0,
                content="4 cloves garlic",
                recipe_id=recipe.id,
            ),
            models.RecipeIngredient(
                position=1,
                content="14 oz canned diced tomatoes",
                recipe_id=recipe.id,
            ),
        ]

        steps = [
            # out of order
            models.RecipeStep(
                position=1, content="Add the garlic cloves.", recipe_id=recipe.id
            ),
            models.RecipeStep(
                position=0, content="Add the diced tomatoes.", recipe_id=recipe.id
            ),
        ]
        self.db.bulk_save_objects(ingredients)
        self.db.bulk_save_objects(steps)
        self.db.commit()

        # TEST
        # Ensure that the ingredients and steps are returned in order by the API.

        response = self.client.get(f"/recipes/{recipe.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIsNotNone(data)
        expected_recipe_subset = {
            "name": "Chili",
            "steps": [
                {
                    "position": 0,
                    "content": "Add the diced tomatoes.",
                    "id": 2,
                    "recipe_id": 1,
                },
                {
                    "position": 1,
                    "content": "Add the garlic cloves.",
                    "id": 1,
                    "recipe_id": 1,
                },
            ],
            "ingredients": [
                {
                    "content": "4 cloves garlic",
                    "position": 0,
                    "id": 1,
                    "recipe_id": 1,
                },
                {
                    "content": "14 oz canned diced tomatoes",
                    "position": 1,
                    "id": 2,
                    "recipe_id": 1,
                },
            ],
        }
        self.assertEqual(data, data | expected_recipe_subset)
        expected_author_subset = {"email": "test@example.com"}
        self.assertEqual(data["author"], data["author"] | expected_author_subset)

    def test_update_recipe_name(self):
        user = self.create_and_login_user(email="test@example.com")

        # SETUP

        recipe = models.Recipe(
            name="Recipe Name Before Change",
            author_id=user.id,
            created_at=datetime.datetime.utcnow(),
        )
        self.db.add(recipe)
        self.db.commit()

        # TEST

        name_change_data = {"name": "Recipe Name AFTER Change"}

        response = self.client.post(f"/recipes/{recipe.id}/", json=name_change_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        expected_subset = {
            "id": recipe.id,
            "name": "Recipe Name AFTER Change",
            "steps": [],
            "ingredients": [],
        }
        self.assertEqual(response.json(), response.json() | expected_subset)


class IngredientsTest(DBTestCase):
    def setUp(self):
        super().setUp()
        self.user = self.create_and_login_user()

    def test_put_ingredient_to_recipe(self):
        # Create a recipe without ingredients
        recipe = models.Recipe(
            name="Chili", author_id=self.user.id, created_at=datetime.datetime.utcnow()
        )
        self.db.add(recipe)
        self.db.commit()

        new_ingredient_data = {
            "content": "14 oz canned fire-roasted tomatoes",
        }

        response = self.client.post(
            f"/recipes/{recipe.id}/ingredients/", json=new_ingredient_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        self.assertEqual(
            response.json(),
            [
                {
                    "id": 1,
                    "position": 0,
                    "content": "14 oz canned fire-roasted tomatoes",
                    "recipe_id": recipe.id,
                }
            ],
        )

        # Add another ingredient. It should be appended.
        new_ingredient_data = {
            "content": "1 can black beans",
        }

        response = self.client.post(
            f"/recipes/{recipe.id}/ingredients/", json=new_ingredient_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        self.assertEqual(
            response.json(),
            [
                {
                    "id": 1,
                    "position": 0,
                    "content": "14 oz canned fire-roasted tomatoes",
                    "recipe_id": recipe.id,
                },
                {
                    "id": 2,
                    "position": 1,
                    "content": "1 can black beans",
                    "recipe_id": recipe.id,
                },
            ],
        )

    def test_update_ingredient(self):
        # Create a recipe with one ingredient
        recipe = models.Recipe(
            name="Chili", author_id=self.user.id, created_at=datetime.datetime.utcnow()
        )
        self.db.add(recipe)
        self.db.commit()

        ingredient = models.RecipeIngredient(
            position=0,
            content="4 cloves garlic",
            recipe_id=recipe.id,
        )
        self.db.add(ingredient)
        self.db.commit()

        update_ingredient_data = {"content": "5 cloves garlic"}

        response = self.client.post(
            f"/recipes/ingredients/{ingredient.id}/", json=update_ingredient_data
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        self.assertEqual(
            response.json(),
            [
                {
                    "id": 1,
                    "position": 0,
                    "content": "5 cloves garlic",
                    "recipe_id": recipe.id,
                },
            ],
        )

    def test_update_ingredients_ingredient_doesnt_exist(self):
        # create a recipe with one ingredient belonging to main user.
        recipe = models.Recipe(
            name="Chili", author_id=self.user.id, created_at=datetime.datetime.utcnow()
        )
        self.db.add(recipe)
        self.db.commit()

        update_ingredient_data = {"content": "5 cloves garlic"}

        response = self.client.post(
            f"/recipes/ingredients/100/", json=update_ingredient_data
        )

        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND, response.json()
        )

    def test_update_ingredients_no_access(self):
        # create a recipe with one ingredient belonging to main user.
        recipe = models.Recipe(
            name="Chili", author_id=self.user.id, created_at=datetime.datetime.utcnow()
        )
        self.db.add(recipe)
        self.db.commit()

        ingredient = models.RecipeIngredient(
            position=0,
            content="4 cloves garlic",
            recipe_id=recipe.id,
        )
        self.db.add(ingredient)
        self.db.commit()

        # change the logged in user and attempt to edit the ingredient. It should fail.

        self.create_and_login_user(
            "test2@example.com", password="lkajsdlkjasdLKJASDLKJ123!:!:!"
        )

        update_ingredient_data = {"content": "5 cloves garlic"}

        response = self.client.post(
            f"/recipes/ingredients/{ingredient.id}/", json=update_ingredient_data
        )

        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN, response.json()
        )

    def test_delete_ingredient(self):
        # Create a recipe with ingredients
        recipe = models.Recipe(
            name="Chili", author_id=self.user.id, created_at=datetime.datetime.utcnow()
        )
        self.db.add(recipe)
        self.db.commit()

        ingredients = [
            models.RecipeIngredient(
                position=0,
                content="4 cloves garlic",
                recipe_id=recipe.id,
            ),
            models.RecipeIngredient(
                position=1, content="1 can black beans", recipe_id=recipe.id
            ),
            models.RecipeIngredient(
                position=2, content="1 can diced tomatoes", recipe_id=recipe.id
            ),
            models.RecipeIngredient(
                position=3, content="2 tbsp cocoa powder", recipe_id=recipe.id
            ),
        ]
        self.db.add_all(ingredients)
        self.db.commit()

        response = self.client.get(
            f"/recipes/{recipe.id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        positions = [ing['position'] for ing in response.json()['ingredients']]
        self.assertEqual(positions, [0, 1, 2, 3])

        ingredient_id_to_delete = response.json()['ingredients'][1]['id']

        # Remove the second ingredient and expect the positions to collapse into place.
        response = self.client.delete(f"/recipes/ingredients/{ingredient_id_to_delete}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        positions = [ing['position'] for ing in response.json()]
        self.assertEqual(positions, [0, 1, 2])

        # Remove the first and last ingredient without error.
        response_a = self.client.delete(f"/recipes/ingredients/{response.json()[0]['id']}/")
        response_b = self.client.delete(f"/recipes/ingredients/{response.json()[-1]['id']}/")
        self.assertEqual(response_a.status_code, status.HTTP_200_OK)
        self.assertEqual(response_b.status_code, status.HTTP_200_OK)

class StepsTest(DBTestCase):
    def setUp(self):
        super().setUp()
        self.user = self.create_and_login_user()

    def test_put_step_to_recipe(self):
        # Create a recipe without steps
        recipe = models.Recipe(
            name="Chili", author_id=self.user.id, created_at=datetime.datetime.utcnow()
        )
        self.db.add(recipe)
        self.db.commit()

        new_step_data = {"content": "Stir it all up!"}

        response = self.client.post(f"/recipes/{recipe.id}/steps/", json=new_step_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        self.assertEqual(
            response.json(),
            [
                {
                    "id": 1,
                    "content": "Stir it all up!",
                    "recipe_id": recipe.id,
                    "position": 0,
                }
            ],
        )

        # Add another step. It should be appended.
        new_step_data = {"content": "Stir it another time!"}

        response = self.client.post(f"/recipes/{recipe.id}/steps/", json=new_step_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        self.assertEqual(
            response.json(),
            [
                {
                    "id": 1,
                    "content": "Stir it all up!",
                    "recipe_id": recipe.id,
                    "position": 0,
                },
                {
                    "id": 2,
                    "content": "Stir it another time!",
                    "recipe_id": recipe.id,
                    "position": 1,
                },
            ],
        )

    def test_update_recipe_step(self):
        # Create a recipe with a step
        recipe = models.Recipe(
            name="Chili", author_id=self.user.id, created_at=datetime.datetime.utcnow()
        )
        self.db.add(recipe)
        self.db.commit()

        step = models.RecipeStep(
            content="Add cayenne pepper. Stir.", recipe_id=recipe.id, position=0
        )
        self.db.add(step)
        self.db.commit()

        # try to update the recipe step.
        edit_step_data = {"content": "Add cayenne pepper. Shake, don't stir."}
        response = self.client.post(f"/recipes/steps/{step.id}/", json=edit_step_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        self.assertEqual(
            response.json(),
            [
                {
                    "id": step.id,
                    "content": "Add cayenne pepper. Shake, don't stir.",
                    "position": 0,
                    "recipe_id": recipe.id,
                }
            ],
        )

    def test_update_recipe_step_does_not_exist(self):
        # Create a recipe without a step
        recipe = models.Recipe(
            name="Chili", author_id=self.user.id, created_at=datetime.datetime.utcnow()
        )
        self.db.add(recipe)
        self.db.commit()

        # try to update the recipe step.
        edit_step_data = {"content": "Add cayenne pepper. Shake, don't stir."}
        response = self.client.post(f"/recipes/steps/100/", json=edit_step_data)

        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND, response.json()
        )

    def test_update_step_no_recipe_access(self):
        # Create a recipe with a step
        recipe = models.Recipe(
            name="Chili", author_id=self.user.id, created_at=datetime.datetime.utcnow()
        )
        self.db.add(recipe)
        self.db.commit()

        step = models.RecipeStep(
            content="Add cayenne pepper. Stir.", recipe_id=recipe.id, position=0
        )
        self.db.add(step)
        self.db.commit()

        # Try to update the recipe step without access.
        # Log into a different user.
        self.create_and_login_user(email="test-other@example.com")
        edit_step_data = {"content": "Add cayenne pepper. Shake, don't stir."}
        response = self.client.post(f"/recipes/steps/{step.id}/", json=edit_step_data)

        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN, response.json()
        )

    def test_delete_step(self):
        # Create a recipe with steps
        recipe = models.Recipe(
            name="Chili", author_id=self.user.id, created_at=datetime.datetime.utcnow()
        )
        self.db.add(recipe)
        self.db.commit()

        steps = [
            models.RecipeStep(
                position=0,
                content="chop garlic",
                recipe_id=recipe.id,
            ),
            models.RecipeStep(
                position=1, content="chop onions", recipe_id=recipe.id
            ),
            models.RecipeStep(
                position=2, content="cook onions", recipe_id=recipe.id
            ),
            models.RecipeStep(
                position=3, content="cook garlic", recipe_id=recipe.id
            ),
        ]
        self.db.add_all(steps)
        self.db.commit()

        response = self.client.get(
            f"/recipes/{recipe.id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        positions = [ing['position'] for ing in response.json()['steps']]
        self.assertEqual(positions, [0, 1, 2, 3])

        step_id_to_delete = response.json()['steps'][1]['id']

        # Remove the second step and expect the positions to collapse into place.
        response = self.client.delete(f"/recipes/steps/{step_id_to_delete}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        positions = [ing['position'] for ing in response.json()]
        self.assertEqual(positions, [0, 1, 2])

        # Remove the first and last step without error.
        response_a = self.client.delete(f"/recipes/steps/{response.json()[0]['id']}/")
        response_b = self.client.delete(f"/recipes/steps/{response.json()[-1]['id']}/")
        self.assertEqual(response_a.status_code, status.HTTP_200_OK)
        self.assertEqual(response_b.status_code, status.HTTP_200_OK)