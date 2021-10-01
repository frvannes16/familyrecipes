# Family Recipes

Family Recipes is a website for storing your family's recipes. 



## Getting Started

1. Create a python3.9 venv by installing python3.9 and running `python3.9 -m venv .venv`.
2. Activate the venv with `source .venv/bin/activate`.
3. Install pip-tools: `pip install pip-tools`
4. Install all other dependencies with `pip-sync`
5. Copy the `.env-example` file into a `.env` file. The app will parse the variables in `.env` in into the app settings, in addition to any environment variables that you have set. Change the `SECRET_KEY` varible to the results of running `echo -n $(openssl rand -base64 128)`
6. Run the migrations:
```bash
alembic upgrade head
```
7. Install `yarn` if it isn't already installed: `npm install -g yarn`.
8. Install frontend dependencies: `pushd frontend && yarn && popd`.
9. Start the api using uvicorn. `uvicorn api.main:app --reload`. In a separate terminal session, run the frontend server: `pushd frontend && yarn dev`.
10. Visit http://127.0.0.1:8000/docs to see the available endpoints and try them out!


## Migrations

Migrations only exist in the `api` directory currently, as do all database models, which are stored in `models.py`.

We use `Alembic` to manage and run migrations: [Alembic Docs](https://alembic.sqlalchemy.org)

To run migrations: `alembic upgrade head`.

To autogenerate a migration from a new table in `api/models.py`: `alembic revision --autogenerate -m "Revision message"`


## Testing

This project uses `pytest` to run tests, activated by running `pytest`.