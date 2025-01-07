import random
import os
import json
import asyncio

from datetime import datetime, timedelta
from web3 import AsyncWeb3
from eth_abi import encode
from curl_cffi.requests import AsyncSession
from typing import Union

from utils.core import*
from data.config import*
from generall_settings import MIN_AVAILABLE_BALANCE, RANDOM_RANGE, ROUNDING_LEVELS


class Worker():
    def __init__(self, client: Client):
        self.client: Client = client  

        