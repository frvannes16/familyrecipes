import os
from typing import Optional
from unittest import TestCase
import logging

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from api.database import Base
from api.main import app, get_db
from api.schemas import UserCreate, User
from api.crud import create_user

logger = logging.getLogger(__name__)


class DBTestCase(TestCase):
    """
    This special test case class creates a new database with every test setup, and destroys the database on teardown.
    You can access the client that uses the test DB by using `self.client`
    e.g.
    ```python
    response = self.client.get("/")
    ```

    You can also access the test DB by invoking `self.db`
    e.g.
    ```python
    user_count = self.db.query(models.User).count()
    ```
    """

    TEST_DB_LOCATION = "./test.db"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        self.db_setup()
        return super().setUp()

    def tearDown(self) -> None:
        self.db_teardown()
        return super().tearDown()

    def db_setup(self):
        # create test db
        self.test_db_url = f"sqlite:///{self.TEST_DB_LOCATION}"
        engine = create_engine(
            self.test_db_url, connect_args={"check_same_thread": False}
        )
        # Create all of the required tables. TODO: run migrations instead.
        logger.debug("Creating a test DB.")
        Base.metadata.create_all(bind=engine)
        TestingSessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=engine
        )

        def override_get_test_db():
            db: Optional[Session] = None
            try:
                db = TestingSessionLocal()
                yield db
            finally:
                if db:
                    db.close()

        # Change the main client's get_db function to use the test db.
        app.dependency_overrides[get_db] = override_get_test_db

        self.client = TestClient(app)
        self.db: Session = TestingSessionLocal()

    def db_teardown(self):
        if self.db:
            self.db.close()

        # destroy the test db by simply deleting the file.

        logger.debug("Destroying the test DB.")
        os.remove(self.TEST_DB_LOCATION)

    def create_user(self, email="test@example.com", password="aBadPa$$w0rd!!") -> User:
        new_user = UserCreate(password=password, email=email)
        created_user = create_user(db=self.db, user=new_user)
        return created_user

    def login(self, email: str, password: str):
        # Login in the user
        response = self.client.post(
            "/auth/token/",
            data={
                "username": email,
                "password": password,
            },
        )
        assert response.status_code == status.HTTP_200_OK, response.json()

    def create_and_login_user(
        self, email="test@example.com", password="aBadPa$$w0rd!!"
    ):
        created_user = self.create_user(email, password)
        self.login(email, password)
        return created_user
