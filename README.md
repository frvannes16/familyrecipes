# Family Recipes

Family Recipes is a website for storing your family's recipes. 



## Getting Started

1. Create a python3.9 venv by installing python3.9 and running `python3.9 -m venv .venv`.
2. Activate the venv with `source .venv/bin/activate`.
3. Install pip-tools: `pip install pip-tools`
4. Install all other depencies with `pip-sync`
5. Copy the `.env-example` file into a `.env` file. The app will parse the variables in `.env` in into the app settings, in addition to any environment variables that you have set.
6. Start the app using uvicorn. `uvicorn api.main:app --reload`. The reload flag will listen for any changes.
7. Visit http://127.0.0.1:8000/docs to see the available endpoints and try them out!



## Testing

This project uses `pytest` to run tests, activated by running `pytest`.