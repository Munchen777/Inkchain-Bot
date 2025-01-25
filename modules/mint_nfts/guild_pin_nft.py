import time
import asyncio

from web3.contract import AsyncContract
from web3.contract.async_contract import AsyncContract
from web3.eth.async_eth import ChecksumAddress
from curl_cffi.requests import AsyncSession
from eth_account.messages import encode_defunct

from modules import *
from utils.client import Client, CustomAsyncWeb3
from data.abi import GUILD_MINT_NFT
from modules.interfaces import *


class MintNFTGuildWorker(Logger):
    def __init__(self, client: Client, module_info: MintNFTGuildModule):
        super().__init__()
        self.client: Client = client
        self.contract_address = CustomAsyncWeb3.to_checksum_address(
            "0x73d1a63bce3083be47597E2Ef0646BbFd1907f1C"
        )

    async def get_user_id(self):
        headers = {
            'accept': '*/*',
            'origin': 'https://guild.xyz',
            'referer': 'https://guild.xyz/inkonchain',
            'user-agent': self.client.get_user_agent(),
        }

        i = 0
        while i < 3:
            try:
                async with AsyncSession() as session:
                    response = await session.get(
                        f'https://api.guild.xyz/v2/users/{self.client.address}/profile',
                        headers=headers,
                        proxy=self.client.proxy_init,
                    )

                    if response.status_code == 200:
                        data = response.json()

                        user_id = data["id"]
                        break

                    else:
                        self.logger.error(f"{self.client.name} Failed request: {response.status_code}")
                        await asyncio.sleep(5)
                        user_id = None
                        i += 1

            except Exception as error:
                self.logger.error(f'{self.client.name} Failed request:  {error}')
                await asyncio.sleep(5)
                user_id = None
                i += 1
        
        return user_id


    async def run(self):
        self.logger.info(
            f'{self.client.name} mint nft Guild on the Ink network'
        )

        address_contract: ChecksumAddress = CustomAsyncWeb3.to_checksum_address(
            "0x73d1a63bce3083be47597E2Ef0646BbFd1907f1C"
        )

        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract,
            abi=GUILD_MINT_NFT
        )

        user_id = await self.get_user_id()
        timestamp = int(time.time())
        pin_data = [
            self.client.address,
            0,
            user_id,
            76109,
            "Ink",
            timestamp
        ]

        admin_treasury: ChecksumAddress = CustomAsyncWeb3.to_checksum_address(
            "0x0000000000000000000000000000000000000000"
        )
        cid = "QmPHCzk4KAoSsR53WyaeXw3MWYBkQLbGCS51A1Z1y5KU4X"

        message_hash = CustomAsyncWeb3.solidity_keccak(
            [
                "address", "uint8", "uint256", "uint256", "string", "uint256",
                "address", "uint256", "uint256", "string", "uint256", "address"
            ],
            [
                pin_data[0], pin_data[1], pin_data[2], pin_data[3], pin_data[4], pin_data[5],
                admin_treasury, 0, timestamp, cid,
                await self.client.w3.eth.chain_id, address_contract
            ]
        )
        
        message = encode_defunct(message_hash)

        # Подпись сообщения
        signed_message = self.client.w3.eth.account.sign_message(
            message,
            private_key=self.client.private_key
        )

        signature = signed_message.signature

        try:
            tx_params = await self.client.prepare_transaction(value=400000000000000)
            transaction = await contract.functions.claim(
                pin_data,
                admin_treasury,
                0,
                int(time.time()),
                cid,
                signature
            ).build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            if str(error) == "('0x646cf558', '0x646cf558')":
                self.logger.info(
                    f'{self.client.name} The NFT has already claimed before'
                )
            else:
                self.logger.error(
                    f'{self.client.name} Failed the mint nft Guild on the Ink network. Error: {error}'
                )