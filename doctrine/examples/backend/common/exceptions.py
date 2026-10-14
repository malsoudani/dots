class BusinessError(Exception):
    """An expected failure. `message` is shown to the end user verbatim (BE-API-3)."""

    status_code = 400

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class InvalidRequest(BusinessError):
    """The request could not be parsed into its request domain."""
