import os


GLOBAL_NETWORK = 1
SOFTWARE_MODE = 0                                    # 0 - consistently / 1 - parallel
SAVE_PROGRESS = True                                 # Save progress of modules execution
BREAK_ROUTE = False                                  # Break route in case of appearing error
TELEGRAM_NOTIFICATIONS = True                        # Enable Telegram Notification via Bot

STREAM = True                                        # True or False | Enables parallel mode

USE_PROXY: bool = True                               # Use proxy for wallets or not

ACCOUNTS_IN_STREAM = 5                               # Number of accounts in the stream

SHUFFLE_WALLETS = True                               # To mix accounts or not

SHUFFLE_ROUTE = False                                # Shuffle the assignments or not

WALLETS_TO_WORK: int | tuple | list = 0              # 0 - all accounts
                                                     # 1 - account No. 1
                                                     # 1, 7 - accounts 1 and 7
                                                     # [5, 25] - accounts 5 through 25 inclusive

'------------------------------------------------SLEEP CONTROL---------------------------------------------------------'
SLEEP_MODE = False               # True or False | Enables sleep after each account is used up
SLEEP_TIME_MODULES = (60, 80)    # (minimum, maximum) seconds | Sleep time between modules
SLEEP_TIME_ACCOUNTS = (40, 60)   # (minimum, maximum) seconds | Sleep time between accounts

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# Settings for Web3 activities (advanced users only)

MIN_AVAILABLE_BALANCE = int(100000000000000)                        # Minimum balance

RANDOM_RANGE = (0.01, 0.1)                                          # Range of random values

ROUNDING_LEVELS = (4, 7)                                            # Rounding levels
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

# EXCEL INFO
EXCEL_FILE_PATH: str = os.path.join(
    os.path.dirname(__file__),
    "data",
    "accounts.xlsx",
)

# TELEGRAM DATA
TG_TOKEN = ""  # https://t.me/BotFather
TG_ID = ""  # https://t.me/getmyid_bot

# OTHERS SETTINGS
LOGS_FILE_PATH: str = os.path.join(
    os.path.dirname(__file__),
    "data",
    "logs",
)
