class WalletError(Exception):
    """
    Base class for wallet-related errors.

    Used as a parent class for all wallet-related exceptions.
    """

class ConfigurationError(Exception):
    """
    Base class for configuration errors.

    Used for handling errors related to application settings.
    """

class InsufficientFundsError(WalletError):
    """
    Exception for insufficient funds on wallet.

    Occurs when it's not enough to complete an operation.
    """
