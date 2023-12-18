import argparse
import logging
import ast
from logging.handlers import SysLogHandler

from eva_snapshot.utils.exceptions import *
from eva_snapshot.utils import files
from eva_snapshot.utils.poly_api import PolyApi
from eva_snapshot.utils.parsing import flow_module, GraphvizModule, UniverseGraphVizModule
from eva_snapshot.utils.store.data_store import DataStore

PAPERTRAIL = ("logs3.papertrailapp.com", 32517)

# demo
OUTPUT_FOLDER = "./eva_snapshot/output/"
#OUTPUT_FOLDER = "./evash_django_api/eva_snapshot/output/"
OUTPUT_FOLDER_FLOWS = f"{OUTPUT_FOLDER}flows/"
#OUTPUT_FOLDER_FLOWS = f"{OUTPUT_FOLDER}flows/"

PROJECT_FOLDER = "./eva_snapshot/input/project_download"
PROJECT_DOWNLOAD_NAME = "project_download.zip"

# Each file is critical to the output of the script, read README for more details. List populated in args.
CORE_FILES = []

# List of files that are used in the programming of EVA but not needed in output and therefore avoided.
FILES_NOT_NEEDED = [
    "main", "global", "handoff", "send_sms", "small_talk", "hotel_directory", "follow_up", 
    "csat_survey", "who_are_you", "csat_survey_copy", "hotel_directory", "hotel_directory_copy", 
    "test", "admin_trigger_fallback"
]


def main(account_id, project_id, group_id, region, customer_email):
    """
    company: FourteenIP Communications
    author: Jordan Prescott
    support: aisupport@fourteenip.com
    
    gitHub: https://github.com/Jordan-Prescott/eva_snapshot_hosted
    
    
    main method that manages user input and orchestrates programs operations.
    """

    # setup logging
    logger = logging.getLogger("EVASnapshot v2")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler = SysLogHandler(address=(PAPERTRAIL[0], PAPERTRAIL[1]))
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    logger.info(f"CUSTOMER EMAIL: {customer_email}, GROUP ID: {group_id}, ACCOUNT ID: {account_id}, PROJECT ID: {project_id}")
   
    CORE_FILES.append(f"./eva_snapshot/input/project_download/data_store/live/{group_id.lower()}/handoff")
    CORE_FILES.append(f"./eva_snapshot//input/project_download/data_store/live/{group_id.lower()}/sms_content_map")
    CORE_FILES.append("./eva_snapshot//input/project_download/agent_configuration/domain/variants.yaml")
    CORE_FILES.append("./eva_snapshot//input/project_download/agent_configuration/domain/utterances.en-US.yaml")

    api = PolyApi(region, account_id, project_id)
    download = api.download_project()
    files.unpack_project_download(download, f"./{PROJECT_FOLDER}", PROJECT_DOWNLOAD_NAME)

    # checks core files are found
    for path in CORE_FILES:
        files.check_file_exists(path)

    store = DataStore(group_id, CORE_FILES, FILES_NOT_NEEDED)

    flows = []
    # parsing python files appending complete flow to flows[]
    for active_flow in store.variant.flows:
        location = "policy/"  # Highest folder in directory
        try:
            filename = active_flow.split('.')[1]
            location += active_flow.split('.')[0] + "/"  # Needed '/' for flow_path splitting location and filename
        except IndexError:
            logger.error(f"IndexError splitting location to filename: {active_flow}" )
            filename = active_flow

        flow_path = f"./eva_snapshot/input/project_download/agent_configuration/{location}{filename}.py"   

        #flow_path = f"./evash_django_api/eva_snapshot/input/project_download/agent_configuration/{location}{filename}.py"
        with open(flow_path) as flow_file:
            code_tree = ast.parse(flow_file.read())

            # set position to start of file and read whole file
            flow_file.seek(0)
            file_in_list = flow_file.readlines()

            ast_mod = flow_module(filename, code_tree, file_in_list, store.files_not_needed)

            if not ast_mod is None:
                flows.append(ast_mod)

    # generate outputs
    # Makes dir as well as copy over media files for output
    uni = UniverseGraphVizModule()

    files.copy_files_to_dest(source_dir="./eva_snapshot/data/output_media/", target_dir=f"{OUTPUT_FOLDER}{group_id}/")
  
    for flow in flows:
        flow_chart = GraphvizModule(flow, f"{OUTPUT_FOLDER}{group_id}/flows/", store)
        uni.graphs.append(flow_chart.dot)

    uni.build_universe(f"{OUTPUT_FOLDER}{group_id}/flows/")
    CORE_FILES.clear()
