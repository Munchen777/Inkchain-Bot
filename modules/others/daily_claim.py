from web3 import AsyncWeb3
from web3.contract import AsyncContract
from web3.contract.async_contract import AsyncContract
from web3.eth.async_eth import ChecksumAddress

from modules import *
from utils.client import Client
from data.abi import DAILY_GM
from modules.interfaces import *


class ClaimDailyGMWorker(Logger):
    def __init__(self, client: Client, module_info: ClaimDailyGMModule):
        super().__init__()
        self.client: Client = client
        self.module_info: ClaimDailyGMModule = module_info

    async def run(self):
        address_contract: ChecksumAddress = AsyncWeb3.to_checksum_address(
            '0x9F500d075118272B3564ac6Ef2c70a9067Fd2d3F'
        )

        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract,
            abi=DAILY_GM
        )

        try:
            tx_params = await self.client.prepare_transaction()
            transaction = await contract.functions.gm().build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed Claim Daily GM. Error: {error} '
            )