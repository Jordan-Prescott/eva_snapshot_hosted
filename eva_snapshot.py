import argparse
import logging
import ast
from logging.handlers import SysLogHandler
from utils import files
from utils.poly_api import PolyApi
from utils.parsing import flow_module, GraphvizModule, UniverseGraphVizModule
from utils.store.data_store import DataStore

PAPERTRAIL = ("logs3.papertrailapp.com", 32517)

OUTPUT_FOLDER = "./output/"
PROJECT_FOLDER = "./input/project_download"
PROJECT_DOWNLOAD_NAME = "project_download.zip"

# List of files that are used in the programming of EVA but not needed in output and therefore avoided.
FILES_NOT_NEEDED = [
    "main", "global", "handoff", "send_sms", "small_talk", "hotel_directory", "follow_up", "csat_survey",
    "who_are_you", "csat_survey_copy"
]


def main():
    """main method that manages user input and orchestrates programs operations.
    """
    
    api = PolyApi(ACCOUNT_ID, PROJECT_ID)

    download = api.download_project()
    # TODO: Review this code if its the best way to achieve this
    if download is False:
        logger.error("1/2 API call failed")
        print(f"""
        ERROR: API call unsuccessful with Account ID: {ACCOUNT_ID} and Project ID: {PROJECT_ID}.
        Please review and enter again.\n""")
        api.ACCOUNT_ID = input("Enter Account ID: ")
        api.PROJECT_ID = input("Enter Project ID: ")

        download = api.download_project()
        if download is False:
            logger.critical("2/2 API call failed")
            print("""
            ERROR: API call failed again. This means either details you are entering are incorrect OR PolyAI's
            API is having issues. Please investigate and run script again.\n""")
            exit()

    files.unpack_project_download(download, PROJECT_FOLDER, PROJECT_DOWNLOAD_NAME)

    for index, path in enumerate(CORE_FILES):
        # TODO: Review this code if its the best way to achieve this
        if not files.check_file_exists(path):
            logger.error(f"1/2 file checks failed: {path}")
            print(f"""
                    ERROR: The file located at {path} could not be found.
                    Please review and enter the correct path.\n""")
            path = input("Enter Correct Path: ")

            if not files.check_file_exists(path):
                logger.critical(f"2/2 file checks failed: {path}")
                print(f"""
                ERROR: The file located at {path} could not be found. The script needs this file to build the generate
                the output. Please check the ./input/project_download as well as the PolyAI studio. The script downloads
                this file structure from the studio so you will encounter this issue again when running the script but
                knowing the path you can amend in the above.\n""")
                exit()
            else:
                CORE_FILES[index] = path

    store = DataStore(SITE_CODE, CORE_FILES, FILES_NOT_NEEDED)
    print("Core files loaded.")

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
    print("File parsing complete.")

    # generate outputs
    # Makes dir as well as copy over media files for output
    uni = UniverseGraphVizModule()
    files.copy_files_to_dest(source_dir="./lib/media/output_media/", target_dir=f"{OUTPUT_FOLDER}{SITE_CODE}/")
    for flow in flows:
        flow_chart = GraphvizModule(flow, f"{OUTPUT_FOLDER}{SITE_CODE}/", store)
        uni.graphs.append(flow_chart.dot)
    print("Single flow files generated.")

    uni.build_universe(f"{OUTPUT_FOLDER}{SITE_CODE}/")
    print("Universe file generated.")


if __name__ == '__main__':
    """
    company: FourteenIP Communications
    author: Jordan Prescott
    support: aisupport@fourteenip.com
    
    gitHub: https://github.com/Jordan-Prescott/EVASnapshot-uni
    """

    # This code is designed for server side - uncomment in phase 2
    # parser = argparse.ArgumentParser(
    #     description="""Generate visual call flows for ACCOUNT_ID and PROJECT_ID passed in.
    #     Stores USERNAME and SITE_CODE for log."""
    # )
    # parser.add_argument(
    #     "--USERNAME",
    #     help="USERNAME for log",
    #     required=False
    # )
    # parser.add_argument(
    #     "--SITE_CODE",
    #     help="target site code for output",
    #     required=False
    # )
    # parser.add_argument(
    #     "--ACCOUNT_ID",
    #     help="account id site is hosted under in PolyAI platform",
    #     required=False
    # )
    # parser.add_argument(
    #     "--PROJECT_ID",
    #     help="project id of the project in PolyAI platform",
    #     required=False
    # )
    #
    # # capture arguments passed in
    # args = parser.parse_args()
    # USERNAME = args.USERNAME
    # SITE_CODE = args.SITE_CODE
    # ACCOUNT_ID = args.ACCOUNT_ID
    # PROJECT_ID = args.PROJECT_ID

    # setup logging
    logger = logging.getLogger("EVASnapshot v2")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler = SysLogHandler(address=(PAPERTRAIL[0], PAPERTRAIL[1]))
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    print("EVASnapshot v2\n")
    
    USERNAME = input("Username: ")
    SITE_CODE = input("Site Code: ")
    ACCOUNT_ID = input("Account ID: ")
    PROJECT_ID = input("Project ID: ")
    logger.info(f"USERNAME: {USERNAME}, SITE_CODE: {SITE_CODE}, ACCOUNT ID: {ACCOUNT_ID}, PROJECT ID: {PROJECT_ID}")

    # Each script is critical to the output of the script. Read README for more details
    CORE_FILES = [
        f"./input/project_download/data_store/live/{SITE_CODE.lower()}/handoff",
        f"./input/project_download/data_store/live/{SITE_CODE.lower()}/sms_content_map",
        "./input/project_download/agent_configuration/domain/variants.yaml",
        "./input/project_download/agent_configuration/domain/utterances.en-US.yaml"
    ]

    main()
    print("\nScript End.")
