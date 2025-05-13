from typing import Any


class APIError(Exception):
    """
    Basic class for API exceptions.

    Attributes:
        BASE_MESSAGES (list): List of base error messages
        error (str): Error description
        response_data (dict, optional): API response data
    """
    BASE_MESSAGES = ["refresh your captcha!!", "Incorrect answer. Try again!"]

    def __init__(self, error: str, response_data: dict = None):
        """
        Initializes the APIError instance.

        Args:
            error (str): Error message
            response_data (dict, optional): API response data. Defaults to None.
        """
        self.error = error
        self.response_data = response_data

    @property
    def error_message(self) -> str:
        """
        Returns the error message from the response data if available.

        Returns:
            str: Error message or None if message is missing
        """
        if self.response_data and "message" in self.response_data:
            return self.response_data["message"]

    def __str__(self) -> str:
        """
        Returns the string representation of the error.

        Returns:
            str: Error description
        """
        return self.error


class SessionRateLimited(Exception):
    """
    Exception raised when the session request limit is exceeded.

    Used when the API returns a rate limit error for the current session.
    """


class CaptchaSolvingFailed(Exception):
    """
    Exception raised when the CAPTCHA solving attempt fails.

    Indicates a problem with automatic CAPTCHA solving.
    """


class ServerError(APIError):
    """
    Exception for server-side errors.

    Inherits from APIError and is used to handle server-side API errors.
    """

class BlockchainError(Exception):
    """
    Base class for blockchain-related errors.
    
    Used as a parent class for all blockchain-related exceptions.
    """


class ContractError(Exception):
    """
    Base class for contract-related errors.

    Used as a parent class for all contract-related exceptions.
    """


class HttpStatusError(APIError):
    def __init__(
        self,
        message: str,
        status_code: int,
        response_data: Any = None,
        ) -> None:
        super().__init__(message, response_data)
        self.status_code: int = status_code
