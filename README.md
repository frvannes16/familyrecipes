# Family Recipes

![Family Recipes Logo](/examples/logo-white.png)

Family Recipes is a website for creating high quality cookbooks for sharing or printing. Use it to create and store recipes using a responsive recipe editor, and then export your recipes to a print-ready PDF complete with links, pagination, a table of contents, and more.

To run this project yourself, follow the instructions in the "Getting Started" section of this README.

![Recipe Editor](/examples/recipe-creator.png)
**Recipe Editor**

![Store your recipes](/examples/view-recipes.png)
**Store your recipes**

**Turn your recipes into fully-featured, print ready cookbooks.**
[Example cookbook](/examples/cookbook.pdf)

## Project Motivation

In addition to creating a useful tool for my relatives, I created Family Recipes to learn! More specifically, I wanted to learn the following:

1. FastAPI: Is it a good replacement for Django + Django Rest Framework?
2. Vue 3: Why is it better than Vue 2?
3. Typescript: Am I more productive writing in Typescript than regular Javascript.
4. OpenAPI schema generation: Can I use FastAPI's OpenAPI spec generator and some handy scripting to generate typescript methods that interact with the API and are automatically typed?
5. Automated PDF generation: Does there exist an Adobe-free way of creating print-ready documents?
6. Improving approaches to settings configuration.

#### Featured Languages and Libraries

![Featured Languages, and Libraries](/examples/feature-software.png)

## Project Outcome

While much of this project is still ongoing, I was able to create a working app and learn everything I wanted to. Here is what I discovered in the process of making Family Recipes:

_Question: Is FastAPI a good replacement for Django + Django Rest Framework?_

Findings: FastAPI is an excellent tool for building lightweight APIs. Defining object structure with Pyndatic and letting Pydantic parse and validate requests made building API endpoints incredibly simple. FastAPI + Pyndatic is far easier to work with and more flexible than Django Rest Framework, which tends to get difficult to use when your serializers stray from your models. Additionally, I was able to quickly write my own password field that validated a given password string to ensure it met requirements. See `/api/schemas.py:PasswordStr`. This field fit in nicely to Pydantic validation responses.

Another benefit of FastAPI is the design of the `Depends()` system which encourages the writing of re-usable code.

The primary drawback of FastAPI was that it is no way near as featureful as Django. I had to implement my own authentication and authorization, which is always scary and leaves you vulnerable to attack. I also had to import an ORM library; I used sqlalchemy, which, while good, falls short of the Django ORM. The sqlalchemy documentation is also of lower quality than the Django ORM.

I look forward to using FastAPI more as it matures and authentication becomes easier. FastAPI's speed and embrace of Python typing renders Flask obsolete, but it's primary use for me will be for creating lightweight APIs. I expect to use FastAPI more as auth and ORM become easier to integrate by 3rd party libraries.

_Question: Vue 3: Why is it better than Vue 2?_

Findings: Vue 3 brings excellent Typescript support and the composition API as its primary offerings. The composition API took some learning to understand, but once I had a handle of it I was able to convert all components over to the composition API with relative easy and enjoyment. While this is a small project, I was still able to abstract code into `composables` that could be re-used. The composition API improved the readability of my code by allowing me to bunch similar logic together. It also made it easier to move code around!

Vue 3's Typescript support was so good, that I cannot remember running into one incompatibilty or any level of weirdness while using Typescript. I was able to use TS everywhere as a result. The use of Typescript was encouraged by my use of API endpoint method generation, which allowed me to really lean into Typescript and to better understand the contents of the objects that the API returned.

_Question: OpenAPI schema generation: Can I use FastAPI's OpenAPI spec generator and some handy scripting to generate typescript methods that interact with the API and are automatically typed?_

Findings: YES! I can. See [`gen.py`](gen.py) for how I generate the API openapi.json spec and provide it to the openapi generator project to generate a Typescript interface to my API. After having done this, I will ALWAYS use a client/server generator on my projects. It makes my life so much easier and it also empowers my use of Typescript in the client by ensuring all API endpoints are typed.

_Question: Automated PDF generation: Does there exist an Adobe-free way of creating print-ready documents?_

Findings: Yes there is, and it's called [weasyprint](https://weasyprint.org/). You can see my cookbook generation code and tests in `/api/cookbook/generator.py`. I use weasyprint to convert HTML and CSS to a feature full PDF. I had to learn about some working drafts for using CSS in print media: CSS Text Module 3 & 4 and CSS Paged Media Module Level 3. Once I understood some of the items in those drafts that Weasyprint supported, I was could paginate my HTML and provide a table of contents with links in the generated PDF. It required a good amount of trial and error to get weasyprint working, but I found the end result to be fairly fast and of a very high quality.

_Question: How can I improve approaches to settings configuration._

Findings: I used Pydantic for settings management. Django has decent settings management but falls short in that it doesn't have a simple way to validate settings on application launch. I was very impressed by Pydantic for just how easy it was to setup, provide multiple sources, and validate the types and presence of all of your settings at `from settings import Settings`-time. Django does not validate your settings, which has led to numerous production bugs in the past. I hope to use Pydantic for settings again!

## Getting Started

1. Create a python3.9 venv by installing python3.9 and running `python3.9 -m venv .venv`.
2. Activate the venv with `source .venv/bin/activate`.
3. Install pip-tools: `pip install pip-tools`
4. Install all other dependencies with `pip-sync`
5. Install weasyprint core libraries with `sudo apt install libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0 libffi-dev libjpeg-dev libopenjp2-7-dev`
6. Copy the `.env-example` file into a `.env` file. The app will parse the variables in `.env` in into the app settings, in addition to any environment variables that you have set. Change the `SECRET_KEY` varible to the results of running `echo -n $(openssl rand -base64 128)`
7. Run the migrations:

```bash
alembic upgrade head
```

8. Install `yarn` if it isn't already installed: `npm install -g yarn`.
9. Install frontend dependencies: `pushd frontend && yarn && popd`.
10. Follow the instructions in https://www.section.io/engineering-education/how-to-get-ssl-https-for-localhost/ exactly. Your localhost.key and localhost.crt should match the same locations as the script below.
11. Start the api using uvicorn. `uvicorn api.main:app --ssl-keyfile=./cert/CA/localhost/localhost.key --ssl-certfile=./cert/CA/localhost/localhost.crt `. In a separate terminal session, run the frontend server: `pushd frontend && yarn dev`.
12. Visit http://127.0.0.1:8000/docs to see the available endpoints and try them out!

## Migrations

Migrations only exist in the `api` directory currently, as do all database models, which are stored in `models.py`.

We use `Alembic` to manage and run migrations: [Alembic Docs](https://alembic.sqlalchemy.org)

To run migrations: `alembic upgrade head`.

To autogenerate a migration from a new table in `api/models.py`: `alembic revision --autogenerate -m "Revision message"`

## Testing

This project uses `pytest` to run tests, activated by running `pytest`.

## Generating OpenAPI Schema

Run `python gen.py` from the project directory to generate the OpenAPI schema in `api/autogenerated/openapi.json`.
