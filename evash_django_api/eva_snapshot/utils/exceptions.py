class EVASHError(Exception):
    """EVA Snapshot Hosted Exceptions.
    """

    def __str__(self) -> str:
        return "An error occurred in the EVA Snapshot Hosted module. \
            Please check your configuration and try again."

class EVASHApiCallFail(EVASHError):
    """API call to download project failed.
    """

    def __str__(self) -> str:
        return f"Failed to download project export in API. Please account_id, project_id, \
region, and group_id"

class EVASHFilesNotLoaded(EVASHError):
    """Core files needed to generate output have not been found.
    """

    def __str__(self) -> str:
        return f"Failed to load core files. Please check the name and path in Poly platform."
    
class EVASHFolderNotFound(EVASHError):
    """Folder needed to perform action cannot be found. 
    """

    def __str__(self) -> str:
        return f"Path given did not find folder. Please review folder path given and\
end desination is a directory."