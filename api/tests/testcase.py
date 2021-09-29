import os
from unittest import TestCase
import logging

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..database import Base
from ..main import app, get_db

logger = logging.getLogger(__name__)


class DBTestCase(TestCase):
    TEST_DB_LOCATION = "./test.db"

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
            db = None
            try:
                db = TestingSessionLocal()
                yield db
            finally:
                if db:
                    db.close()

        # Change the main client's get_db function to use the test db.
        app.dependency_overrides[get_db] = override_get_test_db

        self.client = TestClient(app)

    def db_teardown(self):
        # destroy the test db by simply deleting the file.

        logger.debug("Destroying the test DB.")
        os.remove(self.TEST_DB_LOCATION)