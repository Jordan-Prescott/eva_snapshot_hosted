class EVASHError(Exception):
    """ EVA Snapshot Hosted Exceptions.
    """

    def __str__(self) -> str:
        return "An error occurred in the EVA Snapshot Hosted module. \
            Please check your configuration and try again."
