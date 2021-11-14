import datetime
from typing import Optional

from fastapi import status

from api.testutils.testcase import DBTestCase
from api import models
from api.crud import create_user
from api.cookbooks.generator import generate_pdf_from_recipes
from api.schemas import RecipeInDB, UserCreate


class CookbookMakerAPITest(DBTestCase):
    def create_and_login_user(self, email: Optional[str] = "test@example.com"):
        # create a user
        new_user = UserCreate(password="aBadPa$$w0rd!!", email=email)
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

    def test_generate_basic_cookbook(self):
        # SETUP: Generate a user and recipe.
        created_user = self.create_and_login_user()
        recipe = models.Recipe(
            name=f"Test Recipe",
            author_id=created_user.id,
            created_at=datetime.datetime.utcnow(),
        )
        self.db.add(recipe)
        self.db.commit()
        steps = [
            models.RecipeStep(
                position=idx, content=f"Add {idx + 1} flax eggs", recipe_id=recipe.id
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

        # Log the user in
        login_response = self.client.post(
            "/auth/token/",
            data={
                "username": created_user.email,
                "password": "aBadPa$$w0rd!!",
            },
        )
        self.assertEqual(
            login_response.status_code, status.HTTP_200_OK, login_response.json()
        )

        # Call the cookbook generation endpoint

        response = self.client.get(f"/recipes/{recipe.id}/generate-pdf/")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response)
        self.assertEqual(response.headers.get("content-type"), "application/pdf")
        self.assertIsNotNone(response.content)
        self.assertIn(b"Test Recipe", response.content)

    def test_cookbook_generation_rejects_non_authors(self):
        # SETUP: Generate two user and recipe belonging to the first user.
        first_user = self.create_and_login_user(email="test1@example.com")
        second_user = self.create_and_login_user(email="test2@example.com")

        recipe = models.Recipe(
            name=f"Test Recipe",
            author_id=first_user.id,
            created_at=datetime.datetime.utcnow(),
        )
        self.db.add(recipe)
        self.db.commit()

        steps = [
            models.RecipeStep(
                position=idx, content=f"Add {idx + 1} flax eggs", recipe_id=recipe.id
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

        # Login as second user

        login_response = self.client.post(
            "/auth/token/",
            data={
                "username": second_user.email,
                "password": "aBadPa$$w0rd!!",
            },
        )
        self.assertEqual(
            login_response.status_code, status.HTTP_200_OK, login_response.json()
        )

        # Try to generate the first user's recipe. This should fail

        response = self.client.get(f"/recipes/{recipe.id}/generate-pdf/")
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN, response.json()
        )

    def test_generate_cookbook_byte_return_value(self):
        # SETUP: Generate a user and recipe.
        created_user = self.create_and_login_user()
        recipe = models.Recipe(
            name=f"Test Recipe",
            author_id=created_user.id,
            created_at=datetime.datetime.utcnow(),
        )
        self.db.add(recipe)
        self.db.commit()

        steps = [
            models.RecipeStep(
                position=idx, content=f"Add {idx + 1} flax eggs", recipe_id=recipe.id
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

        recipes = list((RecipeInDB.from_orm(recipe),))

        # Test that there are bytes returned.
        # We don't have a good way of testing the file contents
        pdf_bytes = generate_pdf_from_recipes(recipes)

        self.assertIsNotNone(pdf_bytes)
        self.assertIsInstance(pdf_bytes, bytes)
