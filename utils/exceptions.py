class EVASHError(Exception):
    """ EVA Snapshot Hosted Exceptions.
    """

    def __str__(self) -> str:
        return "An error occurred in the EVA Snapshot Hosted module. \
            Please check your configuration and try again."

class EVASHApiCallFail(EVASHError):
    """ API call to download project failed.
    """

    def __str__(self) -> str:
        return f"Failed to download project export in API. Please check URL, token,\
project_id, and account_id."

class EVASHFilesNotLoaded(EVASHError):
    """ Core files needed to generate output have not been found.
    """

    def __str__(self) -> str:
        return f"Failed to load core files. Please check the name and path in Poly platform."