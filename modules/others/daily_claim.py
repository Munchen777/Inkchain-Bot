from web3.contract import AsyncContract
from web3.contract.async_contract import AsyncContract
from web3.eth.async_eth import ChecksumAddress
from curl_cffi.requests import AsyncSession
from datetime import datetime, timedelta

from modules import *
from utils.client import Client, CustomAsyncWeb3
from data.abi import DAILY_GM
from modules.interfaces import *


class ClaimDailyGMWorker(Logger):
    def __init__(self, client: Client, module_info: ClaimDailyGMModule):
        super().__init__()
        self.client: Client = client
        self.module_info: ClaimDailyGMModule = module_info

    async def get_last_claim(self):
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

                    last_tx_timestamp = None
                    for tx in transactions['items']:
                        if all([
                            tx.get('to', {}).get('name') == 'DailyGM', 
                            tx.get('status') == 'ok', 
                            'contract_call' in tx.get('transaction_types', [])
                        ]):
                            last_tx_timestamp = tx.get('timestamp')

                        if last_tx_timestamp:
                            tx_time = datetime.strptime(last_tx_timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
                            current_time = datetime.utcnow()
                            time_diff = current_time - tx_time
                            remaining_time = timedelta(hours=24) - time_diff
                            if time_diff < timedelta(hours=24): return True, remaining_time
                            else: return False
                    
                    return False
                
                else:
                    self.logger.error(f"{self.client.name} Request failed with status code: {response.status_code}")
                    return False

        except Exception as error:
            self.logger.error(f'{self.client.name} Failed request:  {error}')
            return False

    async def run(self):
        availability_contract, remaining_time = await self.get_last_claim()
        if availability_contract:
            self.logger.info(
                f"{self.client.name} You won't be able to fulfill your GM claim until {remaining_time}"
            )
            return True
        
        address_contract: ChecksumAddress = CustomAsyncWeb3.to_checksum_address(
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
            return False
