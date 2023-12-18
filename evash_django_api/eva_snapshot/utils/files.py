import shutil
import zipfile
import os
import json
import yaml
import logging
from typing import Dict
from datetime import date

from eva_snapshot.utils.exceptions import *

LOGGER = logging.getLogger("EVASnapshot v2")
TODAY = date.today().strftime("%d.%m.%Y")

def unpack_project_download(download, project_folder, project_zipped) -> bool:
    """Stores the contents of the download to the local file system. First unzips and stores and then
    deletes zipped folder.

    :param download: Downloaded project from API call.
    :param project_folder: Folder the download will be unzipped to.
    :param project_zipped: Name of the ZIP file the form the downloads contents.
    :return: True to indicate complete.
    """

    with open(project_zipped, "wb") as file:
        file.write(download.content)

    with zipfile.ZipFile(project_zipped) as zip_ref:
        zip_ref.extractall(project_folder)
    os.remove(project_zipped)

    LOGGER.info(f"unpack_project_download end.")
    return True


def check_file_exists(path) -> bool:
    """Takes a path to a file and checks the file exists.

    :param path: Path to the file the function checks exists.
    :return: Returns True is file exist and rasies EVASHFilesNotLoaded.
    """
    if os.path.exists(path):
        return True
    if not os.path.exists(path):
        LOGGER.critical(f"Core file not found at path: {path}")
        raise EVASHFilesNotLoaded


def load_json_data_from_file(path) -> Dict:
    """Takes path to JSON file and loads file into Python Dict Object.

    :param path: Path to file that will be loaded into Python Dict Object.
    :return: Python Dict object.
    """

    with open(path, 'r') as data:
        return json.loads(data.read())
    LOGGER.info(f"load_json_data_from_file end.")


def load_yaml_data_from_file(path) -> Dict:
    """Takes path to YAML file and loads file into Python Dict Object.

    :param path: Path to file that will be loaded into Python Dict Object.
    :return: Python Dict object.
    """

    with open(path, 'r', errors='replace', encoding='utf-8') as variant_data:
        yaml_data = yaml.load(
            variant_data.read(), Loader=yaml.FullLoader
        )
    LOGGER.info(f"{path} - load_yaml_data_from_file end.")        
    return yaml_data


def make_directory(path):
    """takes in a path and creates a new directory if dir does not already exist

    :param path: Path to directory.
    :return: Returns True to indicate complete.
    """

    if not os.path.exists(path):
        os.mkdir(path)
    return True


def copy_files_to_dest(source_dir, target_dir) -> bool:
    """takes in source directory and new target directory which will copy all files from source, create new target
    directory and paste all files into new directory.

    :param source_dir: Directory where source files are located.
    :param target_dir: Directory which will be created and source files copied to.
    :return: Returns True to indicate complete.
    """

    shutil.copytree(source_dir, target_dir)
    return True

def remove_folder(path):
    """takes in path to folder which will be removed if found and path given is a direactory.
    If path given an error will be raised to indicate path cant be found. 
    """

    if os.path.exists(path) and os.path.isdir(path):
        shutil.rmtree(path)
    else: 
        raise EVASHFolderNotFound
    