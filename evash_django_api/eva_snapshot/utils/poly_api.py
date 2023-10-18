import requests
import logging
import json
import os

from eva_snapshot.utils.exceptions import *

LOGGER = logging.getLogger("EVASnapshot v2")


class PolyApi:
    def __init__(self, region, account_id, project_id) -> None:
        """Api object used to make REST based calls to PolyAI's API.

        :param account_id: account_id (string) account id associated with 14IPs account in PolyAI
        :param project_id: project id associated with the project(brand: Marriott) in PolyAI
        """

        if region == 'EU':
            self.url = ''
        else: 
            self.url = 'https://api.us-1.platform.polyai.app/v1/'

        self.payload = {}
        self.headers = {"x-api-key": os.getenv(account_id)}  # collects key from tuple  
        self.account_id = account_id
        self.project_id = project_id


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
