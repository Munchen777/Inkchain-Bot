import random

from web3.contract import AsyncContract
from web3.contract.async_contract import AsyncContract
from web3.eth.async_eth import ChecksumAddress

from modules import *
from utils.client import Client, CustomAsyncWeb3
from data.abi import DINERO_ABI
from modules.interfaces import *


logger: Logger = Logger().get_logger()


async def canculate_amount_token_desired(
        client: Client, min_available_balance_out_token: float, min_clearance: float
    ):
    balance = await client.get_token_balance(token_name="ETH", check_native=True)

    value = 0 if balance is None else balance / 10 ** 18

    if value < min_available_balance_out_token or value - min_available_balance_out_token < min_clearance:
        logger.warning(
            f'{client.name} Skip the add liquidity ETH on the Ethereum network and ETH on the Ink network, '
            'because you have a minimum number of ETH on the Ethereum network tokens '
            f'Needed: {min_available_balance_out_token} you have: {value}'
        )
        return None
        
    free_amount = value - min_available_balance_out_token

    if free_amount < min_clearance:
        percent = 100
    else:
        percent = random.randint(50, 100)

    amount_out = round(free_amount * (1 - percent / 100), random.randint(2, 4))

    if amount_out < min_clearance:
        amount_out = (random.randint(int(min_clearance * 10 ** 18), int(free_amount * 10 ** 18)) / 10 ** 18)

    return amount_out


class AddLiquidityDineroETHandiETHWorker(Logger):
    def __init__(self, client: Client, module_info: AddLiquidityDineroETHandiETHModule):
        super().__init__()

        self.client: Client = client
        self.module_info: AddLiquidityDineroETHandiETHModule = module_info

    async def run(self):
        amount_out = await canculate_amount_token_desired(
            client=self.client, 
            min_available_balance_out_token=self.module_info.min_available_balance,
            min_clearance=self.module_info.min_amount_out
        )

        if amount_out is None: return False

        self.logger.info(
            f'{self.client.name} Add Liquidity {amount_out} ETH on the Ethereum network and {amount_out} ETH on the Ink network'
        )

        address_contract: ChecksumAddress = CustomAsyncWeb3.to_checksum_address(
            "0xf2b2bbdc9975cf680324de62a30a31bc3ab8a4d5"
        )

        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract,
            abi=DINERO_ABI
        )

        amount_out = amount_out / 10 ** 18
        value = amount_out + (self.module_info.fee / 10 ** 18)

        try:
            tx_params = await self.client.prepare_transaction(value=value)
            transaction = await contract.functions.depositEth(
                self.client.address,
                self.client.address,
                amount_out,
                False,
                b'0003010001040100110100000000000000000000000000055730'
            ).build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the Add Liquidity {amount_out} ETH on the Ethereum network and {amount_out} ETH on the Ink network. Error: {error} '
            )
            return False