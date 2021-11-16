# TODO list

- [x] Select an async ORM.: sqlalchemy[asyncio]. It's in beta currently, but unlikely to make backwards incompatible changes.
- [x] Create a basic Recipe model with the ORM.
- [x] Create an Alembic migration to create the table.
- [x] Document Alembic commands
- [x] Connect pydantic to User model
- [x] Create User endpoints
- [x] Test User endpoints
- [x] Create DB test client inside of api/tests/testcase that will setup and teardown databases. See https://fastapi.tiangolo.com/advanced/testing-database/
- [x] Connect Pydantic to Recipe model.
- [x] Create GET /recipes endpoint.
- [x] Add authentication to users and user model. Do email and password auth for now.
- [x] Cleanup files
- [x] Add admin user role.
- [x] Autogenerate axios methods from fastapi swagger file. Add package.json script or python script for it.
- [ ] Investigate CSRF?
- [x] Remove the multiple fields in the ingredients model. Just have one!
- [ ] Improved front end error handling. Show the message!

If the async sqlalchemy doesn't go well, just use synchronous sqlalchemy.

For later:

- [ ] Package pydantic PasswordStr into its own pypi package.
