import requests
import logging
import json
import os

from utils.exceptions import *

LOGGER = logging.getLogger("EVASnapshot v2")


class PolyApi:

    __instance = None

    @staticmethod
    def get_instance():
        if PolyApi.__instance is None:
            PolyApi("account_id", "project_id")
        return PolyApi.__instance

    def __init__(self, url: str, token: str, account_id: str, project_id: str) -> None:
        """Api object used to make REST based calls to PolyAI's API.

        :param account_id: account_id (string) account id associated with 14IPs account in PolyAI
        :param project_id: project id associated with the project(brand: Marriott) in PolyAI
        """
        if PolyApi.__instance is not None:
            raise Exception("Singleton cannot be instantiated more than once.")
        else:
            self.url = url
            self.payload = {}
            self.headers = {"x-api-key": token}  # collects key from tuple
            self.account_id = account_id
            self.project_id = project_id

            PolyApi.__instance = self


    def download_project(self):
        """makes GET call to PolyAI API to download project. Return files if call was successful and False if
        un-successful.

        :return: Either contents of downloaded program if call was successful or raise EVASHApiCallFail.
        """

        endpoint_url = f"{self.url}{self.account_id}/{self.project_id}/projects/zip"
        response = requests.get(endpoint_url, headers=self.headers)

        if response.status_code == 200:  
            LOGGER.info(f"download_project: API call successful")
            return response
        else:  
            LOGGER.critical(f"API call failed to download project.")
            raise EVASHApiCallFail