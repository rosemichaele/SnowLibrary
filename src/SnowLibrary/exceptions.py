class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class QueryNotExecuted(Error):
    """Raised when it is expected that a query has already been executed, but was not in SnowLibrary.RESTQuery."""
    def __init__(self, message):
        self.message = message
