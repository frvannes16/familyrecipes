import json
import os
import shutil
import zipfile
import glob
import pathlib

import typer
import requests

from api.main import app

typer_app = typer.Typer()


ZIP_FILENAME = "typescript-axios-client"


@typer_app.command()
def all():
    """Generates openapi.json and frontend client code"""
    openapi()
    client()


@typer_app.command()
def openapi():
    """Generates an OpenApi file in api/gen/openapi.json for our FastAPI application."""
    filename = "openapi.json"

    app.setup()

    schema_dict = app.openapi()
    if not schema_dict:
        typer.echo("Error: OpenAPI Schema is empty", err=True, color=True)
        raise typer.Exit(1)

    # Create autogenerated directory
    curpath = os.path.abspath(os.curdir)
    gendir = os.path.join(curpath, "api", "gen")
    if not os.path.exists(gendir):
        typer.echo(f"Creating new {gendir} directory")
        os.mkdir(gendir)

    filepath = os.path.join(gendir, filename)

    # Write schema to openapi.json
    with open(filepath, "w") as openapi_file:
        typer.echo(f"Writing OpenAPI schema to {filepath}")
        json.dump(schema_dict, openapi_file, indent=4)
        typer.echo("Complete")


@typer_app.command()
def client():
    """Uses the openapi generator to generate typescript-axios code from api/gen/openapi.json"""
    curpath = os.path.abspath(os.curdir)
    schema_path = os.path.join(curpath, "api", "gen", "openapi.json")
    code_path = os.path.join(curpath, "frontend", "gen")

    if not os.path.exists(schema_path):
        typer.echo(f"File Not Found: {schema_path}. Please generate the file first.")
        raise typer.Exit(1)

    spec = {}

    with open(schema_path, "r") as schema_file:
        spec = json.load(schema_file)

    data = {"options": {}, "spec": spec}
    response = requests.post(
        "http://api-latest-master.openapi-generator.tech/api/gen/clients/typescript-axios",
        json=data,
    )  # This response contains a link to the downloadable code file.

    # Download and store the zipped code in /tmp/
    if response and response.status_code == 200:
        code_url = response.json()["link"]
        temp_download_path = os.path.join("/", "tmp", f"{ZIP_FILENAME}.zip")
        typer.echo(f"Downloading client code from {code_url} to {temp_download_path}")
        download_client_code_zip(code_url, destination_zip=temp_download_path)
        typer.echo("Prepping generated code directory")
        prepare_destination_dir(destination_dir=code_path)
        typer.echo("Extracting zipped code")
        extract_zipped_code(
            temp_download_path, destination_dir=code_path, dir_name="api"
        )
        typer.echo("Removing unused files")
        delete_unused_files(code_path + "/api")
        typer.echo("Done!")

    else:
        typer.echo(
            f"Bad Response {response.status_code}: {response.json()}",
            err=True,
            color=True,
        )
        raise typer.Exit(1)


def download_client_code_zip(code_url: str, destination_zip: str):

    with requests.get(
        code_url, stream=True, timeout=5000
    ) as resp:  # Contains a zip file download.
        resp.raise_for_status()
        with open(destination_zip, "wb") as zip_file:
            shutil.copyfileobj(resp.raw, zip_file)


def prepare_destination_dir(destination_dir: str):
    """Create the destination directory if it does not already exist.
    Ensure that the directory is empty."""

    abs_path = os.path.abspath(destination_dir) + "/"
    file_pattern = abs_path

    if os.path.exists(file_pattern):
        # Delete everything in the directory.
        paths = pathlib.Path(abs_path).glob("**/*")
        dirs_to_delete = []

        paths = [p for p in paths if p != abs_path]  # exclude the top-level dir
        for p in paths:
            if os.path.isdir(p):
                dirs_to_delete += [p]
            else:
                if os.path.exists(p):
                    os.remove(path=p)

        dirs_to_delete = sorted(dirs_to_delete, key=lambda d: len(str(d)), reverse=True)

        for d in dirs_to_delete:
            os.rmdir(d)
    else:
        # Create a fresh directory.
        os.makedirs(abs_path)


def extract_zipped_code(zip_folder: str, destination_dir: str, dir_name: str):
    """
    Extracts the zip_folder to destination_dir and renames the folder to dir_name.
    """
    with zipfile.ZipFile(zip_folder, "r") as zip_ref:
        zip_ref.extractall(
            destination_dir
        )  # NOT SECURE. This might import files with ../ names to different directories.
    # change the name of the directory to dir_name
    code_dir = os.path.join(destination_dir, ZIP_FILENAME)
    new_code_dir = os.path.join(destination_dir, dir_name)
    os.rename(code_dir, new_code_dir)


def delete_unused_files(autogenerated_code_dir: str):
    FILES_TO_DELETE = ["git_push.sh"]
    if not os.path.exists(autogenerated_code_dir):
        typer.echo(f"{autogenerated_code_dir} does not exist.", err=True, color=True)
        raise typer.Exit(1)

    dirpath = os.path.abspath(autogenerated_code_dir)

    for filename in FILES_TO_DELETE:
        file_path = os.path.join(dirpath, filename)
        if os.path.exists(file_path):
            os.remove(file_path)


if __name__ == "__main__":
    typer_app()
