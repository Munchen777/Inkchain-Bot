from typing import Dict

from utils.networks import Ethereum, Ink
from utils.tools import get_accounts_data


CHAIN_NAMES: Dict[int, str] = {
    0: Ethereum.name,
    1: Ink.name,
}

ACCOUNT_NAMES, PRIVATE_KEYS, PROXIES = get_accounts_data()
