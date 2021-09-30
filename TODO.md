# TODO list
- [x] Select an async ORM.: sqlalchemy[asyncio]. It's in beta currently, but unlikely to make backwards incompatible changes.
- [X] Create a basic Recipe model with the ORM.
- [X] Create an Alembic migration to create the table.
- [X] Document Alembic commands
- [x] Connect pydantic to User model
- [X] Create User endpoints
- [x] Test User endpoints
- [x] Create DB test client inside of api/tests/testcase that will setup and teardown databases. See https://fastapi.tiangolo.com/advanced/testing-database/
- [ ] Connect Pydantic to Recipe model.
- [ ] Create GET /recipes endpoint.
- [X] Add authentication to users and user model. Do email and password auth for now.
- [ ] Cleanup files
- [ ] Add admin user role.

If the async sqlalchemy doesn't go well, just use synchronous sqlalchemy.

For later:
- [ ] Package pydantic PasswordStr into its own pypi package.   

