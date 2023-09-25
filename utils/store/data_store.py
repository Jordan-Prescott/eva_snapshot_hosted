import logging

from utils import files
from store.data_entities import Variant

LOGGER = logging.getLogger("EVASnapshot v2")


class DataStore:
    def __init__(self, variant_id, data_files: list, bad_files: list):
        """Loads and stores all data into program used as a central point of resource for core data when needed
        in program such as the target variant as well as utterances needed.

        :param variant_id: ID of the variant targeted.
        :param data_files: List of paths to files needed in program.
        :param bad_files: List of files that are not needed for the output as well do not fit the logic of program and
        should be avoided when parsing.
        """

        # unpack list and store as variables
        handoff, sms, variants, utterances = data_files

        self.variant = Variant(variant_id.upper())
        self.variant.handoff = files.load_json_data_from_file(handoff)
        self.variant.sms = files.load_json_data_from_file(sms)

        variant_dict = files.load_yaml_data_from_file(
            variants
        )
        flows = []
        for flow in variant_dict['variants'][self.variant.variant_id]['active_flows']:  # Get only target variant flows
            flows.append(flow)
        self.variant.flows = flows

        self.utterance_dict = files.load_yaml_data_from_file(
            utterances
        )
        self.files_not_needed = bad_files

        LOGGER.info("DataStore end.")
