import json
import os
import parser
from pathlib import Path
import shutil
import neocities
import argparse

DIST_DIR = Path("dist")
RECIPE_INPUT_DIR = Path("recipes")
RECIPE_OUTPUT_DIR = DIST_DIR / "recipes"
CLIENT_INPUT_DIR = Path("client")
CLIENT_OUTPUT_DIR = DIST_DIR
NEOCITIES_DIR = "recipes"

def write_recipe_file(recipe_obj, filename):
    with open(filename, "w") as output_file:
        json.dump(recipe_obj, output_file, indent=2)


def write_recipe_list_file(recipe_list):
    with open("dist/recipe_list.json", "w") as output_file:
        json.dump(recipe_list, output_file, indent=2)


def parse_file(filename):
    with open(filename) as recipe:
        return parser.parse_recipe(recipe)


def process_recipe_file(direntry):
    recipe_id = os.path.splitext(direntry.name)[0]
    filename = "{}.json".format(recipe_id)
    output_path = RECIPE_OUTPUT_DIR / filename
    recipe_obj = parser.parse_file(direntry.path)
    write_recipe_file(recipe_obj, output_path)
    return (recipe_obj, recipe_id)


def process_all_recipe_files(recipe_dir):
    recipe_list = []
    with os.scandir(recipe_dir) as it:
        for entry in it:
            if entry.is_file():
                (recipe, file) = process_recipe_file(entry)
                recipe_list.append({ "title": recipe["title"], "id": file})
    write_recipe_list_file(recipe_list)


def copy_file(source, dest):
    shutil.copy(source, dest)


def copy_files(source, dest):
    with os.scandir(source) as it:
        for entry in it:
            if entry.is_file():
                dst_path = dest / entry.name
                copy_file(entry.path, dst_path)

def do_publish(api_key_file, remote_dir):
    with open(api_key_file) as file:
        key = file.readline()
    neocities.sync_neocities(str(DIST_DIR), key, remote_dir)

def do_package():
    RECIPE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    copy_files(CLIENT_INPUT_DIR, CLIENT_OUTPUT_DIR)
    process_all_recipe_files(RECIPE_INPUT_DIR)


aparser = argparse.ArgumentParser()
aparser.add_argument(
    "task",
    help="the build task to perform",
    choices=["package", "publish"]
)
aparser.add_argument(
    "-k", "--api-key-file",
    help="file containing api key for neocities.org"
)



args = aparser.parse_args()

if args.task == "package":
    do_package()
else:
    assert args.task == "publish"
    assert "api_key_file" in args and args.api_key_file
    do_publish(args.api_key_file, NEOCITIES_DIR)

