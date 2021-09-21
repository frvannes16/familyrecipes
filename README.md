# Family Recipes

Family Recipes is a website for storing your family's recipes. 



## Getting Started

1. Create a python3.9 venv by installing python3.9 and running `python3.9 -m venv .venv`.
2. Activate the venv with `source .venv/bin/activate`.
3. Install pip-tools: `pip install pip-tools`
4. Install all other depencies with `pip-sync`
5. Copy the `.env-example` file into a `.env` file. The app will parse the variables in `.env` in into the app settings, in addition to any environment variables that you have set.
6. Run the migrations:
```bash
pushd api && alembic upgrade head && popd
```
7. Start the app using uvicorn. `uvicorn api.main:app --reload`. The reload flag will listen for any changes.
8. Visit http://127.0.0.1:8000/docs to see the available endpoints and try them out!


## Migrations

Migrations only exist in the `api` directory currently, as do all database models, which are stored in `models.py`.

We use `Alembic` to manage and run migrations: [Alembic Docs](https://alembic.sqlalchemy.org)

To use Alembic, you must be in the `api` directory. `pushd api` will get you there.

To run migrations: `alembic upgrade head`.

To autogenerate a migration from a new table in `api/models.py`: `alembic revision --autogenerate -m "Revision message"`


## Testing

This project uses `pytest` to run tests, activated by running `pytest`.