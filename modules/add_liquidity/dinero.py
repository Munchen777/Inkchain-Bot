import random

from web3.contract import AsyncContract
from web3.contract.async_contract import AsyncContract
from web3.eth.async_eth import ChecksumAddress

from modules import *
from utils.client import Client, CustomAsyncWeb3
from data.abi import DINERO_INK_ABI
from modules.interfaces import *


logger: Logger = Logger().get_logger()


async def canculate_amount_token_desired(
        client: Client, min_available_balance_out_token: float, min_clearance: float
    ):
    balance = await client.get_token_balance(token_name="ETH", check_native=True)

    value = 0 if balance is None else balance / 10 ** 18

    if value < min_available_balance_out_token or value - min_available_balance_out_token < min_clearance:
        logger.warning(
            f'{client.name} Skip the add liquidity iETH on the Ink network and ETH on the Ethereum network, '
            'because you have a minimum number of iETH on the Ink network tokens '
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


class AddLiquidityDineroiETHandETHWorker(Logger):
    def __init__(self, client: Client, module_info: AddLiquidityDineroiETHandETHModule):
        super().__init__()

        self.client: Client = client
        self.module_info: AddLiquidityDineroiETHandETHModule = module_info

    async def run(self):
        amount_out = await canculate_amount_token_desired(
            client=self.client, 
            min_available_balance_out_token=self.module_info.min_available_balance,
            min_clearance=self.module_info.min_amount_out
        )

        if amount_out is None: return False

        self.logger.info(
            f'{self.client.name} Add Liquidity {amount_out} iETH on the Ink network and {amount_out} ETH on the Ethereum network'
        )

        address_contract: ChecksumAddress = CustomAsyncWeb3.to_checksum_address(
            "0xcab283e4bb527Aa9b157Bae7180FeF19E2aaa71a"
        )

        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract,
            abi=DINERO_INK_ABI
        )

        value = int(0.00005 * 10 ** 18)

        token_in: ChecksumAddress = CustomAsyncWeb3.to_checksum_address(
            "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
        )

        try:
            tx_params = await self.client.prepare_transaction(value=value, eip1559=False)
            transaction = await contract.functions.deposit(
                token_in,
                value,
                value
            ).build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the Add Liquidity {amount_out} iETH on the Ink network and {amount_out} ETH on the Ethereum network. Error: {error} '
            )
            return False