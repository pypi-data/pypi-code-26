import glob, textwrap
from os.path import join, isfile, isdir, exists
from os import getcwd
from kooki.config import get_kooki_dir_recipes, get_kooki_dir_jars
from kooki.tools import get_file_extension
from kooki.exception import TooMuchResult


def search_jar(jar):
    ret_jar_path = None
    user_jars_dir = get_kooki_dir_jars()
    jar_path = join(user_jars_dir, jar)
    if isdir(jar_path):
        ret_jar_path = jar_path
    return ret_jar_path


def search_recipe(recipe):
    ret_recipe_path = None
    user_recipes_dir = get_kooki_dir_recipes()
    recipe_path = join(user_recipes_dir, recipe)
    if isdir(recipe_path):
        ret_recipe_path = recipe_path
    return ret_recipe_path


def get_search_paths(jars, recipe):
    directories = []
    directories.append(get_local_path())
    directories += get_jars_path(jars, recipe)
    return directories


def get_local_path():
    return getcwd()


def get_jars_path(jars, recipe):
    user_jars_dir = get_kooki_dir_jars()
    directories = []
    for jar in jars:
        jar_path = join(user_jars_dir, jar)
        resource_jar_path = join(jar_path)
        directories.append(resource_jar_path)
        recipe_resource_jar_path = join(jar_path, recipe)
        directories.append(recipe_resource_jar_path)
    return directories


def search_file(jars, recipe, filename):
    ret_file_path = None
    ret_file_path = search_file_in_local(filename)
    if not ret_file_path:
        ret_file_path = search_file_in_jars(jars, recipe, filename)
    return ret_file_path


def search_file_in_local(filename):
    ret_file_path = None
    file_path = join(getcwd(), filename)
    ret_file_path = search_file_in_path(file_path)
    return ret_file_path


def search_file_in_jars(jars, recipe, filename):
    user_jars_dir = get_kooki_dir_jars()
    ret_file_path = None
    for jar in jars:
        jar_path = join(user_jars_dir, jar)
        ret_file_path = search_file_in_jar(jar_path, recipe, filename)
        if ret_file_path:
            break
    return ret_file_path


def search_file_in_jar(jar_path, recipe, filename):
    ret_file_path = search_file_in_jar_recipe(jar_path, recipe, filename)
    if not ret_file_path:
        ret_file_path = search_file_in_jar_local(jar_path, filename)
    return ret_file_path


def search_file_in_jar_recipe(jar_path, recipe, filename):
    ret_file_path = None
    recipe_jar_path = join(jar_path, recipe)
    file_path = join(recipe_jar_path, filename)
    ret_file_path = search_file_in_path(file_path)
    return ret_file_path


def search_file_in_jar_local(jar_path, filename):
    ret_file_path = None
    file_path = join(jar_path, filename)
    ret_file_path = search_file_in_path(file_path)
    return ret_file_path


def search_file_in_path(file_path):
    if isdir(file_path):
        return file_path
    else:
        extension = get_file_extension(file_path)
        result = glob.glob('{}.*'.format(file_path))

        if extension == '':
            result = glob.glob('{}.*'.format(file_path))
            if len(result) == 1:
                return result[0]
            elif len(result) > 1:
                raise TooMuchResult(file_path, result)
            return None
        else:
            if isfile(file_path):
                return file_path
            else:
                return None
