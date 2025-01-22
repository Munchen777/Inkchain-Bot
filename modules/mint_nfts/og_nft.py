import asyncio

from web3 import AsyncWeb3
from web3.contract import AsyncContract
from web3.contract.async_contract import AsyncContract
from web3.eth.async_eth import ChecksumAddress
from curl_cffi.requests import AsyncSession

from modules import *
from utils.client import Client
from data.abi import OG_MINT_NFT
from modules.interfaces import *


class MintNFTOGWorker(Logger):
    def __init__(self, client: Client, module_info: MintNFTOGModule):
        super().__init__()
        self.client: Client = client

    async def get_price(self):
        headers = {
            'accept': '*/*',
            'content-type': 'application/json',
            'referer': 'https://zora.co/collect/oeth:0x5d1e1a5cdd95f68ff18d78242c252f6ceaa4538b/2',
            'user-agent': self.client.get_user_agent(),
        }

        params = {
            'input': '{"json":{"type":"buy","quantity":1,"poolAddress":"0x227f432a82fa6a04826ed6fe9f95f4e0acf091aa","chainId":10}}',
        }

        i = 0
        while i < 3:
            try:
                async with AsyncSession() as session:
                    response = await session.get(
                        'https://zora.co/api/trpc/uniswap.getQuote',
                        headers=headers,
                        params=params,
                        proxy=self.client.proxy_init,
                    )

                    if response.status_code == 200:
                        data = response.json()

                        wei_value = data["result"]["data"]["json"]["price"]["perToken"]["wei"]
                        usd_value = data["result"]["data"]["json"]["price"]["perToken"]["usd"]
                        break

                    else:
                        self.logger.error(f"{self.client.name} Failed request: {response.status_code}")
                        await asyncio.sleep(5)
                        wei_value, usd_value = None, None
                        i += 1

            except Exception as error:
                self.logger.error(f'{self.client.name} Failed request:  {error}')
                await asyncio.sleep(5)
                wei_value, usd_value = None, None
                i += 1
        
        return wei_value, usd_value

    async def run(self):
        wei_value, usd_value = await self.get_price()

        self.logger.info(
            f'{self.client.name} mint nft OG on the Ink network. Price: {usd_value} USD'
        )

        address_contract: ChecksumAddress = AsyncWeb3.to_checksum_address(
            "0x777777EDF27Ac61671e3D5718b10bf6a8802f9f1"
        )

        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract,
            abi=OG_MINT_NFT
        )

        erc_20z_address: ChecksumAddress = AsyncWeb3.to_checksum_address(
            "0xEF660b4A13Da8daF66d69602b2270e6633007927"
        )

        max_eth_to_spend = int(wei_value) + int(int(wei_value) * 0.01)

        try:
            tx_params = await self.client.prepare_transaction(value=max_eth_to_spend)
            transaction = await contract.functions.buy1155(
                erc_20z_address,
                1,
                self.client.address,
                self.client.address,
                max_eth_to_spend,
                0
            ).build_transaction(tx_params)
            await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the mint nft OG on the Ink network. Error: {error} '
            )