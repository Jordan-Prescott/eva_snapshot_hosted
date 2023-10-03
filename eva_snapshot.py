import argparse
import logging
import ast
from logging.handlers import SysLogHandler

from utils.exceptions import *
from utils import files
from utils.poly_api import PolyApi
from utils.parsing import flow_module, GraphvizModule, UniverseGraphVizModule
from utils.store.data_store import DataStore

PAPERTRAIL = ("logs3.papertrailapp.com", 32517)

CUSTOMER_EMAIL = ""
SITE_CODE = ""
ACCOUNT_ID = ""
PROJECT_ID = ""
API_URL = ""
API_TOKEN = ""

OUTPUT_FOLDER = "./output/"
PROJECT_FOLDER = "./input/project_download"
PROJECT_DOWNLOAD_NAME = "project_download.zip"

# Each file is critical to the output of the script, read README for more details. List populated in args.
CORE_FILES = []

# List of files that are used in the programming of EVA but not needed in output and therefore avoided.
FILES_NOT_NEEDED = [
    "main", "global", "handoff", "send_sms", "small_talk", "hotel_directory", "follow_up", "csat_survey",
    "who_are_you", "csat_survey_copy"
]


def main():
    """main method that manages user input and orchestrates programs operations.
    """
    api = PolyApi(API_URL, API_TOKEN, ACCOUNT_ID, PROJECT_ID)
    download = api.download_project()
    files.unpack_project_download(download, PROJECT_FOLDER, PROJECT_DOWNLOAD_NAME)

    # checks core files are found
    for path in CORE_FILES.values():
        files.check_file_exists(path)

    store = DataStore(SITE_CODE, CORE_FILES, FILES_NOT_NEEDED)

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

        flow_path = f"{PROJECT_FOLDER}/agent_configuration/{location}{filename}.py"
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
    files.copy_files_to_dest(source_dir="./data/output_media/", target_dir=f"{OUTPUT_FOLDER}{SITE_CODE}/")
    for flow in flows:
        flow_chart = GraphvizModule(flow, f"{OUTPUT_FOLDER}{SITE_CODE}/", store)
        uni.graphs.append(flow_chart.dot)

    uni.build_universe(f"{OUTPUT_FOLDER}{SITE_CODE}/")

    


if __name__ == '__main__':
    """
    company: FourteenIP Communications
    author: Jordan Prescott
    support: aisupport@fourteenip.com
    
    gitHub: https://github.com/Jordan-Prescott/eva_snapshot_hosted
    """

    parser = argparse.ArgumentParser(
        description="""Generate visual call flows for ACCOUNT_ID and PROJECT_ID passed in.
        Stores USERNAME and SITE_CODE for log."""
    )
    parser.add_argument(
        "--CUSTOMER_EMAIL",
        help="USERNAME for log",
        required=False
    )
    parser.add_argument(
        "--SITE_CODE",
        help="target site code for output",
        required=False
    )
    parser.add_argument(
        "--ACCOUNT_ID",
        help="account id site is hosted under in PolyAI platform",
        required=False
    )
    parser.add_argument(
        "--PROJECT_ID",
        help="project id of the project in PolyAI platform",
        required=False
    )
    parser.add_argument(
        "--API_URL",
        help="Base url of API to download project backup.",
        required=False
    ) 
    parser.add_argument(
        "--API_TOKEN",
        help="API token needed to authenticate and request project.",
        required=False
    )
    
    # capture arguments passed in
    args = parser.parse_args()
    CUSTOMER_EMAIL = args.CUSTOMER_EMAIL
    SITE_CODE = args.SITE_CODE
    ACCOUNT_ID = args.ACCOUNT_ID
    PROJECT_ID = args.PROJECT_ID
    API_URL = args.API_URL
    API_TOKEN = args.API_TOKEN

    # populate core files
    CORE_FILES.append(f"./input/project_download/data_store/live/{SITE_CODE.lower()}/handoff")
    CORE_FILES.append(f"./input/project_download/data_store/live/{SITE_CODE.lower()}/sms_content_map")
    CORE_FILES.append("./input/project_download/agent_configuration/domain/variants.yaml")
    CORE_FILES.append("./input/project_download/agent_configuration/domain/utterances.en-US.yaml")

    # setup logging
    logger = logging.getLogger("EVASnapshot v2")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler = SysLogHandler(address=(PAPERTRAIL[0], PAPERTRAIL[1]))
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    logger.info(f"CUSTOMER_EMAIL: {CUSTOMER_EMAIL}, SITE_CODE: {SITE_CODE}, ACCOUNT ID: {ACCOUNT_ID}, PROJECT ID: {PROJECT_ID}")
   
    main()
    print("\nThe End.")
