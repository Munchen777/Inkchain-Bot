import openpyxl
import os
import sys

from better_proxy import Proxy
from typing import Dict, List, Set

from generall_settings import EXCEL_FILE_PATH
from modules import Logger
from openpyxl.utils.exceptions import InvalidFileException


logger: Logger = Logger().get_logger()


def get_accounts_data():
    try:
        try:
            workbook = openpyxl.load_workbook(EXCEL_FILE_PATH, read_only=True)
            sheet = workbook.active

        except InvalidFileException as error:
            logger.critical(f"Error for trying to open a non-ooxml file. Error {error}")
            sys.exit(1)

        except FileNotFoundError as error:
            logger.error("The file accounts.xlsx was not found")
            return

        except IsADirectoryError as error:
            logger.critical("Are you sure about excel file? Please, pass an excel file")
            sys.exit(1)

        account_names, private_keys, proxies = [], [], []

        for row in sheet.iter_rows():
            account_name = row[0].value
            private_key = row[1].value
            proxy = row[2].value

            if not all([account_name, private_key, proxy]):
                continue

            account_names.append(str(account_name) if isinstance(account_name, (str, int)) else None)
            private_keys.append(private_key if private_key else None)
            proxies.append(
                Proxy.from_str(
                    proxy=proxy.strip() if "://" in proxy.strip() else f"http://{proxy.strip()}"
                ).as_url
                if isinstance(proxy, str) else None
            )

        return account_names, private_keys, proxies

    except Exception as error:
        logger.error(f"Error in get_accounts_data function! Error: {error}")
        sys.exit(1)


def clean_progress_file():
    """
    Function to clean wallets progress file

    """
    with open("./data/service/wallets_progress.json", "w") as file:
        file.truncate(0)


def check_progress_file() -> bool:
    """
    Check if wallets_progress file is empty

    """
    file_path = './data/services/wallets_progress.json'

    if os.path.getsize(file_path) > 0:
        return True
    else:
        return False


def topological_sort(graph: Dict[str, List[str]]) -> List[str]:
    visited: Set[str] = set()
    stack: List[str] = []

    def dfs(module_name: str):
        visited.add(module_name)

        for neighbour in graph.get(module_name, []):
            if neighbour not in visited:
                dfs(neighbour)

        stack.append(module_name)

    for module_name in graph:
        if module_name not in visited:
            dfs(module_name)

    return stack[::-1]
