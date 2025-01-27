from web3.contract import AsyncContract
from web3.contract.async_contract import AsyncContract
from web3.eth.async_eth import ChecksumAddress

from modules import *
from utils.client import Client, CustomAsyncWeb3
from data.abi import PARAGRAF_MINT_NFT
from modules.interfaces import *


class MintNFTParagrafWorker(Logger):
    def __init__(self, client: Client, module_info: MintNFTParagrafModule):
        super().__init__()
        self.client: Client = client

    async def run(self):
        address_contract: ChecksumAddress = CustomAsyncWeb3.to_checksum_address(
            "0x69086dDd87cb58709540f784c32740a6f9a49CFF"
        )

        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract,
            abi=PARAGRAF_MINT_NFT
        )

        balance = await contract.functions.balanceOf(self.client.address).call()

        if balance > 0:
            self.logger.info(
                f'{self.client.name} The address already has nft Paragraf on the Ink network'
            )
            return True

        self.logger.info(
            f'{self.client.name} mint nft Paragraf on the Ink network'
        )
        
        address_mint_referrer: ChecksumAddress = CustomAsyncWeb3.to_checksum_address(
            "0x0000000000000000000000000000000000000000"
        )

        try:
            tx_params = await self.client.prepare_transaction(value=777000000000000)
            transaction = await contract.functions.mintWithReferrer(
                self.client.address,
                address_mint_referrer
            ).build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the mint nft Paragraf on the Ink network. Error: {error} '
            )
            return False