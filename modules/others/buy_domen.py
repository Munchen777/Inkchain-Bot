import re

from faker import Faker
from curl_cffi.requests import AsyncSession

from modules import *
from utils.client import Client, CustomAsyncWeb3
from modules.interfaces import *
from data.abi import ZNS_CONNECT

faker = Faker()


class BuyZNCDomenInkWorker(Logger):
    def __init__(self, client: Client, module_info: BuyZNCDomenInkModule):
        super().__init__()
        self.client: Client = client

    async def get_availability_domen(self):
        headers = {
            'accept': '*/*',
            'referer': f'https://explorer.inkonchain.com/address/{self.client.address}',
            'user-agent': self.client.get_user_agent(),
        }

        try:
            async with AsyncSession() as session:
                response = await session.get(
                    f'https://explorer.inkonchain.com/api/v2/addresses/{self.client.address}/transactions',
                    headers=headers,
                    proxy=self.client.proxy_init,
                )

                if response.status_code == 200:
                    transactions = response.json()

                    for tx in transactions['items']:
                        if (tx.get('status') == 'ok' and 
                            tx.get('method') == 'registerDomains'):
                            return True
                    
                    return False
                    
                else:
                    self.logger.error(f"{self.client.name} Request failed with status code: {response.status_code}")
                    return False

        except Exception as error:
            self.logger.error(f'{self.client.name} Failed request:  {error}')
            return False

    async def run(self):
        availability_contract = await self.get_availability_domen()
        if availability_contract:
            self.logger.info(
                f'{self.client.name} ZNC domen on the Ink network has previously been acquired'
            )
            return True
        
        self.logger.info(
            f'{self.client.name} Buy ZNC domen in the Ink network'
        )

        contract_address = CustomAsyncWeb3.to_checksum_address(
            '0xFb2Cd41a8aeC89EFBb19575C6c48d872cE97A0A5'
        )

        contract = self.client.w3.eth.contract(
            address=contract_address, abi=ZNS_CONNECT
        )

        while True:
            while True:
                domain_name = faker.domain_name()
                name = re.split(r'\.', domain_name)[0]
                if len(name) > 5:
                    break

            owners = [self.client.address]
            domain_names = [name]
            expiries = [1]
            referral = CustomAsyncWeb3.to_checksum_address('0x0000000000000000000000000000000000000000')
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
                return await self.client.send_transaction(transaction, need_hash=True)
            except Exception as error:
                if '0x3a81d6fc' in str(error):
                    self.logger.warning(f"Domain {domain_names} already registered, skipping...")
                    continue
                else:
                    self.logger.error(  
                        f'{self.client.name} Buy ZNC domen. Error: {error} '
                    )
                    return False