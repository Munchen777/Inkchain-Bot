import re

from faker import Faker
from web3 import AsyncWeb3

from modules import *
from utils.client import Client
from modules.interfaces import *
from data.abi import ZNS_CONNECT

faker = Faker()


class BuyZNCDomenInkWorker(Logger):
    def __init__(self, client: Client, module_info: BuyZNCDomenInkModule):
        super().__init__()
        self.client: Client = client

    async def run(self):
        self.logger.info(
            f'{self.client.name} Buy ZNC domen in the Ink network'
        )

        contract_address = AsyncWeb3.to_checksum_address(
            '0xFb2Cd41a8aeC89EFBb19575C6c48d872cE97A0A5'
        )

        contract = self.client.w3.eth.contract(
            address=contract_address, abi=ZNS_CONNECT
        )

        while True:
            domain_name = faker.domain_name()
            name = re.split(r'\.', domain_name)[0]

            owners = [self.client.address]
            domain_names = [name]
            expiries = [1]
            referral = AsyncWeb3.to_checksum_address('0x0000000000000000000000000000000000000000')
            credits = 0

            length_of_domain = len(domain_names[0])

            price = await contract.functions.priceToRegister(length_of_domain).call()

            try:
                tx_params = await self.client.prepare_transaction(value=price)
                transaction = await contract.functions.registerDomains(
                    owners,
                    domain_names,
                    expiries,
                    referral,
                    credits
                ).build_transaction(tx_params)
                await self.client.send_transaction(transaction, need_hash=True)
            except Exception as error:
                if '0x3a81d6fc' in str(error):
                        logger.warning(f"Domain {domain_names} already registered, skipping...")
                        continue
                else:
                    self.logger.error(  
                        f'{self.client.name} Buy ZNC domen. Error: {error} '
                    )
            return