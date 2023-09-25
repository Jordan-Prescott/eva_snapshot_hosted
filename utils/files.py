import shutil
import zipfile
import os
import json
import yaml
import logging
from typing import Dict
from datetime import date

LOGGER = logging.getLogger("EVASnapshot v2")
TODAY = date.today().strftime("%d.%m.%Y")


def program_cleanup(project_folder, output_folder, archive_folder) -> bool:
    """Removes the previous download from the input folder and moves the previous output to the archive folder
    for backups. This cleans the folders of files that will affect the script if left by user.

    :param project_folder: Root folder api download
    :param output_folder: Folder the script outputs generated files to
    :param archive_folder: Archived storage of previous runs of script
    :return: True to indicate complete
    """

    try:
        shutil.rmtree(project_folder)  # remove previous download
    except FileNotFoundError:  # file already removed
        LOGGER.error(f"{project_folder} FileNotFoundError: May already have been removed")
        pass

    for file in os.listdir(output_folder):  # move previous output to archive
        shutil.move(output_folder + file, archive_folder)

    LOGGER.info(f"program_cleanup end.")
    return True


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
    :return: Returns True is file exist and False if not.
    """
    if os.path.exists(path):
        return True
    if not os.path.exists(path):
        LOGGER.error(f"check_file_exists: {path} does not exist.")
        False
    LOGGER.info(f"check_file_exists end.")


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

    with open(path, 'r') as variant_data:
        yaml_data = yaml.load(
            variant_data.read(), Loader=yaml.FullLoader
        )
    LOGGER.info(f"load_yaml_data_from_file end.")
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
