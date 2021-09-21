# TODO list
- [x] Select an async ORM.: sqlalchemy[asyncio]. It's in beta currently, but unlikely to make backwards incompatible changes.
- [ ] Create a basic Recipe model with the ORM.
- [ ] Create an Alembic migration to create the table.
- [ ] Document Alembic commands
- [ ] Connect Pydantic to Recipe model.
- [ ] Create GET /recipes endpoint.
- [ ] Add authentication to users and user model.

If the async sqlalchemy doesn't go well, just use synchronous sqlalchemy.